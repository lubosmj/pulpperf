#!/bin/sh

function wait_until_task_finished() {
    # Poll a Pulp task until it is finished
    echo "Polling the task until it has reached a final state."
    local task_url=$1
    while true
    do
        local response=$(http $task_url)
        local state=$(jq -r .state <<< ${response})
        jq . <<< "${response}"
        case ${state} in
            failed|canceled)
                echo "Task in final state: ${state}"
                exit 1
                ;;
            completed)
                echo "$task_url complete."
                break
                ;;
            *)
                echo "Still waiting..."
                sleep 1
                ;;
        esac
    done
}


function task_start_end() {
    local task_url=$1
    local response=$(http $task_url)
    local state=$(jq -r .state <<< ${response})
    local state=$(jq -r .started_at <<< ${response})
    local state=$(jq -r .finished_at <<< ${response})
}


function fatal() {
    echo "FATAL: $@" >&2
    exit 1
}


export BASE_ADDR=http://localhost:24817
export CONTENT_ADDR=http://localhost:24816

rpm --quiet -q jq || fatal "jq package missing"
rpm --quiet -q python2-httpie || fatal "python2-httpie package missing"
