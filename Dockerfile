# download main image from docker hub
FROM python:3

#create work directoy which contains app
WORKDIR /app

# define flask app enviroment variables
# ENV ENV_DO_MANH_DUNG domanhdung
# ENV FLASK_RUN_HOST 0.0.0.0
ENV MYSQL_DATABASE casc4de_test
ENV MYSQL_HOST 127.0.0.1
ENV MYSQL_USER mddo
ENV MYSQL_PASSWORD dung123

#install app dependenccies
# COPY environment.yml .

# RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
# SHELL ["conda", "run", "-n", "nguacon01", "/bin/bash", "-c"]

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

#bundle app source then copy the current folder into work directory folder in container
COPY . .

#port of container by default
EXPOSE 5000

# #run app in container
CMD [ "python","run.py" ]

# The code to run when container is started:
# COPY run.py .
# ENTRYPOINT ["conda", "run", "-n", "nguacon01", "python", "run.py"]
