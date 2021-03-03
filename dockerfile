# set base image (host OS)
FROM python:3.9

# set the working directory in the container
WORKDIR /fotor
    
# Download sentenses
ADD https://downloads.tatoeba.org/exports/sentences.tar.bz2 .
RUN tar xf sentences.tar.bz2

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY ./ .

# Set fotor alias
RUN echo 'alias fotor="python run.py"'
RUN . ~/.bashrc
# command to run on container start
CMD [ "python", "./run.py" ]
