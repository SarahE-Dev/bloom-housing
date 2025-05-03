import pandas as pd
import numpy as np
import os
import logging

# Set up logging
target = logging.INFO
logging.basicConfig(level=target, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Poverty threshold for per-capita income, per National Poverty threshold.
PCPOV_THRESHOLD = 15650

def load_and_clean_person_data(csv_file="person.csv", data_dir="data"):
    """Load and clean person-level data."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.normpath(os.path.join(base_dir, "..", data_dir, csv_file))
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Person CSV not found at: {csv_path}")

    df = pd.read_csv(csv_path, usecols=['CONTROL', 'AGE', 'PAP'])
    df['PAP'] = df['PAP'].astype(str).str.replace("'", "").astype(int)
    df['CONTROL'] = df['CONTROL'].astype(str)
    logger.info(f"Loaded {len(df)} person records")
    return df

def load_and_clean_household_data(csv_file="household.csv", data_dir="data"):
    """Load and clean household-level data."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.normpath(os.path.join(base_dir, "..", data_dir, csv_file))
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Household CSV not found at: {csv_path}")

    columns = ['CONTROL', 'HINCP', 'DISHH', 'FS', 'MILHH']
    df = pd.read_csv(csv_path, usecols=columns)
    df['CONTROL'] = df['CONTROL'].astype(str)
    for col in ['HINCP', 'DISHH', 'FS', 'MILHH']:
        df[col] = df[col].astype(str).str.replace("'", "").astype(int)

    # Drop negative incomes
    initial = len(df)
    df = df[df['HINCP'] >= 0]
    dropped = initial - len(df)
    if dropped > 0:
        logger.info(f"Dropped {dropped} rows with negative income")

    logger.info(f"Loaded and cleaned {len(df)} household records")
    return df

def apply_encoding(df, mappings):
    """One-hot encode specified columns."""
    for col, mapping in mappings.items():
        series = df[col].map(mapping)
        if series.isna().any():
            unmapped = df.loc[series.isna(), col].unique()
            raise ValueError(f"Unmapped values in {col}: {unmapped}")
        encoded = pd.get_dummies(series).astype(int)
        df = pd.concat([df.drop(columns=[col]), encoded], axis=1)
    return df

def main():
    # 1. Load data
    person_df = load_and_clean_person_data()
    household_df = load_and_clean_household_data()

    # 2. Compute NUMPEOPLE (household size)
    size_df = (
        person_df.groupby('CONTROL')
                 .size()
                 .reset_index(name='NUMPEOPLE')
    )
    household_df = pd.merge(
        household_df, size_df,
        on='CONTROL', how='inner'
    )
    logger.info("Merged NUMPEOPLE; households now have size info")

    # 3. Compute per-capita income for target only
    household_df['income_pc'] = household_df['HINCP'] / household_df['NUMPEOPLE']

    # 4. Create 'veteran_in_household' column
    # Veteran in household: yes if MILHH is 2, 4, or 5
    household_df['veteran_in_household'] = household_df['MILHH'].isin([2, 4, 5]).astype(int)

    # Define household-level at-risk flag
    household_df['at_risk_household'] = (
        (household_df['income_pc'] <= PCPOV_THRESHOLD) |
        (household_df['DISHH'] == 1) |
        (household_df['veteran_in_household'] == 1)
    ).astype(int)

    # 5. Create income bins with fixed thresholds
    bins = [-float('inf'), 40000, 80000, float('inf')]
    labels = ['low', 'medium', 'high']
    household_df['income_bin'] = pd.cut(household_df['HINCP'], bins=bins, labels=labels, include_lowest=True)

    # 6. Save cleaned household
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_hh = os.path.normpath(os.path.join(base_dir, "..", "data", "household_cleaned.csv"))
    household_df.to_csv(out_hh, index=False)
    logger.info(f"Saved cleaned household data to {out_hh}")

    # 7. Merge to person-level
    main_df = pd.merge(
        person_df, household_df,
        on='CONTROL', how='inner', validate='many_to_one'
    )

    # 8. Create gov_assistance
    main_df['gov_assistance'] = ((main_df['FS'] == 1) | (main_df['PAP'] > 0)).astype(int)

    # 9. Feature engineering
    main_df['high_risk_age'] = ((main_df['AGE'].between(18, 24)) | (main_df['AGE'] >= 65)).astype(int)

    # 10. Drop intermediates
    drop_cols = ['FS', 'PAP', 'HINCP', 'income_pc', 'MILHH']
    main_df = main_df.drop(columns=drop_cols + ['CONTROL'])

    # 11. Remove sentinel -9
    before = len(main_df)
    main_df = main_df[~main_df.isin([-9]).any(axis=1)]
    after = len(main_df)
    if before != after:
        logger.info(f"Dropped {before - after} rows containing -9")

    # 12. One-hot encode
    mappings = {
        'DISHH': {1: 'disabled_yes', 2: 'disabled_no', -6: 'disabled_no'},
        'veteran_in_household': {0: 'no_veteran', 1: 'has_veteran'},
        'gov_assistance': {0: 'no_assistance_flag', 1: 'assistance'},
        'income_bin': {'low': 'income_low', 'medium': 'income_medium', 'high': 'income_high'}
    }
    final_df = apply_encoding(main_df, mappings)

    # 13. Save final data
    out_final = os.path.normpath(os.path.join(base_dir, "..", "data", "final_df.csv"))
    final_df.to_csv(out_final, index=False)
    logger.info(f"Saved final encoded data to {out_final}")

    print(final_df.head())
    return final_df

if __name__ == '__main__':
    main()
