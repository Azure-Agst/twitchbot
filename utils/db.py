import sqlite3

# Static
db_path = None


def get_db():
    """Gets an initialized DB object"""

    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    return db


def init_db(path: str):
    """Initializes database"""

    global db_path
    db_path = path

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS " +
        "twitch_token(type, access, expires, refresh)"
    )
    db.commit()

    return db


def set_token(data: dict):
    """Sets the row accordingly to the parsed JSON passed in"""

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO "
        "twitch_token(type, access, expires, refresh) "
        "values (?, ?, ?, ?)",
        ('bearer', data['access_token'], data['expires_in'], data['refresh_token'])
    )
    db.commit()


def get_token():
    """Fetches row from DB"""

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM twitch_token")
    return cur.fetchone()


def clear_token():
    """Deletes row from DB"""

    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM twitch_token")
    db.commit()
