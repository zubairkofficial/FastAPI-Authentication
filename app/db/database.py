from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# DATABASE = "postgresql://postgres:@localhost/Authentication"
# DATABASE = "mysql+pymysql://root:@localhost/voda"
DATABASE = "mysql+pymysql://x4zawqx5vogo2hjf:ojbobi918c7uhf2j@ofcmikjy9x4lroa2.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/img353tamn3ojf0t"
engine = create_engine(DATABASE, echo=True)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
