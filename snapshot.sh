#!/bin/sh

DATE=$(date -d "yesterday 13:00" +"%Y-%m-%d")
CURRENT_SEASON=`python -c "from nbaspa.data.endpoints.parameters import CURRENT_SEASON; print(CURRENT_SEASON)"`

cd /opt

nbaspa-download daily --output-dir $DATA_DIR --game-date $DATE
nbaspa-clean daily --data-dir $DATA_DIR --output-dir $DATA_DIR --game-date $DATE
nbaspa-model daily --data-dir $DATA_DIR --output-dir $DATA_DIR --model $MODEL_PATH --game-date $DATE
nbaspa-rate --data-dir $DATA_DIR --output-dir $DATA_DIR --game-date $DATE
nbaspa-rate --data-dir $DATA_DIR --output-dir $DATA_DIR --game-date $DATE --mode survival-plus

gsutil -m rsync -r $DATA_DIR/$CURRENT_SEASON $GCS_PATH/$CURRENT_SEASON
gsutil -m rsync -r $DATA_DIR/commonplayerinfo $GCS_PATH/commonplayerinfo
