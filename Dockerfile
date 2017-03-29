# magenta-session Dockerfile

# base image
FROM tensorflow/magenta:0.1.10

# installing  library
COPY ./requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# deploy magenta-session module
COPY . /src/

# port
#EXPOSE 8080

# deamon run
CMD python /src/server/server.py
