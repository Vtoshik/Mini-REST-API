# Dev-only image: runs `next dev` with hot reload against a bind-mounted
# source tree (see ../docker-compose.yml). Not a production build.
FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 3000

# -H 0.0.0.0 instead of `npm run dev`: Next's dev server only binds to
# localhost by default, which inside a container means unreachable from
# the published port.
CMD ["npx", "next", "dev", "-H", "0.0.0.0"]
