# Etapa 1: build
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

# Etapa 2: imagem final com Nginx
FROM nginx:alpine

# Copia build do Vite
COPY --from=build /app/dist /usr/share/nginx/html

# Copia config simples do Nginx (opcional, usa a default se quiser)
# Exemplo de config:
#   - servir estático
#   - opcional: proxy /api para o backend
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
