# FlaskMongodbRESTApi_Demo
Flask RESTFul API with Mongodb

## Implemented end points

Supported end points:

- GET /songs
  - Returns a list of songs with some details on them
  - Add possibility to paginate songs.

- GET /songs/avg/difficulty
  - Takes an optional parameter "level" to select only songs from a specific level.
  - Returns the average difficulty for all songs.

- GET /songs/search
  - Takes in parameter a 'message' string to search.
  - Return a list of songs. The search should take into account song's artist and title. The search should be case insensitive.

- POST /songs/rating
  - Takes in parameter a "song_id" and a "rating"
  - This call adds a rating to the song. Ratings should be between 1 and 5.

- GET /songs/avg/rating/<song_id>
  - Returns the average, the lowest and the highest rating of the given song id.

## Pre-requirement

* pipenv
* python 3
* Postman (optional)

You can use also other tools rather than Postman.

## Installation

* Clone data from Git with following command

[prompt]git clone git@github.com:atipi/FlaskMongodbRESTApi_Demo.git

* [prompt]cd FlaskMongodbRESTApi_Demo

* [prompt]pipenv shell

* [prompt]pipenv install

## Usage

### For Ubuntu user

* [prompt]cd FlaskMongodbRESTApi_Demo

* [prompt]pipenv shell

* [prompt]source set_env_DEV.sh

* [prompt]flask run

* start testing via Postman

## Testing

### For unit testing

* [prompt]cd FlaskMongodbRESTApi_Demo

* [prompt]pipenv shell

* [prompt]python -m unittest tests/test_api.py


