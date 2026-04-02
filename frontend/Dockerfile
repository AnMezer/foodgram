# build env
FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
RUN npm config set fetch-timeout 600000 && \
    npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm install
COPY . ./
RUN npm run build
CMD cp -r build result_build
