# Development Dockerfile for frontend
FROM node:22-slim

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application code (for initial layer, will be overridden by volume mount)
COPY . .

# Expose the Vite dev server port
EXPOSE 5173

# Start Vite dev server with host binding for container access
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
