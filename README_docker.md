# Shell md docker run

Shellmd can be started inside docker container. This approach requires to have prepared custom image with all dependenices resolved.
Simple example of run is
```
# executable block
docker build -t shellmd -f Dockerfile .
#docker run -it  shellmd /usr/bin/python3 /app/shellmd/bin/shellmd.py --input-file=/app/shellmd/test/README.md
docker run -it  -v "$(pwd)"/:/app/shellmd  shellmd /usr/bin/python3 /app/shellmd/bin/shellmd.py --input-file=/app/shellmd/README.md --config-file=config_file_docker
```

To set shellmd in your custom contianer you can modify your docker file 
```
# debian based docker
RUN apt-get update && apt-get -y install python3 git 
RUN mkdir -p /app
git clone https://github.com/martinkala/shellmd /app/shellmd
COPY . /app/shellmd
```
