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

#install app dependenccies

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

#bundle app source then copy the current folder into work directory folder in container
COPY . .

#port of container by default
EXPOSE 5000

# #run app in container
# CMD [ "python","run.py" ]
ENTRYPOINT ["sh", "entrypoint.sh"]
