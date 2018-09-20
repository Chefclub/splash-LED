#!/usr/bin/env python3
# git@github.com:Chefclub/splash-LED.git
import asyncio
import aioredis
import random
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions

COLORS = [
    (51, 255, 73),  # Vert
    (230, 255, 51),  # Jaune
    (255, 134, 51),  # Orange Chefclub Kids
    (255, 51, 51),  # Rouge Flag
    (51, 255, 252),  # Bleu Chefclub Light & Fun
    (255, 249, 51),  # Jaune Chefclub Cocktails
    (255, 51, 119),  # Rouge Chefclub Originals
    (255, 255, 255),  # Blanc
    (216, 53, 162),  # Pink Chefclub Girls
    (61, 69, 163),  # Bleu Flag
]

MAX_WIDTH = 192


def write_message(double_buffer, font, color, initX, y, message):
    for i in range(3):
        for x in range(MAX_WIDTH, initX, -1):
            graphics.DrawText(double_buffer, font, x, y, color, message)
            yield


async def produce(queue):
    redis = await aioredis.create_redis_pool(('localhost', 6379))

    while True:
        info = await redis.blpop("SLACK_CHANNEL", encoding='utf-8', timeout=10)
        if info:
            await queue.put(info[1])


async def consume(queue, matrix):
    # Add double_buffer
    double_buffer = matrix.CreateFrameCanvas()
    matrix.SwapOnVSync(double_buffer)

    # Init font
    font = graphics.Font()
    font.LoadFont("../../../fonts/10x20.bdf")

    # Init Colors
    colors = [graphics.Color(*c) for c in COLORS]
    print("Loaded")
    # wait for an item from the producer
    message1 = await queue.get()
    message2 = await queue.get()

    initX1 = -len(message1) * 10
    line1 = iter(
        write_message(double_buffer, font, random.choice(colors), initX1, 12, message1)
    )
    initX2 = -len(message2) * 10
    line2 = iter(
        write_message(double_buffer, font, random.choice(colors), initX2, 29, message2)
    )
    while True:
        double_buffer.Clear()
        try:
            next(line1)
        except StopIteration:
            message1 = await queue.get()
            initX1 = -len(message1) * 10
            line1 = iter(write_message(double_buffer, font, random.choice(colors), initX1, 15, message1))
        try:
            next(line2)
        except StopIteration:
            message2 = await queue.get()
            initX2 = -len(message2) * 10
            line2 = iter(write_message(double_buffer, font, random.choice(colors), initX2, 31, message2))
        matrix.SwapOnVSync(double_buffer)
        await asyncio.sleep(0.02)


if __name__ == "__main__":
    # Init matrix
    options = RGBMatrixOptions()
    options.rows = 32
    options.chain_length = 6
    options.disable_hardware_pulsing = 0
    options.gpio_slowdown = 1
    options.brightness = 100
    options.pwm_bits = 11

    # Matrix
    matrix = RGBMatrix(options=options)

    print("Ready")
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue(loop=loop)
    producer_coro = produce(queue)
    consumer_coro = consume(queue, matrix)
    loop.run_until_complete(asyncio.gather(producer_coro, consumer_coro))
    loop.close()
