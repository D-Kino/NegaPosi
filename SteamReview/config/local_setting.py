# ローカル環境
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "mysql://{user}:{password}@{host}:{port}/{db_name}".format(**{
    'user': 'root',
    'password': '',
    'host': 'localhost',
    "port": "3306",
    "db_name": "web_app"
})
SECRET_KEY = "secret key"
