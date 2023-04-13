FROM python:3.11
WORKDIR /code
COPY . .
RUN sh install.sh
