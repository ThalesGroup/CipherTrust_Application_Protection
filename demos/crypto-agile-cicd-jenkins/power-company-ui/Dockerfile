# Dockerfile for React App

# Stage 1: Build the React app
FROM node:22 AS build
WORKDIR /app
COPY package.json ./
RUN yarn install
COPY . .
RUN yarn build

# Stage 2: Serve the React app using Nginx
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]