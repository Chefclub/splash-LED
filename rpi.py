#!/usr/bin/env python3
# git@github.com:Chefclub/splash-LED.git
import asyncio
import aiohttp
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
BOT_URL = "https://networks-monitoring.chefclub.tools/v1/splash-led-bot"


def write_message(double_buffer, font, color, initX, y, message, reverse=False):
    for i in range(3):
        for x in range(MAX_WIDTH, initX, -1 if reverse else -2):
            graphics.DrawText(double_buffer, font, x, y, color, message)
            yield


async def produce(queue):
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(BOT_URL) as resp:
                if resp.status == 200:
                    body = await resp.json()
                    await queue.put(body["message"])
                else:
                    print(await resp.json())


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
    try:
        message2 = queue.get_nowait()
    except asyncio.QueueEmpty:
        message2 = None

    initX1 = -len(message1) * 10
    color1 = random.choice(colors)
    color2 = None
    line1 = iter(
        write_message(double_buffer, font, color1, initX1, 13, message1, True)
    )
    if message2:
        initX2 = -len(message2) * 10
        color2 = random.choice([c for c in colors if c != color1])
        line2 = iter(
            write_message(double_buffer, font, color2, initX2, 29, message2, False)
        )

    while True:
        double_buffer.Clear()
        if message1:
            try:
                next(line1)
            except StopIteration:
                try:
                    message1 = queue.get_nowait()
                except asyncio.QueueEmpty:
                    message1 = None
                else:
                    initX1 = -len(message1) * 10
                    color1 = random.choice([c for c in colors if c != color2])
                    line1 = iter(write_message(double_buffer, font, color1, initX1, 15, message1, True))
        else:
            try:
                message1 = queue.get_nowait()
            except asyncio.QueueEmpty:
                message1 = None
            else:
                initX1 = -len(message1) * 10
                color1 = random.choice([c for c in colors if c != color2])
                line1 = iter(write_message(double_buffer, font, color1, initX1, 15, message1, True))
        if message2:
            try:
                next(line2)
            except StopIteration:
                try:
                    message2 = queue.get_nowait()
                except asyncio.QueueEmpty:
                    message2 = None
                else:
                    initX2 = -len(message2) * 10
                    color2 = random.choice([c for c in colors if c != color1])
                    line2 = iter(write_message(double_buffer, font, color2, initX2, 31, message2, False))
        else:
            try:
                message2 = queue.get_nowait()
            except asyncio.QueueEmpty:
                message2 = None
            else:
                initX2 = -len(message2) * 10
                color2 = random.choice([c for c in colors if c != color1])
                line2 = iter(write_message(double_buffer, font, color2, initX2, 31, message2, False))

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
