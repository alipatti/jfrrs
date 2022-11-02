# TODO: init database and export connection object

import asyncio
import datetime
from pprint import pprint

from prisma import Prisma


async def main():
    db = Prisma()
    try:
        await db.connect()

        await db.meet.create(
            data={
                "idTFRRS": 521827728,
                "sport": "bcggadccgf",
                "location": "jdcfdcgc",
                "name": "cafdaehjid",
                "date": datetime.datetime.utcnow(),
            },
        )
        print("Successfully added meet!")

        meets = await db.meet.find_many()
        pprint(dict(meets[0]))

        await db.meet.delete(
            where={
                "idTFRRS": 521827728,
            }
        )

        print("Successfully deleted meet!")

    except Exception as e:
        print(e)
        print(e.with_traceback())
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())


# database_connection =
