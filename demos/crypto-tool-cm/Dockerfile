FROM node:alpine
RUN mkdir -p /usr/src
WORKDIR /usr/src

# copy source files
COPY . /usr/src

# install dependencies
RUN npm install
RUN mkdir node_modules/.cache && chmod -R 777 node_modules/.cache

# start app
RUN npm run build
EXPOSE 3000
CMD npm run start