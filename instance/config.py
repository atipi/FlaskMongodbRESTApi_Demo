class BaseConfig(object):
    DEBUG = False
    TESTING = False
    MONGO_DBNAME = 'songs_db'
    MONGO_URI = 'mongodb://localhost:27017/songs_db'


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    MONGO_DBNAME = 'test_songs_db'
    MONGO_URI = 'mongodb://localhost:27017/test_songs_db'


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}