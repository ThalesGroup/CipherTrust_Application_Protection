# Stage 1: Build dependencies (with network fixes)
FROM node:20-alpine AS deps
WORKDIR /app

# 1. Override DNS via ENV instead of /etc/resolv.conf
ENV NODE_OPTIONS="--dns-result-order=ipv4first"
RUN npm config set registry https://registry.npmmirror.com && \
    npm config set fetch-retry-maxtimeout 120000

# 2. Copy ONLY package files first (for caching)
COPY package.json package-lock.json ./
RUN npm ci --no-cache

# Stage 2: Final image
FROM node:20-alpine
WORKDIR /app

# 3. Copy dependencies from cached stage
COPY --from=deps /app/node_modules ./node_modules

# 4. Copy app files
COPY . .

# 5. Fix permissions safely (no 777!)
RUN mkdir -p node_modules/.cache && \
    chown -R node:node node_modules/.cache && \
    chmod -R 755 node_modules/.cache && \
    chmod +x entrypoint.sh

# 6. Run as non-root user
USER node

ENTRYPOINT ["sh", "/app/entrypoint.sh"]