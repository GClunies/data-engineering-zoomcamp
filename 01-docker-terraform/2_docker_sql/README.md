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

Using `pgcli` to connect to postgres.

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

I have cleaned up the original course notebooks and scripts to load this data into postgres - making them easier to follow. See:
- [data_loading.py](data_loading.py)
- [data_loading.ipynb](data_loading.ipynb)


### pgAdmin
Instead of accessing/querying the postgres database via `pgcli`, we can use a GUI tool like `pgadmin`. We can run pgAdmin in a Docker container by running the following command:
```bash
# Running pgAdmin in Docker
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  dpage/pgadmin4  # The image name with pgadmin pre-installed
```
If you try and connect to the postgres database from pgAdmin, you will get an error. This is because the postgres container is running in a different "network" to the pgAdmin container. To fix this, we need to create a network and run both containers in that network.

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
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
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
Now that we can run postgres and pgAdmin together, we still need to load the data into the database. We can do this by running the `data_loading.py` script (similar to `data_loading.ipynb`). The script will load the data from the `.parquet` file into the `ny_taxi` database in the `yellow_taxi_trips` table.

To run the script locally
```bash
URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet"

python data_loading.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --database=ny_taxi \
  --table=yellow_taxi_trips \
  --url=${URL}
```

It is best practice to run our data loading script in a Docker container where we can specify the dependencies in a `Dockerfile`. To do this, we need to:
1. Create a `Dockerfile` to define the docker image along with any dependencies for the  and entrypoint.
2. Build the image.
3. Run the script in the newly built Docker image.

Build the image
```bash
docker build -t taxi_ingest:v001 .
```

On Linux you may have a problem building it:ds
```
error checking context: 'can't stat '/home/name/data_engineering/ny_taxi_postgres_data''.
```
You can solve it with `.dockerignore`:
- Create a folder `data`
- Move `ny_taxi_postgres_data` to `data` (you might need to use `sudo` for that)
- Map `-v $(pwd)/data/ny_taxi_postgres_data:/var/lib/postgresql/data`
- Create a file `.dockerignore` and add `data` there
- Check [this video](https://www.youtube.com/watch?v=tOr4hTsHOzU&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb) (the middle) for more details


Run the script in the newly built Docker container.
```bash
URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet"

docker run -it \
  --network=pg-network \
  data_loading:v001 \
    --user=root \
    --password=root \
    --host=pg-database \
    --port=5432 \
    --database=ny_taxi \
    --table=yellow_taxi_data \
    --url=${URL}
```

### Docker-Compose
Instead of running separate commdands to initialize the postgres and pgAdmin containers and connect them to the same network, we can use `docker-compose` to run them together. The `docker-compose.yml` file in this directory defines the services (postgres and pgAdmin) and their configurations.

Run it:
```bash
docker-compose up
```

If you look in Docker Desktop, you will see a Docker 'stack' with two containers running: `postgres` and `pgadmin`. You can access pgAdmin at `localhost:8080` and login with the email and password you specified in the `docker-compose.yml` file.

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
