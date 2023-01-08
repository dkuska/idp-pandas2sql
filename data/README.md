# Upload Data to Postgres

- First generate data using the TPC-H data generation tool, e.g. `./dbgen -s 10`. Here 10 is the size of data generated in GB.
- Run the *upload-data.sh* script and pass the name of the created database as the first argument, e.g. `source upload-data.sh tpc_h`
