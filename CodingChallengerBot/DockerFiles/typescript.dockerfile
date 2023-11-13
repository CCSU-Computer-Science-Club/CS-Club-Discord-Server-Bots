FROM alpine:latest


RUN mkdir "/workspace"
WORKDIR "/workspace"

RUN apk update && apk upgrade
RUN apk add --update nodejs
RUN apk add --update npm
RUN npm install chai
RUN npm install @codewars/test-compat
RUN npm install -g typescript

COPY typescript-entry.sh /workspace/typescript-entry.sh
RUN chmod +x /workspace/typescript-entry.sh

ENTRYPOINT ["sh", "typescript-entry.sh"]
