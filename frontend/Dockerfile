# Build context: monorepo root (.) — required for production nginx.conf COPY
# See docker-compose.yml frontend.build.context
FROM node:20-alpine AS base
WORKDIR /app
# Enable pnpm via corepack (ships with Node 20)
RUN corepack enable && corepack prepare pnpm@9 --activate

FROM base AS deps
COPY frontend/package.json frontend/pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# ── dev stage: used by docker-compose.dev.yml ─────────────────────────────────
# Source code is volume-mounted at runtime — only node_modules pre-installed
FROM base AS dev
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/package.json ./
# Actual source files come from volume mount in docker-compose.dev.yml

# ── production build ───────────────────────────────────────────────────────────
FROM deps AS builder
COPY frontend/ .
RUN pnpm build

FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY infra/nginx/nginx.conf /etc/nginx/conf.d/default.conf
