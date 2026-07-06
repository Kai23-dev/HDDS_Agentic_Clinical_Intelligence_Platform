FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm install

# Build the frontend
COPY frontend/ .
RUN npm run build

# Serve with a lightweight HTTP server
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
