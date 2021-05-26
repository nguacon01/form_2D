# download main image from docker hub
FROM python:3.8.6

#create work directoy which contains app
WORKDIR /form_2D

# define flask app enviroment variables
# ENV ENV_DO_MANH_DUNG domanhdung
# ENV FLASK_RUN_HOST 0.0.0.0
ENV MYSQL_DATABASE casc4de_test
ENV MYSQL_HOST 127.0.0.1
ENV MYSQL_USER mddo
ENV MYSQL_PASSWORD dung123

# copy the file requirements.txt from current folder of host to folder "/test_flask" in docker's image
COPY requirements.txt requirements.txt
# update pip
RUN pip install --upgrade pip
# install all the dependencies
RUN pip install -r requirements.txt

#copy all files in the current folder of host to the folder "/test_flask" in docker's image
COPY . .

#port of container which is exposed
EXPOSE 5000

# run app in container
# CMD could only run one command. For example here, it will run command: python wsgi.py
# CMD [ "python","wsgi.py" ]
# In the other way, ENTRYPOINT could run multiple command in one line. For example here, it will run command: sh entrypoint.sh
ENTRYPOINT ["sh", "entrypoint.sh"]
