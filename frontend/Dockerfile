FROM node:alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Используем preview сервер Vite
FROM node:alpine

WORKDIR /app

# Копируем только собранные файлы и node_modules (нужен для vite preview)
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package*.json ./

EXPOSE 4173

# Vite preview по умолчанию использует порт 4173
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4173"]