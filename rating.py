from typing import List
from typing import NamedTuple

import db


class Rate(NamedTuple):
    """The structure of the review added to the database """
    from_id: int
    user_id: int
    likes: int
    dislikes: int


def update_rating(user_id: int, from_id: int, rate: bool) -> None:
    """Puts Like or Dislike depending on the rate parameter"""
    cursor = db.get_cursor()
    likes, dislikes = (int(rate), int(not rate))
    cursor.execute("INSERT INTO rating (from_id, user_id, likes, dislikes) "
                   f"VALUES ({from_id}, {user_id}, {likes}, {dislikes}) "
                   "ON CONFLICT (from_id) DO "
                   f"UPDATE SET likes = {likes}, dislikes = {dislikes}")
    db.conn.commit()


def get_user_rating(user_id: int) -> List[Rate]:
    """Returns a list of grades from the database"""
    cursor = db.get_cursor()
    cursor.execute(f"SELECT * FROM rating WHERE user_id = {user_id}")
    rows = cursor.fetchall()
    rates = [
        Rate(
            from_id=row[0],
            user_id=row[1],
            likes=row[2],
            dislikes=row[3]
        ) for row in rows]
    return rates
