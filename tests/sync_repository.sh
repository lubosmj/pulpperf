#!/bin/sh

# Sync repository provided in param. If more repos provided, all are synced in parallel.

source ./lib.sh

if [ "$#" -eq "0" ]; then
    fatal "No repository to sync provided"
fi

repos=$( mktemp )
for REPO_PATH in $@; do
    # Create repo
    export REPO_NAME=$(head /dev/urandom | tr -dc a-z | head -c5)
    export REPO_HREF=$(http POST $BASE_ADDR/pulp/api/v3/repositories/ name=$REPO_NAME | jq -r '._href')
    ###http $BASE_ADDR$REPO_HREF

    # Create remote
    export REMOTE_NAME=$(head /dev/urandom | tr -dc a-z | head -c5)
    http POST $BASE_ADDR/pulp/api/v3/remotes/file/file/ name="$REMOTE_NAME" url="$REPO_PATH/PULP_MANIFEST"
    export REMOTE_HREF=$(http $BASE_ADDR/pulp/api/v3/remotes/file/file/ | jq -r ".results[] | select(.name == \"$REMOTE_NAME\") | ._href")
    ###http $BASE_ADDR$REMOTE_HREF

    echo "$REPO_HREF $REMOTE_HREF" >>$repos
done

tasks=$( mktemp )
while IFS= read -r row; do
    REPO_HREF=$( echo "$row" | cut -d ' ' -f 1 )
    REMOTE_HREF=$( echo "$row" | cut -d ' ' -f 2 )
    # Sync repo using remote
    http --ignore-stdin POST $BASE_ADDR$REMOTE_HREF'sync/' repository=$REPO_HREF mirror=False
    ###export TASK_URL=$(http POST $BASE_ADDR$REMOTE_HREF'sync/' repository=$REPO_HREF mirror=False | jq -r '.task')

    echo "$TASK_URL" >>$tasks
done <$repos

while IFS= read -r row; do
    TASK_URL="$row"
    wait_until_task_finished $BASE_ADDR$TASK_URL
    ###export REPOVERSION_HREF=$(http $BASE_ADDR$TASK_URL| jq -r '.created_resources | first')
    ###http $BASE_ADDR$REPOVERSION_HREF
done <$tasks
