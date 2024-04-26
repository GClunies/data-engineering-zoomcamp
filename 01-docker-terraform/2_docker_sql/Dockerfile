FROM python:3.11

# Install wget
RUN apt-get install wget

# Install Python packages
# Could use conda here, but use pip for simplicity
RUN pip install pandas sqlalchemy psycopg2 pyarrow loguru

# set the working directory in the container
WORKDIR /app

# Copy data_loading.py from local dir into the container
COPY data_loading.py data_loading.py

# Run the data_loading.py Python script when the container launches
ENTRYPOINT [ "python", "data_loading.py" ]
