from app.db.dependencies import get_db


def test_get_db_creates_and_closes_session():

    generator = get_db()

    db = next(generator)

    assert db is not None

    # Finish the generator.
    # This executes the finally block:
    # db.close()
    try:
        next(generator)
    except StopIteration:
        pass