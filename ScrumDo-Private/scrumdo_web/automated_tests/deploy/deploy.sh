#!/bin/bash

# Checkout master, setup virtualenv, 3rd party dependencies and dev configs
SRCD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEST="projects" && PROJ="scrumdo" && VENV="env" && SRC=~/$DEST/$PROJ/$VENV/src
SRC1="http://saucelabs.com/downloads/Sauce-Connect-latest.zip" && DEP1="sauce-connect"
SRC2="http://apache.ip-connect.vn.ua/lucene/solr/3.6.2/apache-solr-3.6.2.zip" && DEP2="apache-solr"
SCHEMA=$SRC/apache-solr-3.6.2/example/solr/conf/schema.xml

mkdir -p ~/$DEST && cd ~/$DEST
if [ -d ~/$DEST/$PROJ ]; then
  echo "**> dropping ~/$DEST/$PROJ" && rm -fR ~/$DEST/$PROJ && cd ~/$DEST
fi
echo "**> git clone scrumdo repository" && git clone --recursive git@github.com:ScrumDoLLC/ScrumDo-Private.git $PROJ && cd $PROJ
echo "**> add project pypath to system" && echo 'export PYTHONPATH=$PYTHONPATH:'"$HOME/$DEST:$HOME/$DEST/$PROJ" >> ~/.bashrc
echo "**> activate and init virtualenv" && source ~/.bashrc && virtualenv $VENV && source $VENV/bin/activate && pip install -r requirements.txt
echo "**> import local settings config" && cp $SRCD/settings.py ~/$DEST/$PROJ/scrumdo_web/local_settings.py
echo "**> restore sqlite test database" && cp scrumdo_web/automated_tests/database.db.backup scrumdo_web/automated_tests/database.db

echo "**> drop dependencies" && rm -fR $SRC && mkdir -p $SRC && cd $SRC
echo "**> set up $DEP1" && curl $SRC1 > $DEP1 && unzip $DEP1 && rm $DEP1
echo "**> set up $DEP2" && curl $SRC2 > $DEP2 && unzip $DEP2 && rm $DEP2
echo "**> build schema" && cd ~/$DEST/$PROJ && python scrumdo_web/manage.py build_solr_schema > $SCHEMA

echo "**> development setup finished and ready to start: './start.sh'"