# -*- coding: utf-8 -*-

__version__ = '0.1.0'
__author__ = 'Porntip Chaibamrung'

import re
from flask import jsonify, current_app
from flask_restful import request, abort, Resource
from instance.song import Song
from instance.rating import Rating

app = current_app


class BaseResource(Resource):
    """
    Base class for end points if we want to pass additional parameters when defining end points.

    """
    _is_test_mode = 0

    def __init__(self, **kwargs):
        # app.logger.debug('Arguments kwargs in __init__: %s', kwargs)
        config_name = kwargs['config_name']
        if config_name == 'testing':
            self._is_test_mode = 1


class AddSong(BaseResource):
    """
    Class object for adding songs end point

    """

    def post(self):
        """
        Handler function for adding song data.

        :return:
        """
        data = request.get_json()
        app.logger.debug('Post JSON data from request: %s', data)

        created_id = Song().create(**data)
        return {"created_id": created_id}

    @staticmethod
    def get():
        abort(404, error_message='Operation is not allowed')


class ListSong(BaseResource):
    """
    Class object of listing songs end point

    """

    def get(self):
        """
        Main function to fetch list of song by 'limit' and 'page' parameter.
        If no parameter given then list all songs

        :return: data_dict: dictionary with following keys:
                 'result':  rows data
                 'total': total number of found items
        """

        args = request.args  # retrieve args from query string
        app.logger.debug('Arguments from request: %s', args)

        page_size = args.get("limit", None)
        page_number = args.get("page", None)

        show_all = 1
        if page_size is not None:
            if page_size == '':
                raise ValueError('Value in limit parameter cannot be empty string')

            show_all = 0
            page_size = int(page_size)

        if page_number is None or page_number == '':
            page_number = 1
        else:
            page_number = int(page_number)

        if page_number <= 0:
            page_number = 1

        if show_all:
            output = Song().list_all()
        else:
            output = Song().list(page_size=page_size, page_number=page_number)

        return jsonify({'result': output, 'total': len(output)})

    @staticmethod
    def post():
        abort(404, error_message='Operation is not allowed')


class ListSongByLevel(BaseResource):
    """
    Class object for searching songs by level value end point.

    """

    def get(self):
        """
        Main function to search songs by given level value and returns the average difficulty for all songs

        :method: GET
        :return: data_dict: dictionary with following keys:
                 'total': total number of found songs
                 'avg_value': the average difficulty value for all songs
                 'result': list of found songs
        """

        args = request.args
        level = args.get("level", None)

        if level is None:
            abort(404, error_message='Missing level parameter')

        is_match = re.match('\d', level)
        if not is_match:
            abort(404, error_message='Except numeric value for level parameter')

        output = Song().search_by_level(level_value=level)
        avg_value = Song().get_average_difficulty()

        total_item = 0
        if output is not None:
            total_item = len(output)

        return jsonify({'total': total_item, 'avg_value': avg_value, 'result': output})

    @staticmethod
    def post():
        abort(404, error_message='Operation is not allowed')


class SearchSong(BaseResource):
    """
    Class object for searching song by keyword's end point

    """

    def get(self):
        """
        Main function to search songs by keywords.

        :return: data_dict: dictionary with following keys:
                 'total': total number of found songs
                 'result': list of dictionary of song data
        """
        args = request.args
        message = args.get("message", None)

        if message is None or message == '':
            abort(404, error_message='Missing message parameter')

        output = Song().search_by(key_search=message)

        total_item = 0
        if output is not None:
            total_item = len(output)

        return jsonify({'total': total_item, 'result': output})

    @staticmethod
    def post():
        abort(404, error_message='Operation is not allowed')


class RateSong(BaseResource):
    """
    Class object for rating a song's end point.

    """

    def post(self):
        """
        Main function to rate a song with 'song_id' and 'rating' parameter.

        :return: dictionary of create rating object.
        """

        data = request.get_json()
        app.logger.debug('Arguments from request: %s', data)

        song_id = data.get("song_id", None)
        rating = data.get("rating", None)

        if song_id is None:
            abort(404, error_message='Missing song id parameter')

        if rating is None:
            abort(404, error_message='Missing rating parameter')

        result = {}
        try:
            req_dict = {
                'song_id': song_id,
                'rating': rating
            }
            result = Rating().create(**req_dict)
        except Exception as e:
            app.logger.debug('Error: %s', e)
            abort(404, error_message='{}'.format(e))

        return jsonify(result)

    @staticmethod
    def get():
        abort(404, error_message='Operation is not allowed')


class ListRating(BaseResource):
    """
    Class object for listing rating objects end point.

    """

    def get(self):
        """
        Main function to list rating object

        :return:
        """
        result_dict = Rating().list_all()
        return jsonify(result_dict)

    @staticmethod
    def post():
        abort(404, error_message='Operation is not allowed')


class GetStatRating(BaseResource):
    """
    Class object for getting statistic data of selected song id.

    """

    def get(self, song_id):
        """

        :param song_id: string of song id
        :return: see get_stat() function in Rating class
        """
        # app.logger.debug('request: %s', request)
        app.logger.debug('song_id: %s', song_id)

        result = Rating().get_stat(song_id)
        return result

    @staticmethod
    def post():
        abort(404, error_message='Operation is not allowed')
