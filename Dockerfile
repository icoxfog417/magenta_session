# magenta-session Dockerfile

# base image
FROM tensorflow/magenta:0.1.10

# installing  library
COPY ./requirements_heroku.txt /tmp/
RUN pip install -r /tmp/requirements_heroku.txt

# deploy magenta-session module
COPY . /opt/

# port
#EXPOSE 8080

# deamon run
WORKDIR /opt/server/
# CMD python server.py
CMD gunicorn -b 0.0.0.0:$PORT server:app
