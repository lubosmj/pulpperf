#!/bin/sh

source ./lib.sh

REPO_PATH="$1"   # Path to the repository to sync
if [ -z "$REPO_PATH" ]; then
    fatal "Variable REPO_PATH empty (first param)"
fi

# Create repo
export REPO_NAME=$(head /dev/urandom | tr -dc a-z | head -c5)
export REPO_HREF=$(http POST $BASE_ADDR/pulp/api/v3/repositories/ name=$REPO_NAME | jq -r '._href')
###http $BASE_ADDR$REPO_HREF

# Create remote
export REMOTE_NAME=$(head /dev/urandom | tr -dc a-z | head -c5)
http POST $BASE_ADDR/pulp/api/v3/remotes/file/file/ name="$REMOTE_NAME" url="$REPO_PATH/PULP_MANIFEST"
export REMOTE_HREF=$(http $BASE_ADDR/pulp/api/v3/remotes/file/file/ | jq -r ".results[] | select(.name == \"$REMOTE_NAME\") | ._href")
###http $BASE_ADDR$REMOTE_HREF

# Sync repo using remote
export TASK_URL=$(http POST $BASE_ADDR$REMOTE_HREF'sync/' repository=$REPO_HREF mirror=False | jq -r '.task')
wait_until_task_finished $BASE_ADDR$TASK_URL
export REPOVERSION_HREF=$(http $BASE_ADDR$TASK_URL| jq -r '.created_resources | first')
###http $BASE_ADDR$REPOVERSION_HREF
