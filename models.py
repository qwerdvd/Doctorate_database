from constants import CONFIG_PATH
from sqlalchemy import create_engine, Column, Integer, String, JSON, Text
from sqlalchemy.ext.declarative import declarative_base

from utils import read_json

database_config = read_json(CONFIG_PATH)["database"]

engine = create_engine(
    f"mysql+pymysql://{database_config['user']}:{database_config['password']}@{database_config['host']}:{database_config['port']}/DoctoratePy1"
)
Base = declarative_base()


class AccountTable(Base):
    __tablename__ = 'account'
    __mysql_engine__ = 'InnoDB'
    __mysql_charset__ = 'utf8mb4'
    __mysql_collate__ = 'utf8mb4_bin'

    uid = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(255, collation='utf8mb4_bin'), nullable=True)
    password = Column(String(255, collation='utf8mb4_bin'), nullable=True)
    secret = Column(String(255, collation='utf8mb4_bin'), nullable=True)
    user = Column(JSON, default=[])
    mails = Column(JSON, nullable=True)
    assistCharList = Column(JSON, nullable=True)
    friend = Column(JSON, nullable=True)
    ban = Column(Integer, nullable=True, default=None)


class MailTable(Base):
    __tablename__ = 'mail'

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", Text, nullable=True)
    sender = Column("from", Text, nullable=True)
    subject = Column("subject", Text, nullable=True)
    content = Column("content", Text, nullable=True)
    items = Column("items", JSON, nullable=True)
