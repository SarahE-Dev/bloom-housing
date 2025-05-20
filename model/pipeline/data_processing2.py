import pandas as pd
from pathlib import Path
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the directory of the current script
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / ".." / "data"

def load_household_data() -> pd.DataFrame:
    """Load and clean household data from CSV."""
    input_path = DATA_DIR / "household.csv"
    try:
        cols = [
            "CONTROL", "HINCP", "DISHH", "FS", "HUDSUB", "RENTSUB", "RENTCNTRL",
            "NUMPEOPLE", "PERPOVLVL", "HIHALF", "HIBEHINDFRQ", "HIMORTFORC",
            "HIEVICNOTE", "HINFORC", "MILHH"
        ]
        df = pd.read_csv(input_path, usecols=cols)
        logger.info(f"Loaded {len(df)} households from {input_path}")
        
        # Convert columns to int, removing quotes
        for col in df.columns:
            if col != "CONTROL":
                df[col] = pd.to_numeric(df[col].astype(str).str.replace("'", ""), errors='coerce').fillna(0).astype(int)
        
        # Filter rows where HINCP >= 0
        df = df[df["HINCP"] >= 0]
        logger.info(f"Rows after cleaning HINCP: {len(df)}")
        
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {input_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading household data: {str(e)}")
        raise

def create_at_risk_column(df: pd.DataFrame) -> pd.DataFrame:
    """Create 'at_risk' column based on specified conditions."""
    try:
        df["at_risk"] = (
            (df["PERPOVLVL"] <= 100) |
            (df["HIHALF"] == 1) |
            (df["HIMORTFORC"] == 1) |
            (df["HIEVICNOTE"] == 1) |
            (df["HIBEHINDFRQ"].isin([2, 3, 4])) |
            (df["HINFORC"] == 1)
        ).astype(int)
        
        # Drop columns used for at_risk calculation
        df = df.drop(columns=[
            "PERPOVLVL", "HIHALF", "HIBEHINDFRQ", 
            "HIEVICNOTE", "HIMORTFORC", "HINFORC"
        ])
        logger.info("Created at_risk column and dropped temporary columns")
        return df
    except Exception as e:
        logger.error(f"Error creating at_risk column: {str(e)}")
        raise

def load_person_data() -> pd.DataFrame:
    """Load and clean person data from CSV."""
    input_path = DATA_DIR / "person.csv"
    try:
        df = pd.read_csv(input_path, usecols=["CONTROL", "AGE", "PAP", "MIL"])
        df["MIL"] = pd.to_numeric(df["MIL"].astype(str).str.replace("'", ""), errors='coerce').fillna(0).astype(int)
        logger.info(f"Loaded and cleaned person data from {input_path}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {input_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading person data: {str(e)}")
        raise

def merge_datasets(household_df: pd.DataFrame, person_df: pd.DataFrame) -> pd.DataFrame:
    """Merge household and person datasets."""
    try:
        merged_df = pd.merge(
            person_df, household_df, 
            on="CONTROL", 
            how="inner", 
            validate="many_to_one"
        )
        logger.info(f"Merged datasets, resulting in {len(merged_df)} rows")
        return merged_df
    except Exception as e:
        logger.error(f"Error merging datasets: {str(e)}")
        raise

def create_gov_assistance_column(df: pd.DataFrame) -> pd.DataFrame:
    """Create government assistance column and clean up related columns."""
    try:
        df["gov_assistance"] = (
            (df["RENTSUB"].isin([1, 2, 3, 4, 5])) |
            (df["FS"] == 1) |
            (df["PAP"] > 0) |
            (df["HUDSUB"] == 1) |
            (df["RENTCNTRL"] == 1)
        ).astype(int)
        
        # Drop columns used for gov_assistance
        df = df.drop(columns=["FS", "PAP", "HUDSUB", "RENTSUB", "RENTCNTRL"])
        logger.info("Created gov_assistance column and dropped temporary columns")
        return df
    except Exception as e:
        logger.error(f"Error creating gov_assistance column: {str(e)}")
        raise

def finalize_data(df: pd.DataFrame) -> pd.DataFrame:
    """Finalize dataset with final cleaning and transformations."""
    try:
        # Drop rows with -9 in any column
        df = df[~df.isin([-9]).any(axis=1)]
        
        # Drop MIL and CONTROL columns
        df = df.drop(columns=["MIL", "CONTROL"])
        
        # Convert MILHH and DISHH to binary
        df["MILHH"] = df["MILHH"].isin([1, 2, 3, 4, 5]).astype(int)
        df["DISHH"] = (df["DISHH"] == 1).astype(int)
        
        logger.info(f"Final dataset shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error finalizing data: {str(e)}")
        raise

def save_dataframe(df: pd.DataFrame, filename: str) -> None:
    """Save DataFrame to CSV."""
    output_path = DATA_DIR / filename
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Saved DataFrame to {output_path}")
    except Exception as e:
        logger.error(f"Error saving DataFrame to {output_path}: {str(e)}")
        raise

def print_data_summary(df: pd.DataFrame) -> None:
    """Print summary statistics of the dataset."""
    try:
        print("Null values in dataset:\n")
        print(df.isna().sum())
        print("\nData types in dataset:\n")
        print(df.dtypes)
        print("\nNumber of unique values in each column:\n")
        print(df.nunique())
        
        print("\nValue counts for columns with less than 10 unique values:\n")
        cols = ["MILHH", "NUMPEOPLE", "DISHH", "gov_assistance", "at_risk"]
        for col in cols:
            print(f"\n{col}:\n")
            print(df[col].value_counts())
    except Exception as e:
        logger.error(f"Error printing data summary: {str(e)}")
        raise

def main():
    """Main function to orchestrate data processing."""
    try:
        # Process household data
        household_df = load_household_data()
        household_df = create_at_risk_column(household_df)
        save_dataframe(household_df, "household_cleaned-v2.csv")

        # Process person data
        person_df = load_person_data()
        save_dataframe(person_df, "person_cleaned-v2.csv")

        # Merge datasets
        main_df = merge_datasets(household_df, person_df)

        # Create government assistance column
        main_df = create_gov_assistance_column(main_df)

        # Finalize data
        main_df = finalize_data(main_df)

        # Save final dataset
        save_dataframe(main_df, "final_df-v2.csv")

        # Print summary
        print_data_summary(main_df)

    except Exception as e:
        logger.error(f"Error in main pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main()