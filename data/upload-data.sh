export PGPASSWORD=idp22-hisssql
psql -h 172.20.18.12 -p 5777 -U admin idp -c "CREATE DATABASE $1"
psql -h 172.20.18.12 -p 5777 -U admin $1 -f dss.ddl
for i in `ls *.tbl`; do
  table=${i/.tbl/}
  echo "Loading $table..."
  sed 's/|$//' $i > /tmp/$i
  psql -h 172.20.18.12 -p 5777 -U admin $1 -q -c "TRUNCATE $table"
  psql -h 172.20.18.12 -p 5777 -U admin $1 -c "\\copy $table FROM '/tmp/$i' CSV DELIMITER '|'"
done
