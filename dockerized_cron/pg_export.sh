#!/bin/bash

set -e

now=$(date '+%F_%H:%M:%S')
today=$(date +%F)

while read -r LINE; do
  if [[ $LINE == *'='* ]] && [[ $LINE != '#'* ]]; then
    eval "declare $(echo "$LINE" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  fi
done < "$DOT_ENV"

db_schema='public'
db_table='ria_used_cars'

PGPASSWORD=$DB_PASSWORD
psql_cmd="psql -h $DB_HOST -U $DB_USER -d $DB_NAME --tuples-only --command"
psql_chk_tbl=$(cat <<-EOSQL
  SELECT EXISTS (
    SELECT FROM information_schema.tables
      WHERE table_schema = '$db_schema'
        AND table_name = '$db_table'
  );
EOSQL
)

res=$( ${psql_cmd} "$psql_chk_tbl" | tr -d '[:space:]' )
if [ -n "$res" ] && [ "$res" = 'f' ]; then
  echo "${now}: table $db_schema.$db_table not found. Nothing to export."
  exit 0
fi

zip_file_name=${CRON_EXPORT_DIR}/export-${today}.zip

$psql_cmd \
"copy public.ria_used_cars TO STDOUT DELIMITER ',' CSV ENCODING 'UTF8' QUOTE '\"' ESCAPE '''';" | \
zip "${zip_file_name}" - && \
printf "@ -\n@=export-%s.csv\n" "$now" | zipnote -w "${zip_file_name}"

echo "${now}: export into ${zip_file_name} is successful."
