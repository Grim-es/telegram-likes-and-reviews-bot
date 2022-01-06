from typing import List
from typing import NamedTuple
from typing import Union

import db


class User(NamedTuple):
    """The structure of the user added to the database"""
    id: int
    name: str
    last_name: str
    phone_number: str
    photo: Union[bytes, None]


def add_user(user_id: int, name: str, last_name: str, phone_number: str, photo: str) -> None:
    cursor = db.get_cursor()
    cursor.execute("INSERT INTO user (id, name, last_name, phone_number, photo) "
                   f"VALUES (?, ?, ?, ?, ?)", (user_id, name, last_name, phone_number, photo))
    db.conn.commit()


def get_users(args: List[str]) -> List[User]:
    """Returns a list of found users from the database by search criteria"""
    query = _parse_query_values(args)
    cursor = db.get_cursor()
    cursor.execute(f"SELECT * FROM user WHERE {query}")
    rows = cursor.fetchall()
    users = [
        User(
            id=row[0],
            name=row[1],
            last_name=row[2],
            phone_number=row[3],
            photo=row[4]
        ) for row in rows]
    return users


def get_user(user_id: int) -> Union[User, None]:
    """Returns the user by id from the database"""
    cursor = db.get_cursor()
    cursor.execute(f"SELECT * FROM user WHERE id = {user_id}")
    result = cursor.fetchone()
    if not result:
        return
    user = User(
        id=result[0],
        name=result[1],
        last_name=result[2],
        phone_number=result[3],
        photo=result[4]
    )
    return user


def _parse_query_values(args: List[str]) -> str:
    """Parses the arguments of the received message into the text of the request to the database"""
    query = [f"'{arg}' IN (name, last_name)" for arg in args]
    return ' OR '.join(query)
