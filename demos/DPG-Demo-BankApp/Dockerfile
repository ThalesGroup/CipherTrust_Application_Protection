# Build the Next.js app
FROM node:lts-alpine AS build
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install
COPY . .
RUN yarn build

# Serve the Next.js app
FROM node:lts-alpine AS serve
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install --production
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/next.config.js ./next.config.js
COPY --from=build /app/prisma ./prisma
RUN npx prisma generate
EXPOSE 3000

CMD ["yarn", "start"]