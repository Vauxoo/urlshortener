[![Build Status](https://travis-ci.org/Vauxoo/urlshortener.svg?branch=master)](https://travis-ci.org/Vauxoo/urlshortener)

# urlshortener
A URL shortening Flask micro website similar to bit.ly 

## To launch the application:

    docker build -t urlshortener .
    docker run -ti -p 5000:5000 -v var:/app/var urlshortener

## To program on it:

    virtualenv -p python3 env
    . env/bin/activate
    pip install -r requirements.txt

## Running (no docker):

    python main.py
    python main.py --help

## Running test suite:

    tox

## Supoort for postgresql.

If the environment variable USE_POSTGRESQL is setted you will be able to save all in postresql
this docker has the ability of provide some standard configurations following
the base [Postgresql image on docker](https://docs.docker.com/engine/examples/postgresql_service/)
documentation, nothing special is implemented until now.
