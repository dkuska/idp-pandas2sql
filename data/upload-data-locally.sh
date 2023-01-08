docker pull postgres
docker run --name my-postgres -p 5432:5432 -e POSTGRES_PASSWORD=mypassword -d postgres
export PGPASSWORD=mypassword
psql -h localhost -p 5432 -U postgres postgres -c "CREATE DATABASE tpc_h_01gb"
psql -h localhost -p 5432 -U postgres tpc_h_01gb -f dss.ddl
for i in `ls *.tbl`; do
  table=${i/.tbl/}
  echo "Loading $table..."
  sed 's/|$//' $i > /tmp/$i
  psql -h localhost -p 5432 -U postgres tpc_h_01gb -q -c "TRUNCATE $table"
  psql -h localhost -p 5432 -U postgres tpc_h_01gb -c "\\copy $table FROM '/tmp/$i' CSV DELIMITER '|'"
done
