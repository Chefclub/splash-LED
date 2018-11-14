import asyncio
import os

from aiohttp import web
import aioredis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))


async def bot_say_hook(request):
    loop = asyncio.get_event_loop()
    redis = await aioredis.create_redis(
        (REDIS_HOST, REDIS_PORT), db=REDIS_DB, loop=loop
    )

    data = await request.post()

    try:
        await redis.rpush("SPLASH_SCREEN", data["text"])
        return web.Response(text="Entendu")
    except KeyError:
        return web.json_response({"error": "Nothing"},
                                 status=400)


async def screen_get(request):
    loop = asyncio.get_event_loop()
    redis = await aioredis.create_redis(
        (REDIS_HOST, REDIS_PORT), db=REDIS_DB, loop=loop
    )

    result = await redis.lpop("SPLASH_SCREEN",
                              encoding="utf-8")
    if result:
        return web.json_response({"message": result})

    return web.json_response({"error": "Nothing"},
                             status=404)


app = web.Application()
app.add_routes([web.get('/bot', screen_get),
                web.post('/bot', bot_say_hook)])

web.run_app(app)
