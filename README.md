Pulp performance testing related stuff
======================================

Installation:

    ansible-playbook -i conf/inventory.ini playbooks/install/install_pulp3.yaml

Configure monitoring:

    ansible-playbook -i conf/inventory.ini playbooks/collectd-generic.yaml -e "carbon_host=carbon.example.com carbon_port=2003 graphite_prefix=pulp3"

Create pulp file repository (100k files with 10B each):

    scripts/create_pulp_file_repo.py --files-count 100000 --file-size 10 --directory file-100k-10B/

Measure:

    cd tests/
    rm -f status-data.json
    ./sync_repository.py http://repos.example.com/pub/pulpperf/file-10k-10B-B/ http://repos.example.com/pub/pulpperf/file-10k-10B-C/ http://repos.example.com/pub/pulpperf/file-10k-10B-D/   # create and sync repo
    ./resync_repository.py   # resync repository
    ./publish_repository.py   # create publication and distribution
    ./download_repository.py   # download all units from repository
    ./list_content.py   # list and inspect repository content
    ./repo_version.py   # clone repository version
