#!/bin/sh
url=`printenv API_IP`
port=`printenv API_PORT`
auth_url=`printenv AUTH_SERVER`
auth_client_id=`printenv AUTH_CLIENT`
auth_redirect_uri=`printenv AUTH_REDIRECT_URL`
truncate -s 0 .env
echo "REACT_APP_BACKEND_IP_ADDRESS=$url" >> .env
echo "REACT_APP_BACKEND_PORT=$port" >> .env
echo "REACT_APP_AUTH_URL=$auth_url" >> .env
echo "REACT_APP_AUTH_KEY=$auth_client_id" >> .env
echo "REACT_APP_AUTH_REDIRECT_IP=$auth_redirect_uri" >> .env
npm run start