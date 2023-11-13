FROM alpine:latest


RUN mkdir "/workspace"
WORKDIR "/workspace"

RUN apk update && apk upgrade
RUN apk add --no-cache python3
RUN apk add --no-cache git
RUN apk add cmd:pip3
RUN apk add cmd:git
RUN pip3 install --upgrade pip
RUN pip3 install git+https://github.com/codewars/python-test-framework.git#egg=codewars_test

ENTRYPOINT ["python3", "-u", "test.py"]
