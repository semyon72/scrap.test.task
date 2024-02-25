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
pg_dump_cmd="pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -n $db_schema -t $db_table $DB_NAME"

zip_file_name=${CRON_DUMP_DIR}/dump-${today}.zip
$pg_dump_cmd | zip "${zip_file_name}" - && printf "@ -\n@=dump-%s.sql\n" "$now" | zipnote -w "${zip_file_name}"
echo "${now}: dump into ${zip_file_name} is successful."
