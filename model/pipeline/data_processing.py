import pandas as pd
import numpy as np
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_and_clean_household_data(csv_file="household.csv", data_dir="data"):
    """
    Load and clean household data from a CSV file with specified columns.
    
    Parameters:
    -----------
    csv_file : str
        Name of the CSV file (default: 'household.csv')
    data_dir : str
        Directory containing the CSV file (default: 'data')
        
    Returns:
    --------
    pandas.DataFrame : Loaded and cleaned household data with 'at_risk' column
    """
    try:
        # Construct relative path to CSV (data directory is at same level as pipeline)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "..", data_dir, csv_file)
        csv_path = os.path.normpath(data_path)  # Normalize path to handle '..' correctly
        
        # Validate file existence
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at: {csv_path}")
        
        logger.info(f"Loading household data from {csv_path}")
        
        # Load data with specified columns
        columns = ["CONTROL", "HINCP", "DISHH", "FS", "HHADLTKIDS", 
                  "PERPOVLVL", "HIHALF", "HIBEHINDFRQ", "HIMORTFORC", 
                  "HIEVICNOTE", "MILHH"]
        
        df = pd.read_csv(
            csv_path,
            usecols=columns
        )
        
        logger.info(f"Loaded {len(df)} households")
        
        # Data Cleaning
        # Remove single quotes and convert to int, except CONTROL column
        for col in df.columns:
            if col != "CONTROL":
                df[col] = df[col].astype(str).str.replace("'", "").astype(int)
        
        # Drop rows where HINCP is below 0
        initial_rows = len(df)
        df = df[df['HINCP'] >= 0]
        if len(df) < initial_rows:
            logger.info(f"Dropped {initial_rows - len(df)} rows where HINCP < 0")
        
        # Create 'at_risk' column based on conditions
        df['at_risk'] = (
            (df['PERPOVLVL'] <= 100) |
            (df['HIHALF'] == 1) |
            (df['HIMORTFORC'] == 1) |
            (df['HIEVICNOTE'] == 1) |
            (df['HIBEHINDFRQ'].isin([2, 3, 4]))
        ).astype(int)
        
        # Drop columns used to make 'at_risk' column
        df = df.drop(columns=['PERPOVLVL', 'HIHALF', 'HIBEHINDFRQ', 'HIEVICNOTE', 'HIMORTFORC'])
        
        return df
    
    except FileNotFoundError as e:
        logger.error(f"File error: {str(e)}")
        raise
    except pd.errors.EmptyDataError:
        logger.error("Household CSV file is empty")
        raise
    except KeyError as e:
        logger.error(f"Column not found in household CSV: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"Data conversion error in household data: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in household data: {str(e)}")
        raise

def load_and_clean_person_data(csv_file="person.csv", data_dir="data"):
    """
    Load and clean person data from a CSV file with specified columns.
    
    Parameters:
    -----------
    csv_file : str
        Name of the CSV file (default: 'person.csv')
    data_dir : str
        Directory containing the CSV file (default: 'data')
        
    Returns:
    --------
    pandas.DataFrame : Loaded and cleaned person data
    """
    try:
        # Construct relative path to CSV (data directory is at same level as pipeline)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "..", data_dir, csv_file)
        csv_path = os.path.normpath(data_path)  # Normalize path to handle '..' correctly
        
        # Validate file existence
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at: {csv_path}")
        
        logger.info(f"Loading person data from {csv_path}")
        
        # Load data with specified columns
        df = pd.read_csv(
            csv_path,
            usecols=['CONTROL', 'AGE', 'PAP', 'MIL']
        )
        
        # Clean MIL column
        df['MIL'] = df['MIL'].astype(str).str.replace("'", "").astype(int)
        
        logger.info(f"Loaded {len(df)} person records")
        
        return df
    
    except FileNotFoundError as e:
        logger.error(f"File error: {str(e)}")
        raise
    except pd.errors.EmptyDataError:
        logger.error("Person CSV file is empty")
        raise
    except KeyError as e:
        logger.error(f"Column not found in person CSV: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"Data conversion error in person data: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in person data: {str(e)}")
        raise

def apply_encoding(df, mappings_dict):
    """
    Apply one-hot encoding to specified columns using provided mappings.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame to encode
    mappings_dict : dict
        Dictionary of column names to mapping dictionaries for encoding
        
    Returns:
    --------
    pandas.DataFrame : DataFrame with encoded columns
    """
    try:
        for column_name, mapping in mappings_dict.items():
            # Create a temporary Series with mapped values for encoding
            temp_series = df[column_name].map(mapping)
            
            # Check for unmapped values
            if temp_series.isna().any():
                unmapped_values = df[column_name][temp_series.isna()].unique()
                logger.warning(f"Unmapped values in {column_name}: {unmapped_values}")
                raise ValueError(f"Unmapped values in {column_name}: {unmapped_values}")
            
            # One-hot encode the mapped values
            encoded = pd.get_dummies(temp_series).astype(int)
            
            # Add encoded columns to the result
            df = pd.concat([df.drop(column_name, axis=1), encoded], axis=1)
        
        return df
    
    except KeyError as e:
        logger.error(f"Column not found during encoding: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error during encoding: {str(e)}")
        raise

def main():
    """
    Main function to orchestrate loading, cleaning, merging, updating, and encoding of household and person data.
    
    Returns:
    --------
    pandas.DataFrame : Final encoded DataFrame
    """
    try:
        # Load and clean household data
        household_df = load_and_clean_household_data()
        
        # Save cleaned household data
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(base_dir, "..", "data", "household_cleaned.csv")
        output_path = os.path.normpath(output_path)  # Normalize path
        household_df.to_csv(output_path, index=False)
        logger.info(f"Saved cleaned household data to {output_path}")
        
        # Display household data
        print(household_df.head(20))
        print(f"\n\n{len(household_df)} Households loaded")
        print(f'Rows after cleaning: {len(household_df)}')
        
        # Load and clean person data
        person_df = load_and_clean_person_data()
        
        # Display person data
        print("\nPerson Data Preview:")
        print(person_df.head(20))
        print(f"\n{len(person_df)} Person records loaded")
        
        # Merge household and person data
        logger.info("Merging household and person data")
        main_df = pd.merge(
            person_df,
            household_df,
            on='CONTROL',
            how='inner',
            validate='many_to_one'
        )
        
        # Display merged data
        print("\nMerged Data Preview:")
        print(main_df.head(20))
        print(f"\n{len(main_df)} Records in merged dataset")
        logger.info(f"Merged dataset contains {len(main_df)} records")
        
        # Update 'at_risk' column for MIL == 2
        logger.info("Updating at_risk column for MIL == 2")
        mask = main_df['MIL'] == 2
        population_size = mask.sum()
        probability_of_atrisk = 0.4  # 40% chance of 1
        
        if population_size > 0:
            # Generate random binary values
            binary_values = np.random.choice(
                [0, 1],
                size=population_size,
                p=[1 - probability_of_atrisk, probability_of_atrisk]
            )
            
            # Validate the proportion
            print(f"Proportion of 1s in binary values: {np.mean(binary_values)}")
            
            # Update the 'at_risk' column
            main_df.loc[mask, 'at_risk'] = binary_values
            
            # Display updated values
            print('\n\n')
            print("Updated MIL at risk values:\n")
            print(main_df[mask][['MIL', 'at_risk']].value_counts())
        else:
            logger.info("No records with MIL == 2 found for at_risk update")
        
        # Check class ratio of at_risk column
        print("\nAt-risk class distribution (expecting ~4:1 ratio of 0s to 1s):")
        print(main_df['at_risk'].value_counts())
        logger.info(f"At-risk class distribution:\n{main_df['at_risk'].value_counts().to_dict()}")
        
        # Create gov_assistance column
        logger.info("Creating gov_assistance column")
        main_df['gov_assistance'] = ((main_df['FS'] == 1) | (main_df['PAP'] > 0)).astype(int)
        
        # Drop FS and PAP columns
        main_df = main_df.drop(columns=['FS', 'PAP'])
        
        # Drop rows with -9 in any column
        initial_rows = len(main_df)
        main_df = main_df[~main_df.isin([-9]).any(axis=1)]
        if len(main_df) < initial_rows:
            logger.info(f"Dropped {initial_rows - len(main_df)} rows containing -9")
        
        # Drop MIL and CONTROL columns
        main_df = main_df.drop(columns=['MIL', 'CONTROL'])
        
        # Save merged data
        output_path = os.path.join(base_dir, "..", "data", "main_df.csv")
        output_path = os.path.normpath(output_path)
        main_df.to_csv(output_path, index=False)
        logger.info(f"Saved merged data to {output_path}")
        
        # Display unique values and value counts
        print("\nNumber of unique values in each column:\n")
        print(main_df.nunique())
        print('\n\n')
        
        print("Value counts for columns with less than 10 unique values:\n")
        print(main_df['MILHH'].value_counts())
        print('\n')
        print(main_df['HHADLTKIDS'].value_counts())
        print('\n')
        print(main_df['DISHH'].value_counts())
        print('\n')
        print(main_df['at_risk'].value_counts())
        print('\n')
        print(main_df['gov_assistance'].value_counts())
        
        # Define mappings for one-hot encoding
        dishh_mapping = {
            1: "disabled_person_in_household_yes",
            2: "disabled_person_in_household_no",
            -6: "disabled_person_in_household_no"
        }
        
        milhh_mapping = {
            1: "military_1person_active",
            2: "military_1person_veteran",
            3: "military_2plus_active_no_veterans",
            4: "military_2plus_veterans",
            5: "military_2plus_mix_active_veterans",
            6: "military_no_service",
            -6: "military_no_service"
        }
        
        gov_assistance_mapping = {
            0: "no_government_assistance",
            1: "government_assistance"
        }
        
        mappings = {
            'DISHH': dishh_mapping,
            'MILHH': milhh_mapping,
            'gov_assistance': gov_assistance_mapping
        }
        
        # Apply one-hot encoding
        logger.info("Applying one-hot encoding")
        final_df = apply_encoding(main_df, mappings)
        
        # Save final encoded data
        output_path = os.path.join(base_dir, "..", "data", "final_df.csv")
        output_path = os.path.normpath(output_path)
        final_df.to_csv(output_path, index=False)
        logger.info(f"Saved final encoded data to {output_path}")
        
        # Display final encoded data
        print("\nFinal Encoded Data Preview:")
        print(final_df.head(20))
        logger.info("Completed all data processing and encoding steps")
        
        return final_df
    
    except pd.errors.MergeError as e:
        logger.error(f"Merge error: {str(e)}")
        raise
    except KeyError as e:
        logger.error(f"Column not found during processing: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in main pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        final_df = main()
    except Exception as e:
        print(f"Pipeline failed: {str(e)}")