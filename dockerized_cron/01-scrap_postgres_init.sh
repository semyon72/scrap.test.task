#!/bin/bash
set -ex

if [ -n "$DOT_ENV" ] && [ -f "$DOT_ENV" ]; then

while read -r LINE; do
  if [[ $LINE == *'='* ]] && [[ $LINE != '#'* ]]; then
    eval "declare $(echo "$LINE" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  fi
done < "$DOT_ENV"

echo "$POSTGRES_DB"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE USER "$DB_USER" PASSWORD '$DB_PASSWORD' ;
  CREATE DATABASE "$DB_NAME";
  GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "$DB_USER";
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" <<-EOSQL
  GRANT ALL PRIVILEGES ON SCHEMA "public" TO "$DB_USER";
EOSQL

else
echo "File '${DOT_ENV}' is not found. Custom user/database creation was skipped"
fi
