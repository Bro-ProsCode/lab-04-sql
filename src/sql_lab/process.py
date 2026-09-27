import os
import pandas as pd
import sys
import logging
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.types import BigInteger, Integer, Float, Boolean, DateTime, String

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')  # Set up logging


def read_data(filename: str) -> pd.DataFrame:
    """Reads in the given file and converts to a pandas dataframe"""
    logging.info(f"Reading file {filename}")
    df = pd.read_csv(filename)
    logging.info("Loaded %d rows and %d columns from %s.", len(df), len(df.columns), filename)
    return df


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Cleans the given pandas dataframe by sanitizing white spaces, dropping null/NA values, and converting data types to pd types"""
    logging.info("Cleaning data: starting with %d rows.", len(data))

    cleaned_df = data.dropna().copy()
    dropped = len(data) - len(cleaned_df)
    logging.info("Dropped %d rows containing missing values (%d rows remain).", dropped, len(cleaned_df))

    cleaned_df.columns = [col.strip().lower().replace(" ", "_") for col in cleaned_df.columns]  # Replaces white space with underscore
    logging.info("Normalized column names: %s", list(cleaned_df.columns))

    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == "object":
            try:
                cleaned_df[col] = pd.to_datetime(cleaned_df[col])
                logging.info("Column '%s' converted to datetime.", col)
                continue
            except (ValueError, TypeError):
                logging.debug(f"Column '{col}' could not be converted to datetime. Keeping as object.")
                pass

        cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce").fillna(cleaned_df[col])

    logging.info("Cleaning complete: %d rows, %d columns.", len(cleaned_df), len(cleaned_df.columns))
    return cleaned_df


# SQLAlchemy DDL type mapping for to_sql dtype argument
SQL_TYPE_MAPPING = {
    "int64": BigInteger(),
    "int32": Integer(),
    "float64": Float(),
    "bool": Boolean(),
    "datetime64[ns]": DateTime(),
    "object": String(255),
    "string": String(255),
}


def load_data(data: pd.DataFrame, table: str = "mock") -> None:
    """Create the destination table and bulk load DataFrame rows using SQLAlchemy"""

    # Sets up the database variables
    host = os.getenv("DBHOST")
    user = os.getenv("DBUSER")
    password = os.getenv("DBPASS")
    database = os.getenv("DBNAME")

    if not all([host, user, password, database]):
        logging.error("Missing one or more required database environment variables.")
        sys.exit(1)

    # Encode credentials to handle special characters cleanly using quote_plus
    safe_user = quote_plus(user)
    safe_pass = quote_plus(password)

    connection_url = (
        f"mysql+mysqlconnector://{safe_user}:{safe_pass}@{host}:3306/{database}"
    )

    engine = None
    try:
        logging.info("Initializing SQLAlchemy engine for database: %s", database)
        engine = create_engine(connection_url, echo=False)

        # Map pandas dtypes to SQLAlchemy types for accurate schema creation
        dtype_dict = {
            col: SQL_TYPE_MAPPING.get(str(dtype), String(255))
            for col, dtype in data.dtypes.items()
        }

        logging.info("Writing %d rows to table '%s' using pandas .to_sql()...", len(data), table)

        # Replaces existing table if the same name is found
        with engine.begin() as connection:
            data.to_sql(
                name=table,
                con=connection,
                if_exists="replace",
                index=False,
                dtype=dtype_dict,
                chunksize=1000
            )

        logging.info("Successfully loaded records into '%s'.", table)

    except Exception as err:
        logging.error("SQLAlchemy bulk upload failed: %s", err)
        raise
    finally:
        if engine:
            engine.dispose()
            logging.info("SQLAlchemy engine disposed.")


def main():
    """Sequences the loading, cleaning, and uploading of mock data to the db"""
    filename = "MOCK_DATA.csv"  # load mock data from local directory
    data = read_data(filename)
    cleaned_data = clean_data(data)
    load_data(cleaned_data, table="mock")
    logging.info("Data processing completed.")


if __name__ == "__main__":  # Prevents the file from being run during imports
    main()