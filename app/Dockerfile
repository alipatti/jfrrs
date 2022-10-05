FROM node:16-alpine
COPY . .








# ##############
# # BASE IMAGE #
# ##############
# FROM node:16-alpine AS base
# WORKDIR /app
# ENV NODE_ENV production

# COPY package.json .
# COPY package-json.json .
# RUN npm clean-install

# ENV PORT 3000
# EXPOSE 3000


# ######################
# # DEPENDENCIES IMAGE #
# ######################
# FROM base as dependencies
# RUN npm clean-install


# #####################
# # DEVELOPMENT IMAGE #
# #####################
# FROM dependencies as development
# ENV NODE_ENV development
# COPY . .
# CMD npm run dev


# ###############
# # BUILD IMAGE #
# ###############
# FROM dependencies AS build
# COPY . .
# RUN npm run build


# ####################
# # PRODUCTION IMAGE #
# ####################
# FROM base AS production

# COPY --from=build /app/public ./public
# COPY --from=build --chown=node /app/.next/standalone ./
# COPY --from=build --chown=node /app/.next/static ./.next/static

# USER node
# CMD npm start
