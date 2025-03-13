#!/bin/sh
url=`printenv REACT_APP_API_URL`
echo "REACT_APP_API_URL=$url" > .env
npm run start