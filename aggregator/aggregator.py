import asyncio
import async_timeout
import aiohttp
import feedparser
from sqlalchemy import create_engine

# from sqlalchemy import text
from sqlalchemy import select
from sqlalchemy import engine
from utils import create_table
import os


class FeedLinkError(Exception):
    pass


async def fetch(session: aiohttp.ClientSession, feed_url: str) -> dict:
    with async_timeout.timeout(10):
        async with session.get(feed_url) as response:
            return await response.text()


def feeds() -> engine.row.LegacyRow:
    engine = create_engine("sqlite+pysqlite:///test.db", echo=True)
    stmt = select(create_table.url_table.c.url)
    with engine.connect() as conn:
        # result = conn.execute(text("select url from rss_feeds"))
        result = conn.execute(stmt)
        for link in result:
            yield link


def is_rss_valid(rss: feedparser.util.FeedParserDict) -> bool:
    return not rss.bozo


async def main() -> int:
    async with aiohttp.ClientSession() as session:

        for feed in feeds():
            html = await fetch(session, feed.url)
            rss = feedparser.parse(html)

            if not is_rss_valid(rss):
                raise FeedLinkError(f"{feed.url} is not a valid rss feed!")

            # print(rss.feed.title)
            # print(rss.feed.description)
            # print("---------------------")
            # for entry in rss.entries:
            #     print(f"{entry.title} -> {entry.links[0]['href']}")
            #     print()
    return 0


if __name__ == "__main__":
    print(os.getcwd)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
