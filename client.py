import asyncio
from aiohttp import ClientSession

async def main():
    async with ClientSession() as session:
        response = await session.post('http://127.0.0.1:8080/adverts/',
                                      json={
                                          "title": "Sell all sorts of stuff",
                                          "description": "all bullshit",
                                          "owner": "owner bullshit"
        })
        print(await response.json())

        response = await session.get('http://127.0.0.1:8080/adverts/1/')
        print(await response.json())

        # response = await session.delete('http://127.0.0.1:8080/adverts/1/')
        # print(await response.json())

asyncio.run(main())