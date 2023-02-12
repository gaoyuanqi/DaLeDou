FROM python:alpine
WORKDIR /code
COPY . .
RUN sh install.sh
