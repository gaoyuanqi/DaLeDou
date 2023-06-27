FROM python:3.11
WORKDIR /code
COPY . .
RUN  pip3 install -r requirements.txt
