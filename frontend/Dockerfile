# # ============================================
# # Stage 1: Build the React + TypeScript app
# # ============================================
# FROM node:20-alpine AS builder

# # Set working directory
# WORKDIR /app

# # Copy package files first (for better layer caching)
# COPY package*.json ./

# # Install dependencies
# RUN npm ci --only=production=false

# # Copy source files
# COPY . .

# # Build the Vite app for production
# RUN npm run build

# # ============================================
# # Stage 2: Serve with Nginx
# # ============================================
# FROM nginx:1.25-alpine

# # Remove default nginx website
# RUN rm -rf /usr/share/nginx/html/*

# # Copy built app from builder stage (Vite outputs to /app/dist)
# COPY --from=builder /app/dist /usr/share/nginx/html

# # Copy custom nginx configuration
# COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# # Expose port 80
# EXPOSE 80

# # Add health check
# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#   CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

# # Start nginx
# CMD ["nginx", "-g", "daemon off;"]


# Stage 1: Build the React app
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies including devDependencies
RUN npm install

# Copy all source files
COPY . .

# Build the app for production
RUN npm run build

# ---------------------------------------------------------

# Stage 2: Serve the built app with Nginx
FROM nginx:alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy build folder from Stage 1 (Vite outputs to /app/dist)
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx config
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
