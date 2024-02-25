#!/bin/bash

msg="$(date): I am alive."
echo "$msg" >> "$CRON_LOG_DIR/cron-alive-$(date +%F).log"
echo "$msg"
