import asyncio
import async_timeout
import aiohttp
import feedparser
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy import engine
from utils import create_table
import os
import pymongo

# import time

URL_DATABASE = os.getenv("URL_DATABASE", default="sqlite+pysqlite:///test.db")
ARTICLES_DATABASE = os.getenv(
    "ARTICLES_DATABASE", default="mongodb://localhost:27017/"
)


class FeedLinkError(Exception):
    pass


async def fetch(session: aiohttp.ClientSession, feed_url: str) -> dict:
    with async_timeout.timeout(10):
        async with session.get(feed_url) as response:
            return await response.text()


def feeds() -> engine.row.LegacyRow:
    engine = create_engine(URL_DATABASE, echo=True)
    stmt = select(create_table.url_table.c.url)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        for link in result:
            yield link


def is_rss_valid(rss: feedparser.util.FeedParserDict) -> bool:
    return not rss.bozo


async def save_articles(collection, rss: dict) -> None:
    blog = {
        "blog-title": rss.feed.title,
        "blog-description": rss.feed.description,
        "blog-entries": [
            {
                "entrie-title": e.title,
                "entrie-url": e.links[0]["href"],
                "uid": e.guid,
            }
            for e in rss.entries
        ],
    }
    if collection.find_one({"blog-title": rss.feed.title}):
        collection.find_one_and_replace({"blog-title": rss.feed.title}, blog)
    else:
        collection.insert_one(blog)


async def main() -> int:
    async with aiohttp.ClientSession() as session:
        client = pymongo.MongoClient(ARTICLES_DATABASE)
        db = client.articles
        articles = db["articles"]
        for feed in feeds():
            html = await fetch(session, feed.url)
            rss = feedparser.parse(html)

            if not is_rss_valid(rss):
                # raise FeedLinkError(f"{feed.url} is not a valid rss feed!")
                print(f"{feed.url} is not a valid rss feed!")
            else:
                await save_articles(articles, rss)

    return 0


if __name__ == "__main__":
    print(ARTICLES_DATABASE)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

# docker run --name Aggregator --rm -p 8000:5000 --link mongodb:dbserver \
#   -e ARTICLES_DATABASE=mongodb://172.17.0.2:27017/ aggregator:latest
