import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost/energy")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

def load_csv_to_db(csv_path, table_name, dtype=None, parse_dates=None, column_map=None, clean_func=None):
    """
    Load CSV file into database table

    Args:
        csv_path: Path to CSV file
        table_name: Target database table
        dtype: Data types for columns
        parse_dates: List of date columns
        column_map: Dictionary to rename columns from CSV to DB format
        clean_func: Function to clean/transform dataframe before loading
    """
    print(f"Loading data from {csv_path} into {table_name}...")

    # Read CSV file
    df = pd.read_csv(csv_path, dtype=dtype, parse_dates=parse_dates)

    # Rename columns if needed
    if column_map:
        df = df.rename(columns=column_map)

    # Apply custom cleaning function if provided
    if clean_func:
        df = clean_func(df)

    # Print first few rows for verification
    print(f"Sample data ({len(df)} rows total):")
    print(df.head(3))

    # Upload to database
    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"Successfully loaded {len(df)} rows into {table_name}")


def clean_tariffs(df):
    """Clean tariffs dataframe to ensure no NULL values in primary key columns"""
    # Fill missing cdi values with 0
    df['cdi'] = df['cdi'].fillna(0).astype(int)
    return df


def main():
    # Set CSV file paths - using current directory
    services_csv = 'services.csv'
    tariffs_csv = 'tariffs.csv'
    records_csv = 'records.csv'
    consumption_csv = 'consumption.csv'
    injection_csv = 'injection.csv'
    xm_data_csv = 'xm_data_hourly_per_agent.csv'

    # Define data types and date columns for each table
    services_dtypes = {
        'id_service': int,
        'id_market': int,
        'cdi': int,  # This will be renamed to cir
        'voltage_level': int
    }

    tariffs_dtypes = {
        'id_market': int,
        'voltage_level': int,
        # Don't specify dtype for cdi since we'll clean it
        'G': float,
        'T': float,
        'D': float,
        'R': float,
        'C': float,
        'P': float,
        'CU': float
    }

    records_dtypes = {
        'id_record': int,
        'id_service': int
    }

    consumption_dtypes = {
        'id_record': int,
        'value': float
    }

    injection_dtypes = {
        'id_record': int,
        'value': float
    }

    # Column mapping for services table - map 'cdi' to 'cir'
    services_column_map = {
        'cdi': 'cdi'
    }

    try:
        # Clear existing data first (optional)
        print("Clearing existing data...")
        conn = engine.connect()
        #conn.execute("TRUNCATE services, tariffs, records, consumption, injection, xm_data_hourly_per_agent CASCADE")
        conn.close()
        print("Tables cleared.")

        # Load data into tables
        load_csv_to_db(services_csv, 'services', dtype=services_dtypes, column_map=services_column_map)
        load_csv_to_db(tariffs_csv, 'tariffs', dtype=tariffs_dtypes, clean_func=clean_tariffs)
        load_csv_to_db(records_csv, 'records', dtype=records_dtypes, parse_dates=['record_timestamp'])
        load_csv_to_db(consumption_csv, 'consumption', dtype=consumption_dtypes)
        load_csv_to_db(injection_csv, 'injection', dtype=injection_dtypes)
        load_csv_to_db(xm_data_csv, 'xm_data_hourly_per_agent', parse_dates=['record_timestamp'])

        print("All data loaded successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")
        print("Data loading failed. Please check your database structure and CSV files.")


if __name__ == "__main__":
    main()