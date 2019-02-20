import unittest
import json
import os

from api import create_app
from instance.song import Song, create_from_file
from instance.rating import create_from_file as create_ratings_from_file


class TestSongApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Import test data set before running test cases

        :return:
        """

        cls.app = create_app(config_name="testing")
        cls.app.config["MONGO_DBNAME"] = "test_songs_db"
        cls.app.config["MONGO_URI"] = "mongodb://localhost:27017/test_songs_db"
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            dbnames_list = Song().get_dbnames()
            if len(dbnames_list) == 0:
                SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
                json_url = os.path.join(SITE_ROOT, "test_songs.json")
                print('== json_url: %s', json_url)
                create_from_file(file_path=json_url)

    @classmethod
    def tearDownClass(cls):
        """ Drop database after executed all test cases """

        with cls.app.app_context():
            Song().drop_database()
            # print('DROPPED database')

    def test_add_song_invalid_operation(self):
        response = self.client.get('/songs/add')
        # print("Response test_add_song_invalid_operation: ", response)
        json_data = response.get_json(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data['error_message'], "Operation is not allowed")

    def test_add_song(self):
        params_dict = {
            "artist": "The Yousicians",
            "title": "Wishing In The Night",
            "difficulty": 10.98,
            "level": 9,
            "released": "2016-01-01"
        }
        response = self.client.post('/songs/add',
                                    data=json.dumps(params_dict),
                                    content_type='application/json')
        # print("Response test_add_song: ", response)
        json_data = response.get_json()
        # print("Response test_add_song: ", json_data)
        created_id = json_data['created_id']
        created_ok = False
        if created_id != '':
            created_ok = True
        self.assertTrue(created_ok)

    def test_list_all_songs(self):
        response = self.client.get('/songs')
        # print("Response test_list_all_songs", response.data)
        json_data = response.get_json()
        # print("Response test_list_all_songs: ", json_data)
        total = json_data['total']
        self.assertTrue(total > 0)

    def test_list_songs_pagination(self):
        response = self.client.get('/songs?limit=1&page=1')
        status_code = response.status_code
        # print("test_list_songs_pagination - status_code: ", status_code)
        # print("Response test_list_songs_pagination", response.data)
        self.assertEqual(status_code, 200)

    def test_search_by_level_missing_params(self):
        response = self.client.get('/songs/avg/difficulty')
        # print("Response test_search_by_level_missing_params: ", response)
        # print("Response test_search_by_level_missing_params: ", response.status_code)
        json_data = response.get_json(response.data)
        # print("Response test_search_by_level_missing_params: ", json_data['error_message'])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data['error_message'], "Missing level parameter")

    def test_search_by_level_invalid_params(self):
        response = self.client.get('/songs/avg/difficulty?level=a')
        json_data = response.get_json(response.data)
        # print("Response test_search_by_level_invalid_params: ", json_data['error_message'])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data['error_message'], "Except numeric value for level parameter")

    def test_search_by_level(self):
        response = self.client.get('/songs/avg/difficulty?level=9')
        json_data = response.get_json()
        # print("Response test_search_by_level: ", json_data)
        result_list = json_data['result']
        avg_value = json_data['avg_value']
        self.assertIsNotNone(avg_value)
        self.assertIsNotNone(result_list)
        self.assertTrue(len(result_list) > 0)

    def test_search_song_missing_params(self):
        response = self.client.get('/songs/search')
        self.assertEqual(response.status_code, 404)
        json_data = response.get_json(response.data)
        self.assertEqual(json_data['error_message'], "Missing message parameter")

    def test_search_song(self):
        response = self.client.get('/songs/search?message=night')
        json_data = response.get_json()
        # print("Response test_search_song: ", json_data)

    def test_rate_song_missing_song_id_params(self):
        params_dict = {
            "artist": "The Yousicians",
        }
        response = self.client.post('/songs/rating',
                                    data=json.dumps(params_dict),
                                    content_type='application/json')
        json_data = response.get_json(response.data)
        # print("test_rate_song_missing_song_id_params error message: ", json_data['error_message'])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data['error_message'], "Missing song id parameter")

    def test_rate_song_missing_rating_params(self):
        params_dict = {
            "song_id": "5c6c4b562e48ae1c0f1a6d8a",
        }
        response = self.client.post('/songs/rating',
                                    data=json.dumps(params_dict),
                                    content_type='application/json')
        json_data = response.get_json(response.data)
        # print("test_rate_song_missing_rating_params error message: ", json_data['error_message'])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data['error_message'], "Missing rating parameter")

    def test_rate_song_invalid_rating_value(self):
        params_dict = {
            "song_id": "5c6c4b562e48ae1c0f1a6d8a",
            "rating": 6
        }
        response = self.client.post('/songs/rating',
                                    data=json.dumps(params_dict),
                                    content_type='application/json')
        json_data = response.get_json(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data['error_message'], "Invalid rating value. Accepted values are 1, 2, 3, 4 and 5")

    def test_rate_song(self):
        params_dict = {
            "artist": "The Yousicians",
            "title": "Greasy Fingers - boss level",
            "difficulty": 2,
            "level": 3,
            "released": "2016-03-01"
        }
        res_create = self.client.post('/songs/add',
                                      data=json.dumps(params_dict),
                                      content_type='application/json')
        json_data_create = res_create.get_json()
        created_id = json_data_create['created_id']
        # print("Response test_rate_song - created_id: ", created_id)

        json_data_rate = None
        if created_id is not None and created_id != '':
            rate_params_dict = {
                "song_id": "5c6c4b562e48ae1c0f1a6d8a",
                "rating": 3
            }
            res_rate = self.client.post('/songs/rating',
                                        data=json.dumps(rate_params_dict),
                                        content_type='application/json')
            json_data_rate = res_rate.get_json()

        # print("Response test_rate_song - json_data_rate: ", json_data_rate)
        self.assertIsNotNone(json_data_rate)

        created_rate_id = json_data_rate['created_id']
        self.assertIsNotNone(created_rate_id)

    def test_get_stat_rating(self):
        with self.app.app_context():
            SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
            json_url = os.path.join(SITE_ROOT, "test_stat_rating_songs.json")
            # print('== json_url: %s', json_url)
            create_ratings_from_file(file_path=json_url)

        response = self.client.get('/songs/avg/rating/5c6c4b562e48ae1c0f1a6d8a')
        # print("Response test_list_all_songs", response.data)
        json_data = response.get_json()
        # print("Response test_get_stat_rating: ", json_data)
        self.assertIsNotNone(json_data['avg_value'])
        self.assertIsNotNone(json_data['min_value'])
        self.assertIsNotNone(json_data['max_value'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
