# Development stage
FROM node:20-alpine AS development

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* /app/

RUN npm install

COPY frontend /app

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Production build stage
FROM node:20-alpine AS build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* /app/

RUN npm ci

COPY frontend /app

RUN npm run build

# Production serve stage
FROM nginx:alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html

COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
