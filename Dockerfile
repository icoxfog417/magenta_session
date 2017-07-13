# magenta-session Dockerfile

# base image
FROM tensorflow/magenta:latest

RUN apt-get update && apt-get install -y --no-install-recommends libasound2-dev && apt-get clean

# installing  library
COPY ./requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# deploy magenta-session module
COPY . /src/

# port
#EXPOSE 8080

# deamon run
WORKDIR /src/server/
CMD python server.py
