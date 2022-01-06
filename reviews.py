from typing import List
from typing import NamedTuple
from typing import Optional

import db


class Review(NamedTuple):
    """The structure of the review added to the database"""
    id: Optional[int]
    from_id: int
    user_id: int
    message: str


def add_review(user_id: int, from_id: int, message: str) -> None:
    """Fills user feedback in the database"""
    cursor = db.get_cursor()
    cursor.execute("INSERT INTO review (from_id, user_id, message) "
                   f"VALUES ({from_id}, {user_id}, '{message}') ")
    db.conn.commit()


def get_reviews(user_id: int) -> List[Review]:
    """Returns a list of reviews from the database"""
    cursor = db.get_cursor()
    cursor.execute(f"SELECT * FROM review WHERE user_id = {user_id}")
    rows = cursor.fetchall()
    reviews = [
        Review(
            id=row[0],
            from_id=row[1],
            user_id=row[2],
            message=row[3]
        ) for row in rows]
    return reviews


def delete_review(review_id: int):
    """Removes feedback from the database"""
    cursor = db.get_cursor()
    cursor.execute(f"DELETE from review where id={review_id}")
    db.conn.commit()
