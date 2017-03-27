#!/bin/bash

# Running Suite
DEST="projects"
PROJ="scrumdo"
VENV="env"

cd ~/$DEST/$PROJ
source $VENV/bin/activate
export TEST_CASE_CLASS=FunctionalTestCase
python scrumdo_web/automated_tests/selenium/suite.py