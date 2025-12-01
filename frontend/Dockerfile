# Etapa 1: build
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Se quiser usar o .env.docker durante o build:
# COPY .env.docker .env

RUN npm run build

# Etapa 2: imagem final com Nginx
FROM nginx:alpine

# Copia build do Vite
COPY --from=build /app/dist /usr/share/nginx/html

# Copia config do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
