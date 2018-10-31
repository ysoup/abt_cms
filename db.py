from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://discuz:Aibitou.88@sql.aibilink.com:3306/new_flash?charset=utf8", max_overflow=0, pool_size=5)
Session = sessionmaker(bind=engine)

session_conn = Session()