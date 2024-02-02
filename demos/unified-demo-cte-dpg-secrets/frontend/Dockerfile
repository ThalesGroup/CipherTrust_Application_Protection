FROM node:alpine
WORKDIR /app
COPY ./ ./
RUN npm i --force
RUN rm -rf node_modules/.cache && mkdir node_modules/.cache && chmod -R 777 node_modules/.cache
RUN chmod -v +x entrypoint.sh
ENTRYPOINT ["sh", "/app/entrypoint.sh"]