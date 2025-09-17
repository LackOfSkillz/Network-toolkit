FROM node:20-slim
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --silent || npm install --silent
COPY . .
CMD ["npm", "run", "dev", "--", "--host"]
