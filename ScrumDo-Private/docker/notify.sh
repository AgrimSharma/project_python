#!/bin/bash
ACCESS_TOKEN=8517446bc42e45aeaa2b36abf126c576
ENVIRONMENT=production-v2-ecs

LOCAL_USERNAME=`whoami`
REVISION=`git log -n 1 --pretty=format:"%H"`

curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token=$ACCESS_TOKEN \
  -F environment=$ENVIRONMENT \
  -F revision=$REVISION \
  -F local_username=$LOCAL_USERNAME


curl -H "x-api-key:9a70a07f58e6682d432701b229f263d46374b1f5e675380" -d "deployment[app_name]=ScrumDo V2 App Server" https://api.newrelic.com/deployments.xml