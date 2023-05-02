#!/bin/sh
url=`printenv CM_URL`
echo "REACT_APP_BACKEND_IP_ADDRESS=$url" > .env
npm run start