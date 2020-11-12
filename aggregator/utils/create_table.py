from sqlalchemy import create_engine

# from sqlalchemy import text
from sqlalchemy import insert
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


URL_FEEDS = [
    "https://www.lemonde.fr/rss/une.xml",
    "https://korben.info/feed",
    "https://www.lemonde.fr/pixels/rss_full.xml",
    "https://www.lemonde.fr/sciences/rss_full.xml",
    "https://www.computer.org/category/tech-news-post/feed/",
    "https://www.lemonde.fr/",
]

metadata = MetaData()

url_table = Table(
    "rss_feeds",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("url", String),
)

if __name__ == "__main__":
    # engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
    engine = create_engine("sqlite+pysqlite:///../test.db", echo=True)
    metadata.create_all(engine)
    with engine.connect() as conn:
        # conn.execute(text("create table rss_feeds (url text)"))
        conn.execute(
            # text("insert into rss_feeds (url) values (:url)"),
            insert(url_table),
            [{"url": url} for url in URL_FEEDS],
        )
        # conn.commit()
