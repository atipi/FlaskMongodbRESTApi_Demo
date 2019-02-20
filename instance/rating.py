# -*- coding: utf-8 -*-

__version__ = '0.1.0'
__author__ = 'Porntip Chaibamrung'


import bson
import datetime

from flask import current_app, json
from instance.song import get_dict_data

app = current_app


def create_from_file(file_path=None):
    """
    Import song and rating data from JSON file.

    :param file_path: full file path to JSON file
    :return: status: True if creation is done successfully
    """
    if file_path is None:
        raise ValueError("Require JSON file path")

    status = False
    with open(file_path) as json_file:
        data = json.load(json_file)
        app.logger.debug('== JSON data: %s', data)
        for one_row in data:
            app.logger.debug('one_row: %s', one_row)
            created_id = Rating().create(**one_row)

        status = True

    return status


class Rating(object):
    """
    Class object for managing rating songs

    """

    _mongo = None

    def __init__(self):
        """
        Initiate PyMongo object for the class
        """
        self._mongo = app.config['mongodb']

    def create(self, **kwargs):
        """
        Create rating object is ratings collection.

        :param kwargs: dictionary of rating data
        :return: res_dict: dictionary of created object id. created_id is the key
        """

        song_id = kwargs['song_id']
        rating_value = kwargs['rating']

        if song_id == '':
            raise ValueError("Empty string of song ID found")

        if rating_value == '':
            raise ValueError("Empty string of rating found")

        # app.logger.debug('Type of rating_value: %s', type(rating_value))
        self.validate_rating_value(rating_value)
        kwargs['rating'] = int(rating_value)

        kwargs['song_id'] = bson.ObjectId(str(song_id))
        kwargs['creation_date'] = datetime.datetime.utcnow()

        created_id = self._mongo.db.ratings.insert_one(kwargs).inserted_id
        created_id = str(created_id)
        return {"created_id": str(created_id)}

    def validate_rating_value(self, rating_value=None):
        """
        Validate given rating value. Possible values are: 1, 2, 3, 4 and 5

        :param rating_value: rating value
        :return: return True if validation is OK
        """

        valid_values = (1, 2, 3, 4, 5, "1", "2", "3", "4", "5")
        if rating_value not in valid_values:
            raise ValueError("Invalid rating value. Accepted values are 1, 2, 3, 4 and 5")

        return True

    def list_all(self):
        """
        Get all rating objects in ratings collection

        :return: data_dict: dictionary with 'total' and 'output' key. Row data can be found in 'output' key.
        """

        cursor = self._mongo.db.ratings.find()
        # app.logger.debug('cursor: %s', cursor)

        total_found = cursor.count()
        app.logger.debug('total_found: %s', total_found)

        output = []
        if total_found > 0:
            for document in cursor:
                app.logger.debug('document: %s', document)
                output.append(get_dict_data(document))

        return {'total': total_found, 'output': output}

    def get_stat(self, song_id=None):
        """
        Get statistic data for selected song id.

        :param song_id: string of song id
        :return: data_dict: dictionary with following keys:
                 'avg_value': average level value of the song
                 'min_value': minimum level value of the song
                 'max_value': maximum level value of the song
        """

        song_id = bson.ObjectId(str(song_id))

        cursor = self._mongo.db.ratings.aggregate([
            {'$match': {"song_id": song_id}},
            {
                '$group': {
                    '_id': None,
                    "avg_level": {'$avg': '$rating'},
                    "min_value": {'$min': '$rating'},
                    "max_value": {'$max': '$rating'}
                }
            }
        ])
        # app.logger.debug('== get_stat cursor: %s', cursor)

        avg_value = None
        min_value = None
        max_value = None
        for document in cursor:
            # app.logger.debug('== get_stat document: %s', document)
            avg_value = document["avg_level"]
            min_value = document["min_value"]
            max_value = document["max_value"]

        return {
            "avg_value": avg_value,
            "min_value": min_value,
            "max_value": max_value
        }

    def find_update(self, song_id=None, rating_value=None):
        """
        Update rating value of given song id. NOT IN USED!

        :param song_id: string of song id
        :param rating_value: rating value for updating
        :return: data_dict: dictionary with following keys:
                 'status': operation status
                 'output' updated row data
        """

        if song_id == '':
            raise ValueError("Empty string of song ID found")

        song_id = bson.ObjectId(str(song_id))
        cursor = self._mongo.db.ratings.find({"_id": song_id})
        # app.logger.debug('== cursor: %s', len(cursor))

        rating = None
        for document in cursor:
            # app.logger.debug('== add_rating document: %s', document)
            if 'rating' in document:
                rating = document['rating']
                if rating is None:
                    rating = 0
                rating += rating_value

        if rating is None:
            rating = rating_value

        app.logger.debug('rating: %s', rating)

        updated = self._mongo.db.ratings.update_one(
            {'_id': song_id},
            {
                '$set': {'rating': rating},
                '$currentDate': {'lastModified': True}
            }
        )
        # app.logger.debug('updated: %s', updated)
        app.logger.debug('updated: %s', updated.modified_count)

        songs = self._mongo.db.ratings.find_one({"_id": song_id})
        app.logger.debug('songs: %s', songs)
        item_dict = get_dict_data(songs)

        return {"status": updated.modified_count, "output": item_dict}
