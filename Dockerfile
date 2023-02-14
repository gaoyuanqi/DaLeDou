FROM python:3.10
WORKDIR /code
COPY . .
RUN sh install.sh
