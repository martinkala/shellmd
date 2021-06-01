FROM debian:10-slim
ENV NO_PROXY=localhost
RUN apt-get update && apt-get -y install python3 
WORKDIR /
RUN mkdir -p /app/shellmd
COPY . /app/shellmd
