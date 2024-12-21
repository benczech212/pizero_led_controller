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


def rainbow_cycle(wait = 0.001, direction = 1, offset = 0, step = 1, mirror = True, erase_step = 2, erase = True,fade_speed = 0.02):
    global tick_count
    
    for j in range(512):
        pixel_offset = tick_count // 64
        for i in range(num_pixels):
            affected_pixels = []
            if mirror:
                pixel_index = (i * 256 // num_pixels) + tick_count * direction + offset
                pixel_index = num_pixels - pixel_index - 1
            else:
                pixel_index = (i * 256 // num_pixels) + tick_count * direction + offset
            pixel_id = (i * step + pixel_offset) % num_pixels
        #     affected_pixels.append(pixel_id)
            pixels[pixel_id] = wheel(pixel_index & 255)

            current_color = pixels[i]
            if erase and i % erase_step == 0:
                new_color = (0, 0, 0)
            else:
                new_color = wheel(pixel_index & 255)

            pixels[i] = (
                int(current_color[0] * (1-fade_speed) + new_color[0] * fade_speed),
                int(current_color[1] * (1-fade_speed) + new_color[1] * fade_speed),
                int(current_color[2] * (1-fade_speed) + new_color[2] * fade_speed)
            )
        # for i in range(num_pixels):
        #     if i not in affected_pixels:
        #         current_color = pixels[i]
        #         pixels[i] = (int(current_color[0] * 0.9), int(current_color[1] * 0.9), int(current_color[2] * 0.9))

        pixels.show()
        tick_count += 1
        time.sleep(wait)
        for i in range(num_pixels):
            current_color = pixels[i]
            pixels[i] = (int(current_color[0] * (1-fade_speed)), int(current_color[1] * (1-fade_speed)), int(current_color[2] * (1-fade_speed)))

def wrap_value(value, min_value, max_value):
    while value < min_value:
        value += max_value - min_value
    value %= max_value
    return value
def lerp(a, b, t):
    return a + (b - a) * t
def lerp_color(color1, color2, t):
    return (
        int(lerp(color1[0], color2[0], t)),
        int(lerp(color1[1], color2[1], t)),
        int(lerp(color1[2], color2[2], t))
    )

def rgb_to_hsv(r, g, b):
    r, g, b = r / 255, g / 255, b / 255
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin

    if delta == 0:
        h = 0
    elif cmax == r:
        h = (60 * ((g - b) / delta) + 360) % 360
    elif cmax == g:
        h = (60 * ((b - r) / delta) + 120) % 360
    elif cmax == b:
        h = (60 * ((r - g) / delta) + 240) % 360

    if cmax == 0:
        s = 0
    else:
        s = delta / cmax

    v = cmax

    return h, s, v

def hsv_to_rgb(h, s, v):
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    elif 300 <= h < 360:
        r, g, b = c, 0, x

    r, g, b = (r + m) * 255, (g + m) * 255, (b + m) * 255

    return int(r), int(g), int(b)


class Brush:
    def __init__(self, pixel_buffer, position = 0, hue = 0, size = 1, speed = 0.001, direction = 1, offset = 0, step = 1, mirror = True,hue_change_per_age = 0.01):
        self.position = position
        self.size = size
        self.speed = speed
        self.direction = direction
        self.offset = offset
        self.step = step
        self.mirror = mirror
        self.pixel_buffer = pixel_buffer
        self.total_pixels = pixel_buffer.num_pixels
        # self.fade_speed = fade_speed
        self.age = 0
        self.hue_offset = random.uniform(0,1)
        self.hue = hue
        self.hue_change_per_age = hue_change_per_age
        
    def get_color(self):
        return hsv_to_rgb(wrap_value(self.hue + self.hue_offset,0,1)*255, 1, 1)

    def draw(self):
        pixel_id_offset = wrap_value(int(self.position * self.total_pixels) + self.offset, 0, self.total_pixels)
        for i in range(self.size):
            pixel_id_primary = wrap_value(pixel_id_offset + (i * self.step), 0, self.total_pixels) 
            self.pixel_buffer.add_color(pixel_id_primary, self.get_color())
            if self.mirror:
                pixel_id_mirror = wrap_value(self.total_pixels - pixel_id_primary - 1, 0, self.total_pixels)
                self.pixel_buffer.add_color(pixel_id_mirror, self.get_color())

            

    def move(self):
        self.position += (self.speed * self.direction)
        self.position %= 1
        self.hue = wrap_value(self.hue + self.hue_change_per_age, 0, 1)
        self.age += 1
    

tick_count = 0
pixels.fill((0, 0, 0))
pixels.show()



class PixelBuffer:
    def __init__(self, num_pixels, fade_speed = 0.01):
        self.num_pixels = num_pixels
        self.pixel_buffer = [[(0, 0, 0)] for i in range(num_pixels)]
        self.fade_speed = fade_speed

    def add_color(self, pixel_id, color):
        self.pixel_buffer[pixel_id].append(color)
    
    def clear_color(self, pixel_id):
        self.pixel_buffer[pixel_id] = [(0, 0, 0)]

    def blend(self):
        for i in range(self.num_pixels):
            if len(self.pixel_buffer[i]) > 1:
                self.pixel_buffer[i] = [lerp_color(self.pixel_buffer[i][0], self.pixel_buffer[i][1], 0.1)]
            else:
                self.pixel_buffer[i] = [self.pixel_buffer[i][0]]
    def fade_all(self):
        self.blend()
        for i in range(self.num_pixels):
            self.pixel_buffer[i] = [(int(self.pixel_buffer[i][0][0] * (1-self.fade_speed)), int(self.pixel_buffer[i][0][1] * (1-self.fade_speed)), int(self.pixel_buffer[i][0][2] * (1-self.fade_speed)))]



            

    def set_pixels(self):
        for pixel_id, colors in enumerate(self.pixel_buffer):
            pixels[pixel_id] = colors[0]
buf = PixelBuffer(num_pixels)


brushes = [
    Brush(buf, position = 0.5, hue = 0.001, size = 1, speed = 0.0007, direction = 1, offset = 0, step = 1, mirror = True, hue_change_per_age = 0.001),
# Brush(buf, position = 0.5, hue = 0.100, size = 1, speed = 0.006, direction = -1, offset = 0, step = 1, mirror = True),
# Brush(buf, position = 0.5, hue = 0.200, size = 1, speed = 0.0009, direction = 1, offset = 0, step = 1, mirror = True, hue_change_per_age = random.uniform(0.0001, 0.0005)),
Brush(buf, position = 0.5, hue = 0.300, size = 1, speed = 0.0004, direction = -1, offset = 0, step = 1, mirror = True, hue_change_per_age = 0.004),
# Brush(buf, position = 0.5, hue = 0.400, size = 8, speed = 0.0003, direction = 1, offset = 0, step = 1, mirror = True, hue_change_per_age = random.uniform(0.0001, 0.0005)),
# Brush(buf, position = 0.5, hue = 0.500, size = 1, speed = 0.002, direction = -1, offset = 0, step = 1, mirror = True, hue_change_per_age = random.uniform(0.0001, 0.0005)),
# Brush(buf, position = 0.5, hue = 0.600, size = 4, speed = 0.0001, direction = 1, offset = 0, step = 1, mirror = True, hue_change_per_age = random.uniform(0.0001, 0.0005)),
]





while True:
    buf.fade_all()
    for brush in brushes:
        brush.move()
        brush.draw()
        # brush.color = wheel(int(brush.age * 0.2) % 255)
    buf.blend()
    buf.set_pixels()
    pixels.show()



    # wait = random.uniform(0.001, 0.01)
    # direction = random.choice([-1, 1])
    # offset = random.randint(0, 255)
    # offset = 0
    # step = random.randint(1, 3)
    # mirror = random.choice([True, False])
    # print(f"wait: {wait}, direction: {direction}, offset: {offset}, step: {step}, mirror: {mirror}")
    # for i in range(1024):
    #     rainbow_cycle(wait, direction, offset, step, mirror)
    #     # color_wipe(wheel(i), wait)


