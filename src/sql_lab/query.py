#!/usr/bin/env python3

import os
import sys
import logging
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# Configure logging at the module level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Fetch database credentials from environment variables
host = os.getenv("DBHOST")
user = os.getenv("DBUSER")
password = os.getenv("DBPASS")
database = os.getenv("DBNAME")

if not all([host, user, password, database]):
    logging.error("Missing one or more required database environment variables.")
    sys.exit(1)

# Initialize database connection
db = mysql.connector.connect(
    user=user,
    host=host,
    password=password,
    database=database,
    port=3306
)
cur = db.cursor()


def get_data_by_group(value: str):
    """Return mock table rows whose group matches ``value`` (list of tuples).
    """
    logging.info("Querying records where `group` = '%s'...", value)
    query = "SELECT * FROM `mock` WHERE `group` = %s;"
    try:
        cur.execute(query, (value,))
        results = cur.fetchall()
        logging.info("Found %d records for group '%s'.", len(results), value)
        return results
    except mysql.connector.Error as e:
        logging.error("MySQL Error in get_data_by_group: %s", e)
        return None


def plot_counts(groupby: str = "group") -> pd.DataFrame:
    """Count records grouped by column, show a bar chart, and return DataFrame.
    """
    logging.info("Calculating category counts grouped by `%s`...", groupby)
    query = f"SELECT `{groupby}`, COUNT(`{groupby}`) AS count FROM `mock` GROUP BY `{groupby}`;"
    try:
        cur.execute(query)
        results = cur.fetchall()
        headers = [col[0] for col in cur.description]
        df = pd.DataFrame(results, columns=headers)

        if not df.empty:
            logging.info("Generating plot for %d groups...", len(df))
            df.plot.bar(x=groupby, y="count", legend=False)
            plt.title(f"Record Count by {groupby.capitalize()}")
            plt.xlabel(groupby.capitalize())
            plt.ylabel("Count")
            plt.tight_layout()
            plt.show()

        return df
    except mysql.connector.Error as e:
        logging.error("MySQL Error in plot_counts: %s", e)
        return None


def main():
    """Run demonstration queries against the mock database and print results."""
    print("=== Group Counts ===")
    counts_df = plot_counts(groupby="group")
    if counts_df is not None and not counts_df.empty:
        print(counts_df.to_string(index=False))

        # Select the first available group to demo parameter filtering
        first_group = counts_df.iloc[0]["group"]
        print(f"\n=== Records where group = '{first_group}' ===")
        sample_records = get_data_by_group(first_group)
        if sample_records:
            for row in sample_records[:5]: # Display preview of first 5
                print(row)

    # Clean up connection
    cur.close()
    db.close()
    logging.info("Database connection closed cleanly.")


if __name__ == "__main__":
    main()