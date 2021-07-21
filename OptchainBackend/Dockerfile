# pull official base image
FROM python:3.8

RUN apt-get update \
    && apt-get install -yyq netcat

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .

# copy custom yfinance module
RUN ls /usr/local/lib/python3.8/site-packages/
ADD ./modules/yfinance /usr/local/lib/python3.8/site-packages/yfinance

# copy project
COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
