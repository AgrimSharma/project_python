#!/bin/bash
source /home/ec2-user/scrumdo-v2-env/bin/activate
python -W ignore::DeprecationWarning /home/ec2-user/scrumdo-v2/scrumdo_web/manage.py burnup_chart
python -W ignore::DeprecationWarning /home/ec2-user/scrumdo-v2/scrumdo_web/manage.py record_kanban_backlog
