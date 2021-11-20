#!/bin/bash

DATE=$(date -d "yesterday 13:00" +"%Y-%m-%d")

nbaspa-download daily --output-dir $DATA_DIR --game-date $DATE
nbaspa-clean daily --data-dir $DATA_DIR --output-dir $DATA_DIR --game-date $DATE
nbaspa-model daily --data-dir $DATA_DIR --output-dir $DATA_DIR --model $MODEL_PATH--game-date $DATE
nbaspa-rate --data-dir $DATA_DIR --output-dir $DATA_DIR --game-date $DATE
nbaspa-rate --data-dir $DATA_DIR --output-dir $DATA_DIR --game-date $DATE --mode survival-plus

gsutil -m rsync -r $DATA_DIR $GCS_PATH
