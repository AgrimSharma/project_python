#!/bin/bash

# These are DEPLOYMENT keys, not app run keys

# We need 2 different set of access keys, one for rackspace environment,
# and one for qa environment on our own aws account.
# This script sets the keys to rackspace.

# The values of RACK_AWS_ACCESS_* are set in the circleci configuration website.

export AWS_ACCESS_KEY_ID=$RACK_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$RACK_AWS_SECRET_ACCESS_KEY
export ECR=418483041397.dkr.ecr.us-east-1.amazonaws.com
export CLUSTER=ProdECS-ECSCluster-11PNPNNZ7D0J
