#!/bin/bash
source /home/ec2-user/scrumdo-v2-env/bin/activate
python -W ignore::DeprecationWarning /home/ec2-user/scrumdo-v2/scrumdo_web/manage.py extras_sync pull
python -W ignore::DeprecationWarning /home/ec2-user/scrumdo-v2/scrumdo_web/manage.py sync_github_teams

