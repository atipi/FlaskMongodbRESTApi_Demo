# -*- coding: utf-8 -*-

__version__ = '0.1.0'
__author__ = 'Porntip Chaibamrung'

import os

from flask import Flask
from flask_restful import Api
from flask_pymongo import PyMongo

from instance.config import app_config
from instance.resources import AddSong, ListSong, ListSongByLevel, SearchSong, RateSong, ListRating, GetStatRating
from instance.song import Song, create_from_file


def create_app(config_name=None):
    """
    Create and configure the app

    :param config_name: string of configuration. Possible values are 'testing', 'development' and 'production'
    :return: app: app object
    """

    app = Flask(__name__, instance_relative_config=True)

    is_test_mode = 0
    if config_name is None:
        config_name = 'development'

    if config_name == 'testing':
        is_test_mode = 1

    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py', silent=True)

    if is_test_mode == 1:
        app.config["MONGO_DBNAME"] = "test_songs_db"
        app.config["MONGO_URI"] = "mongodb://localhost:27017/test_songs_db"
    else:
        app.config["MONGO_DBNAME"] = "songs_db"
        app.config["MONGO_URI"] = "mongodb://localhost:27017/songs_db"

    app.config['mongodb'] = PyMongo(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        dbnames_list = Song().get_dbnames()

        # Import data from a file if songs collection does not exist in the database
        if len(dbnames_list) == 0:
            SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
            json_url = os.path.join(SITE_ROOT, "data/songs.json")
            create_from_file(file_path=json_url)

    # Define end points
    api = Api(app)
    api.add_resource(ListSong, "/songs", endpoint="songs", resource_class_kwargs={'config_name': config_name})
    api.add_resource(AddSong, "/songs/add", endpoint="songs_add", resource_class_kwargs={'config_name': config_name})
    api.add_resource(ListSongByLevel, "/songs/avg/difficulty", endpoint="songs_by_level",
                     resource_class_kwargs={'config_name': config_name})
    api.add_resource(SearchSong, "/songs/search", endpoint="search_songs",
                     resource_class_kwargs={'config_name': config_name})
    api.add_resource(RateSong, "/songs/rating", endpoint="rate_songs",
                     resource_class_kwargs={'config_name': config_name})
    api.add_resource(ListRating, "/rating", endpoint="ratings", resource_class_kwargs={'config_name': config_name})
    api.add_resource(GetStatRating, "/songs/avg/rating/<string:song_id>", endpoint="get_stat_rating",
                     resource_class_kwargs={'config_name': config_name})

    return app
