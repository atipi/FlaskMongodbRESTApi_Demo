# -*- coding: utf-8 -*-

__version__ = '0.1.0'
__author__ = 'Porntip Chaibamrung'


import bson
from flask import json, current_app

app = current_app


def create_from_file(file_path=None):
    """
    Import song data from JSON file.

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
            Song().create(**one_row)

        status = True
    return status


def convert_to_list(listItem=None):
    """
    Convert data to list

    :param listItem: list of items for converting
    :return: list: list of valid dictionary data
    """
    output = []
    for s_dict in listItem:
        item_dict = get_dict_data(s_dict)
        output.append(item_dict)

    # app.logger.debug('== output: %s', output)
    return output


def get_dict_data(data_dict=None):
    """
    Replace ObjectId to string data type inside dictionary

    :param data_dict: dictionary data for converting
    :return: item_dict: formatted dictionary data
    """

    item_dict = {}
    for key in data_dict:
        if key == '_id' or key == 'song_id':
            item_dict[key] = str(data_dict['_id'])
        else:
            item_dict[key] = data_dict[key]
    return item_dict


class Song(object):
    """
    Class object for song management

    """
    _mongo = None

    def __init__(self):
        """
        Initiate PyMongo object for the class
        """

        self._mongo = app.config['mongodb']

    def get_dbnames(self):
        """
        Get all collection names inside the database

        :return: dbnames_list: list of collection names
        """

        dbnames_list = self._mongo.db.list_collection_names()
        app.logger.debug('== dbnames_list: %s', dbnames_list)
        app.logger.debug('== dbnames_list: %s', len(dbnames_list))
        return dbnames_list

    def drop_database(self):
        """
        Drop database

        :return:
        """
        self._mongo.db.command("dropDatabase")

    def create(self, **kwargs):
        """
        Add row to songs collection.

        :param kwargs: dictionary of data
        :return: created_id: string of created object id
        """
        app.logger.debug('CREATE args: %s', kwargs)
        created_id = self._mongo.db.songs.insert_one(kwargs).inserted_id
        created_id = str(created_id)
        app.logger.debug('created_id: %s', created_id)
        return created_id

    def get_doc_from_cursor(self, cursor=None):
        """
        Get document from cursor object.

        :param cursor:
        :return:
        """
        for document in cursor:
            # app.logger.debug('== document: %s', document)
            return document

    def list_all(self):
        """
        List all rows in songs collection

        :return: list: list of dictionary data of a song
        """

        songs = self._mongo.db.songs
        # app.logger.debug('songs: %s', songs)
        output = convert_to_list(songs.find())
        return output

    def list(self, page_size=1, page_number=None):
        """
        List data rows from songs collection or certain set of data with pagination.

        :param page_size: number of row per page
        :param page_number: page number for displaying
        :param skip_value: number of row for jumping
        :return: list: list of dictionary data of a song
        """
        songs = None
        if page_number == 1:
            songs = self._mongo.db.songs.find().limit(int(page_size))
        else:
            if page_number > 1:
                next_skip = ( int(page_size) * int(page_number) ) - 1
                songs = self._mongo.db.songs.find().skip(next_skip).limit(int(page_size))

        output = convert_to_list(songs)
        return output

    def search_by(self, key_search=None):
        """
        Search songs by given artist name or title string.

        :param key_search: string for searching
        :return: list: list of dictionary data of a song
        """
        app.logger.debug('key_search: %s', key_search)
        songs = self._mongo.db.songs.find({'$or': [
            {'artist': {'$regex': key_search, '$options': 'i'}},
            {'title': {'$regex': key_search, '$options': 'i'}}]})

        output = convert_to_list(songs)
        return output

    def search_by_level(self, level_value=None):
        """
        Search songs by level value.

        :param level_value: integer value of level for searching
        :return: list: list of dictionary data of a song
        """
        songs = self._mongo.db.songs.find({"level": int(level_value)})

        output = convert_to_list(songs)
        return output

    def get_average_level(self):
        """
        Get average level of all songs

        :return: float value of average level value
        """
        cursor = self._mongo.db.songs.aggregate([
            {
                '$group': {
                    '_id': "$id",
                    "avg_level": {'$avg': '$level'}
                }
            }
        ])
        # app.logger.debug('== get_average_level cursor: %s', cursor)

        avg_value = None
        for document in cursor:
            # app.logger.debug('== get_average_level document: %s', document)
            avg_value = document["avg_level"]

        return float(avg_value)

    def get_average_difficulty(self):
        """
        Get average difficulty value of all songs

        :return: float value of average difficulty value
        """
        cursor = self._mongo.db.songs.aggregate([
            {
                '$group': {
                    '_id': "$id",
                    "avg_level": {'$avg': '$difficulty'}
                }
            }
        ])
        # app.logger.debug('== get_average_difficulty cursor: %s', cursor)

        avg_value = None
        for document in cursor:
            # app.logger.debug('== get_average_difficulty document: %s', document)
            avg_value = document["avg_level"]

        return float(avg_value)

    def delete(self, song_id=None):
        """
        Delete a row from songs collection.

        :param song_id: string of song object id
        :return: status: boolean value of operation status
        """
        if song_id is None:
            raise ValueError("Missing song_id parameter")

        song_id = bson.ObjectId(str(song_id))

        # db_response contains DeleteResult object
        db_response = self._mongo.db.songs.delete_one({'_id': song_id})

        app.logger.debug('DELETE - db_response count: %s', db_response.deleted_count)
        if db_response.deleted_count == 1:
            return True
        else:
            return False
