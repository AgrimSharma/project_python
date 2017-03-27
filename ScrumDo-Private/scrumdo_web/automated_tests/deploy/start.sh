#!/bin/bash

# Starting Django, Celery and Solr
SRCD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEST="projects" && PROJ="scrumdo" && VENV="env" && SRC=~/$DEST/$PROJ/$VENV/src
SOLR=$SRC/apache-solr-3.6.2/example

cd ~/$DEST/$PROJ && source $VENV/bin/activate && pip install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:$HOME/$DEST:$HOME/$DEST/$PROJ
python scrumdo_web/manage.py runserver localhost:9000 > runserver.log 2>&1 &
python scrumdo_web/manage.py celeryd > celeryd.log 2>&1 &
cd $SOLR && java -jar start.jar > solr.log 2>&1 &

echo "**> everything started and ready for testing:'./test.sh'('ctrl+c' to stop)" &

trap "kill -TERM -$$" SIGINT

wait