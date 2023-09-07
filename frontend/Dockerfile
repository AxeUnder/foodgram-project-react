# Build frontend
FROM node:13.12.0-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . ./
RUN npm run build

# Serve frontend using nginx
FROM nginx:1.19.3
COPY --from=build /app/build /usr/share/nginx/html
COPY infra/nginx.production.conf /etc/nginx/conf.d/default.conf
COPY /etc/letsencrypt /etc/letsencrypt
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
