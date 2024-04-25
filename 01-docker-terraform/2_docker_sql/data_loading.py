"""Script to load data from a file link to a Postgres datebase.

Args:
    user (str): Username for Postgres.
    password (str): Password to the username for Postgres.
    host (str): Hostname for Postgres.
    port (str): Port for Postgres connection.
    db (str): Databse name for Postgres.
    tb (str): Destination table name for Postgres.
    url (str): URL for file.
"""

import argparse
import os
import sys
from time import time

import pandas as pd
import pyarrow.parquet as pq
from loguru import logger
from sqlalchemy import create_engine


def main(args):
    user = args.user
    password = args.password
    host = args.host
    port = args.port
    db = args.db
    tb = args.tb
    url = args.url

    # Get the name of the file from url
    file_name = url.rsplit("/", 1)[-1].strip()
    logger.info(f"Downloading {file_name} ...")
    # Download file from url
    os.system(f"curl {url.strip()} -o {file_name}")

    # Create SQL engine
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    # Read file based on csv or parquet
    if file_name.endswith(".csv") or file_name.endswith(".csv.gz"):
        df = pd.read_csv(file_name, nrows=10)  # Read first 10 rows to get schema
        df_iter = pd.read_csv(file_name, iterator=True, chunksize=100000)
    elif file_name.endswith(".parquet"):
        file = pq.ParquetFile(file_name)
        # Read first 10 rows to get schema
        df = next(file.iter_batches(batch_size=10)).to_pandas()
        df_iter = file.iter_batches(batch_size=100000)
    else:
        logger.info("Error: Only .csv or .parquet files allowed.")
        sys.exit()

    # Create the table in the database
    df.head(0).to_sql(name=tb, con=engine, if_exists="replace")

    # Insert values
    t_start = time()
    count = 0

    for batch in df_iter:
        count += 1

        if ".parquet" in file_name:
            batch_df = batch.to_pandas()
        else:
            batch_df = batch
            # CSV reading does not convert to datetime automatically
            batch_df.tpep_pickup_datetime = pd.to_datetime(
                batch_df.tpep_pickup_datetime
            )
            batch_df.tpep_dropoff_datetime = pd.to_datetime(
                batch_df.tpep_dropoff_datetime
            )

        logger.info(f"Inserting batch {count}...")
        b_start = time()
        batch_df.to_sql(name=tb, con=engine, if_exists="append")
        b_end = time()
        logger.info(f"Inserted! time taken {b_end-b_start:10.3f} seconds.\n")

    t_end = time()
    logger.info(
        f"Completed! Total time taken was {t_end-t_start:10.3f} seconds for {count} batches."
    )


if __name__ == "__main__":
    # Parsing arguments
    parser = argparse.ArgumentParser(
        description="Loading data from a file link to a Postgres datebase."
    )
    parser.add_argument("--user", help="Username for Postgres.")
    parser.add_argument("--password", help="Password to the username for Postgres.")
    parser.add_argument("--host", help="Hostname for Postgres.")
    parser.add_argument("--port", help="Port for Postgres connection.")
    parser.add_argument("--db", help="Databse name for Postgres")
    parser.add_argument("--tb", help="Destination table name for Postgres.")
    parser.add_argument("--url", help="URL for file.")
    args = parser.parse_args()
    main(args)
