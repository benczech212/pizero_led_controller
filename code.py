# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import neopixel
import time
import random
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# import subprocess

# class ChangeHandler(FileSystemEventHandler):
#     def on_modified(self, event):
#         if event.src_path.endswith(".py"):
#             print(f"{event.src_path} has been modified. Restarting service...")
#             subprocess.run(["systemctl", "restart", "led_controller.service"])

# if __name__ == "__main__":
#     path = "."  # directory to watch
#     event_handler = ChangeHandler()
#     observer = Observer()
#     observer.schedule(event_handler, path, recursive=True)
#     observer.start()
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()


# On CircuitPlayground Express, and boards with built in status NeoPixel -> board.NEOPIXEL
# Otherwise choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D1
pixel_pin = board.D18

# On a Raspberry pi, use this instead, not all pins are supported
# pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 150

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    # if pos < 0 or pos > 255:
    #     r = g = b = 0
    while pos < 0:
        pos += 255
    pos %= 255
    if pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b)


def rainbow_cycle(wait = 0.001, direction = 1, offset = 0, step = 1, mirror = True):
    for j in range(255):
        for i in range(num_pixels):
            if mirror:
                pixel_index = (i * 256 // num_pixels) + j * direction + offset
                pixel_index = num_pixels - pixel_index - 1
            else:
                pixel_index = (i * 256 // num_pixels) + j * direction + offset
            pixel_id = (i * step) % num_pixels
            pixels[pixel_id] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

def color_wipe(color, wait=0.01):
    for i in range(num_pixels):
        for j in range(num_pixels):
            if j == i:
                pixels[i] = color
            else:
                current_color = pixels[i]
                pixels[i] = (int(current_color[0] * 0.9), int(current_color[1] * 0.9), int(current_color[2] * 0.9))
        pixels.show()

while True:
   
    wait = random.uniform(0.001, 0.01)
    direction = random.choice([-1, 1])
    offset = random.randint(0, 255)
    step = random.randint(1, 3)
    mirror = random.choice([True, False])
    print(f"wait: {wait}, direction: {direction}, offset: {offset}, step: {step}, mirror: {mirror}")
    for i in range(512):
        # rainbow_cycle(wait, direction, offset, step, mirror)
        color_wipe(wheel(i), wait)