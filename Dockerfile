FROM node:16-alpine

WORKDIR /app

# install dependencies
COPY ./package.json ./
RUN yarn

CMD [ "yarn", "run", "start" ]
