FROM node:alpine
WORKDIR /app
COPY ./ ./
RUN npm i
RUN mkdir node_modules/.cache && chmod -R 777 node_modules/.cache
RUN chmod -v +x entrypoint.sh
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
EXPOSE 3000