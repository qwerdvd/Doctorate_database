import json
from typing import List

from Account import Account, UserInfo
from Search import SearchAssistCharList, SearchUidList
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import AccountTable, MailTable


class SQLA:
    def __init__(self, url: str):
        self.engine = create_engine(f"mysql+pymysql://{url}")
        AccountTable.__table__.create(bind=self.engine, checkfirst=True)
        MailTable.__table__.create(bind=self.engine, checkfirst=True)
        self.session = sessionmaker(bind=self.engine)

    def query_account_by_secret(self, secret: str) -> List[Account]:
        with self.session() as session:
            return session.query(AccountTable).filter_by(secret=secret).all()

    def query_account_by_phone(self, phone: str) -> List[Account]:
        with self.session() as session:
            return session.query(AccountTable).filter_by(phone=phone).all()

    def query_account_by_uid(self, uid: int) -> List[Account]:
        with self.session() as session:
            return session.query(AccountTable).filter_by(uid=uid).all()

    def query_nick_name(self, nick_name: str) -> List:
        with self.session() as session:
            result = session.query(
                AccountTable.uid
            ).from_(
                AccountTable
            ).where(
                AccountTable.user['status']['nickName'] == nick_name
            ).all()
            return result

    def query_user_info(self, uid: int) -> List[UserInfo]:
        with self.session() as session:
            result = session.query(
                AccountTable.uid,
                AccountTable.user['status'].label('status'),
                AccountTable.user['troop']['chars'].label('chars'),
                AccountTable.user['social']['assistCharList'].label('social_assist_char_list'),
                AccountTable.assistCharList.label('assist_char_list'),
                AccountTable.friend
            ).from_(
                AccountTable
            ).where(
                AccountTable.uid == uid
            ).all()
            return result

    def search_player(self, nick_name: str, nick_number: str) -> List[SearchUidList]:
        with self.session() as session:
            result = session.query(
                AccountTable.uid,
                AccountTable.user['status']['level'].label('level'),
            ).from_(
                AccountTable
            ).where(
                AccountTable.user['status']['nickName'].like(f"%{nick_name}%")
            ).where(
                AccountTable.user['status']['nickNumber'].like(f"%{nick_number}%")
            ).all()
            return result

    def search_assist_char_list(self, profession: str) -> List[SearchAssistCharList]:
        with self.session() as session:
            result = session.select(
                AccountTable.uid,
                AccountTable.user['status'].label('status'),
                AccountTable.user['troop']['chars'].label('chars'),
                AccountTable.user['social']['assistCharList'].label('social_assist_char_list'),
                AccountTable.assistCharList[profession].label('assist_char_list'),
            ).from_(
                AccountTable
            ).where(
                AccountTable.assistCharList[profession].isnot(None)
            ).all()
            return result

    def register_account(self, phone: str, password: str, secret: str) -> tuple:
        with self.session() as session:
            new_account = AccountTable(
                phone=phone,
                password=password,
                secret=secret,
                user={},
                mails=[],
                assistCharList={},
                friend={"list": [], "request": []},
                ban=0
            )
            session.add(new_account)
            session.commit()
            return new_account.uid, new_account.secret

    def login_account(self, phone: str, password: str) -> List[Account]:
        with self.session() as session:
            return session.query(
                AccountTable
            ).filter_by(
                phone=phone,
                password=password
            ).all()

    def set_password(self, secret: str, password: str) -> int:
        with self.session() as session:
            result = session.query(
                AccountTable
            ).filter_by(
                secret=secret
            ).update(
                password=password
            )
            session.commit()
            return result

    def set_phone(self, secret: str, phone: str, new_secret: str) -> int:
        with self.session() as session:
            result = session.query(
                AccountTable
            ).filter_by(
                secret=secret
            ).update(
                phone=phone,
                secret=new_secret
            )
            session.commit()
            return result

    def set_user_data(self, uid: int, user_data: dict) -> int:
        with self.session() as session:
            result = session.query(
                AccountTable
            ).filter_by(
                uid=uid
            ).update(
                user=json.dumps(user_data, ensure_ascii=False)
            )
            session.commit()
            return result

    def set_friend_data(self, uid: int, friend_data: dict) -> int:
        with self.session() as session:
            account = session.query(
                AccountTable
            ).filter_by(
                uid=uid
            ).update(
                json.dumps(friend_data, ensure_ascii=False)
            )
            session.commit()
            return account.rowcount

    def set_assist_char_list_data(self, uid: int, assist_char_list: dict) -> int:
        with self.session() as session:
            account = session.query(
                AccountTable
            ).filter_by(
                uid=uid
            ).update(
                json.dumps(assist_char_list, ensure_ascii=False)
            )
            session.commit()
            return account.rowcount

    def set_user_status(self, uid: int, ban: int) -> int:
        with self.session() as session:
            account = session.query(
                AccountTable
            ).filter_by(
                uid=uid
            ).update(
                ban=ban
            )
            session.commit()
            return account.rowcount

    def delete_account(self, uid: int) -> int:
        with self.session() as session:
            result = session.where(
                AccountTable.uid == uid
            ).delete()
            session.commit()
            return result.rowcount

    def table_exists(self, table_name: str) -> bool:
        with self.session() as session:
            result = session.show_tables_like(table_name).execute()
            return result


def create_sqla(url: str) -> SQLA:
    return SQLA(url)


def init_db(url):
    connection = create_engine(f"mysql+pymysql://{url}").connect()
    # 创建数据库
    connection.execute("CREATE DATABASE IF NOT EXISTS DoctoratePy1;")
    connection.execute("USE DoctoratePy1;")
    # 关闭连接
    connection.close()


if __name__ == '__main__':
    from constants import CONFIG_PATH
    from utils import read_json

    database_config = read_json(CONFIG_PATH)["database"]
    user = database_config["user"]
    password = database_config["password"]
    host = database_config["host"]
    port = database_config["port"]
    database = 'DoctoratePy1'
    init_db(
        f"{user}:{password}@{host}:{port}"
    )
    sql = create_sqla(
        f"{user}:{password}@{host}:{port}/{database}"
    )
    sync = read_json("syncData.json")
    # sql.register_account('4', '5', '6')
    # sql.set_user_data(10, sync)
    # sql.set_phone('10', '15', '15')
    # result = sql.query_user_info(10)
    # print(result)
