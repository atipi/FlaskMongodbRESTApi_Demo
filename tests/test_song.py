import unittest

from api import create_app
from instance.song import Song


class TestSong(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_name="testing")
        cls.app.config["MONGO_DBNAME"] = "test_songs_db"
        cls.app.config["MONGO_URI"] = "mongodb://localhost:27017/test_songs_db"
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        """ Drop database after executed all test cases """

        with cls.app.app_context():
            Song(is_test_mode=1).drop_database()
            print('DROPPED database')

    def test_create(self):
        """
        Test creating data row to song collection
        :return:
        """
        params = {
            "artist": "Mr Fastfinger",
            "title": "Awaki-Waki",
            "difficulty": 15,
            "level": 13,
            "released": "2012-05-11"
        }
        created_id = None
        with self.app.app_context():
            created_id = Song().create(**params)
        print("Created row id ", created_id)
        self.assertIsNotNone(created_id)

    def test_delete(self):
        """
        Test deleting data row from song collection

        :return:
        """
        params = {
            "artist": "Mr Fastfinger",
            "title": "Awaki-Waki",
            "difficulty": 15,
            "level": 13,
            "released": "2012-05-11"
        }
        created_id = None
        status = False
        with self.app.app_context():
            created_id = Song(is_test_mode=1).create(**params)

            if created_id is not None:
                print('== created_id: %s', created_id)
                status = Song().delete(song_id=created_id)

        self.assertTrue(status)


if __name__ == '__main__':
    unittest.main(verbosity=2)
