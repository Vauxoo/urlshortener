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
