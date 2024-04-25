## Docker and SQL

### Running Postgres with Docker

#### Linux and MacOS
```bash
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:13
```

If you see that `ny_taxi_postgres_data` is empty after running
the container, try these:

- Deleting the folder and running Docker again (Docker will re-create the folder)
- Adjust the permissions of the folder by running `sudo chmod a+rwx ny_taxi_postgres_data`

### CLI for Postgres
We want to install `pgcli` to connect to Postgres. To do so, we first need an isolated environment. We can use `conda` for that. First, we create an `environment.yml` file with the following content:
```yaml
name: docker-sql-env
channels:
  - conda-forge
  - nodefaults
dependencies:
  - python=3.11
  - pip
  - pgcli
  - pandas
  - sqlalchemy
  - psycopg2
  - pyarrow
  - loguru
  - ipykernel
```

Then we create the environment with the following command:
```bash
conda env create -f environment.yml
```

After that, we activate the environment:
```bash
conda activate docker-sql-env
```

Now, we can install `pgcli` in our environment:
```bash
conda install pgcli
```

Using `pgcli` to connect to Postgres

```bash
pgcli -h localhost -p 5432 -u root -d ny_taxi
```


### NY Trips Dataset

Dataset:
- https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- https://www1.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf

The [TLC trip data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) is in `.parquet` format. We will use the *yellow taxi* trip data, which can be downloaded by running:
```bash
curl -L https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet -o yellow_tripdata_2021-01.parquet
```

Previously, the TLC trip data was in `.csv` format - the course repo still has a copy - that can be downloaded by running:
```bash
curl -L https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz -o yellow_tripdata_2021-01.csv.gz
```

The Taxi Zone Lookup Table can be downloaded by running the following commands:
```bash
curl -L https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv -o taxi_zone_lookup.csv
```

I have cleaned up the original notebooks and scripts to load this data into postgres - making them easier to follow. See:
- [data_loading.py](data_loading.py)
- [data_loading.ipynb](data_loading.ipynb)


### pgAdmin

Running pgAdmin

```bash
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  dpage/pgadmin4
```

### Running Postgres and pgAdmin together

Create a network

```bash
docker network create pg-network
```

Run Postgres (change the path)

```bash
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v c:/Users/alexe/git/data-engineering-zoomcamp/week_1_basics_n_setup/2_docker_sql/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network=pg-network \
  --name pg-database \
  postgres:13
```

Run pgAdmin

```bash
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  --network=pg-network \
  --name pgadmin-2 \
  dpage/pgadmin4
```


### Data ingestion

Running locally

```bash
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

python ingest_data.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --table_name=yellow_taxi_trips \
  --url=${URL}
```

Build the image

```bash
docker build -t taxi_ingest:v001 .
```

On Linux you may have a problem building it:

```
error checking context: 'can't stat '/home/name/data_engineering/ny_taxi_postgres_data''.
```

You can solve it with `.dockerignore`:

- Create a folder `data`
- Move `ny_taxi_postgres_data` to `data` (you might need to use `sudo` for that)
- Map `-v $(pwd)/data/ny_taxi_postgres_data:/var/lib/postgresql/data`
- Create a file `.dockerignore` and add `data` there
- Check [this video](https://www.youtube.com/watch?v=tOr4hTsHOzU&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb) (the middle) for more details



Run the script with Docker

```bash
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pg-database \
    --port=5432 \
    --db=ny_taxi \
    --table_name=yellow_taxi_trips \
    --url=${URL}
```

### Docker-Compose

Run it:

```bash
docker-compose up
```

Run in detached mode:

```bash
docker-compose up -d
```

Shutting it down:

```bash
docker-compose down
```

Note: to make pgAdmin configuration persistent, create a folder `data_pgadmin`. Change its permission via

```bash
sudo chown 5050:5050 data_pgadmin
```

and mount it to the `/var/lib/pgadmin` folder:

```yaml
services:
  pgadmin:
    image: dpage/pgadmin4
    volumes:
      - ./data_pgadmin:/var/lib/pgadmin
    ...
```


### SQL

Coming soon!
