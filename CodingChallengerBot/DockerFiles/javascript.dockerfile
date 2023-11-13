FROM alpine:latest


RUN mkdir "/workspace"
WORKDIR "/workspace"

RUN apk update && apk upgrade
RUN apk add --update nodejs
RUN apk add --update npm
RUN npm install chai
RUN npm install @codewars/test-compat

ENTRYPOINT ["node", "test.js"]
