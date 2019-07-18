Pulp performance testing related stuff
======================================

Installation:

    ansible-playbook -i conf/inventory.ini playbooks/install/install_pulp3.yaml

Create pulp file repository (100k files with 10B each):

    mkdir file-100k-10B/
    scripts/create_pulp_file_repo.py --files-count 100000 --file-size 10 --directory file-100k-10B/
