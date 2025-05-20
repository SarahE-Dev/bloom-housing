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
        
        # Log NaN values before coercion
        nan_counts = df.isna().sum()
        if nan_counts.sum() > 0:
            logger.warning(f"NaN values found before coercion: {nan_counts[nan_counts > 0].to_dict()}")
        
        # Convert columns to int, removing quotes
        for col in df.columns:
            if col != "CONTROL":
                df[col] = pd.to_numeric(df[col].astype(str).str.replace("'", ""), errors='coerce').fillna(0).astype(int)
        
        # Filter rows where HINCP >= 0
        rows_before = len(df)
        df = df[df["HINCP"] >= 0]
        logger.info(f"Rows after cleaning HINCP: {len(df)} (dropped {rows_before - len(df)} rows)")
        
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
            (df["PERPOVLVL"] <= 124) |  # Poverty level <= 124% per CA
            (df["HIHALF"] == 1) |       # High housing cost burden
            (df["HIMORTFORC"] == 1) |   # Mortgage foreclosure
            (df["HIEVICNOTE"] == 1) |   # Eviction notice
            (df["HIBEHINDFRQ"].isin([2, 3, 4])) |  # Frequent missed payments
            (df["HINFORC"] == 1)        # Other foreclosure issues
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
        
        # Log NaN values before coercion
        nan_counts = df.isna().sum()
        if nan_counts.sum() > 0:
            logger.warning(f"NaN values in person data: {nan_counts[nan_counts > 0].to_dict()}")
        
        # Convert MIL to numeric
        df["MIL"] = pd.to_numeric(df["MIL"].astype(str).str.replace("'", ""), errors='coerce').fillna(0).astype(int)
        
        # Validate AGE
        rows_before = len(df)
        df = df[df["AGE"] >= 0]
        logger.info(f"Rows after cleaning AGE: {len(df)} (dropped {rows_before - len(df)} rows)")
        
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
        # Log unmatched records
        unmatched_persons = person_df[~person_df["CONTROL"].isin(household_df["CONTROL"])]
        unmatched_households = household_df[~household_df["CONTROL"].isin(person_df["CONTROL"])]
        if not unmatched_persons.empty:
            logger.warning(f"{len(unmatched_persons)} person records unmatched")
        if not unmatched_households.empty:
            logger.warning(f"{len(unmatched_households)} household records unmatched")
        
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
            (df["RENTSUB"].isin([1, 2, 3, 4, 5])) |  # Rental subsidies
            (df["FS"] == 1) |                       # Food stamps/SNAP
            (df["PAP"] > 0) |                       # Public assistance income
            (df["HUDSUB"] == 1)                     # HUD subsidies
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
        # Drop rows with -9
        rows_before = len(df)
        df = df[~df.isin([-9]).any(axis=1)]
        logger.info(f"Dropped {rows_before - len(df)} rows with -9 values")
        
        # Drop MIL and CONTROL columns
        df = df.drop(columns=["MIL", "CONTROL"])
        
        # Convert MILHH and DISHH to binary
        # Note: MILHH=1 for values 1-5 (veteran or active military household); verify data dictionary
        df["MILHH"] = df["MILHH"].isin([1, 2, 3, 4, 5]).astype(int)
        df["DISHH"] = (df["DISHH"] == 1).astype(int)
        
        # Ensure final feature order
        final_columns = ["HINCP", "AGE", "NUMPEOPLE", "DISHH", "MILHH", "gov_assistance", "at_risk"]
        df = df[final_columns]
        
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
        
        print("\nContinuous feature statistics:\n")
        print(df[["HINCP", "AGE", "NUMPEOPLE"]].describe())
        
        print("\nValue counts for columns with less than 10 unique values:\n")
        cols = ["MILHH", "NUMPEOPLE", "DISHH", "gov_assistance", "at_risk"]
        for col in cols:
            print(f"\n{col}:\n")
            print(df[col].value_counts())
        
        print("\nHINCP distribution by at_risk:\n")
        print(df.groupby("at_risk")["HINCP"].describe())
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