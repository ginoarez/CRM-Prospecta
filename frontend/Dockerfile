FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
# This machine sits behind an SSL-intercepting proxy; without trusting it, npm silently
# skips Next's optional native SWC binary (@next/swc-linux-x64-musl), breaking `next dev`.
RUN npm config set strict-ssl false && npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
