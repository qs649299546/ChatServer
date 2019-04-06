from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import MYSQL_SETTINGS


CONNECT_STRING = 'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}'

engine = create_engine(CONNECT_STRING.format(**MYSQL_SETTINGS), pool_recycle=3600)


# MySQL
DB_Session = sessionmaker(bind=engine)
