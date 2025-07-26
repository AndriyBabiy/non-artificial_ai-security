FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with legacy peer deps to avoid conflicts
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]