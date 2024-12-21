import pygame
import time
import random

def wrap_value(value, min_value, max_value):
    while value < min_value:
        value += max_value - min_value
    value %= max_value
    return value

def lerp(a, b, t):
    return a + (b - a) * t
def lerp_color_hsv(hsv1, hvs2, t):
    return (
        lerp(hsv1[0], hvs2[0], t),
        lerp(hsv1[1], hvs2[1], t),
        lerp(hsv1[2], hvs2[2], t)
    )

def lerp_color_int(color1, color2, t):
    return (
        int(lerp(color1[0], color2[0], t)),
        int(lerp(color1[1], color2[1], t)),
        int(lerp(color1[2], color2[2], t))
    )

def wheel(pos):
    wrap_value(pos, 0, 255)
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def int_rgb_to_float_hsv(r, g, b):
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
    h /= 360
    return h, s, v

def hsv_to_rgb(h, s, v):
    wrap_value(h, 0, 1)
    wrap_value(s, 0, 1)
    wrap_value(v, 0, 1)
    c = v * s
    x = c * (1 - abs((h * 6) % 2 - 1))
    m = v - c

    if 0 <= h < 1/6 or h == 1:
        r, g, b = c, x, 0
    elif 1/6 <= h < 2/6:
        r, g, b = x, c, 0
    elif 2/6 <= h < 3/6:
        r, g, b = 0, c, x
    elif 3/6 <= h < 4/6:
        r, g, b = 0, x, c
    elif 4/6 <= h < 5/6:
        r, g, b = x, 0, c
    elif 5/6 <= h < 1:
        r, g, b = c, 0, x

    r, g, b = (r + m) * 255, (g + m) * 255, (b + m) * 255

    return int(r), int(g), int(b)
class Brush:
    def __init__(self, pixel_buffer, position = 0, hue = 0.0, sat=0.0, val=0.0, size = 1, speed = 0.001, direction = 1, offset = 0, step = 1, mirror = True,blend_strength = 0.5):
        self.position = position
        self.size = size
        self.speed = speed
        self.direction = direction
        self.offset = offset
        self.step = step
        self.mirror = mirror
        self.pixel_buffer = pixel_buffer
        self.total_pixels = pixel_buffer.num_pixels
        self.blend_strength = blend_strength
        # self.fade_speed = fade_speed
        
        self.hue = hue
        self.sat = 1
        self.val = 1
        self.age = 0
        
    def get_color_hsv(self):
        return wrap_value(self.hue,0,1), self.sat, self.val
    def get_color_rgb(self):
        return hsv_to_rgb(*self.get_color_hsv())


        

    def draw(self):
        pixel_id_offset = wrap_value(int(self.position * self.total_pixels) + self.offset, 0, self.total_pixels)
        for i in range(self.size):
            pixel_id_primary = wrap_value(pixel_id_offset + (i * self.step), 0, self.total_pixels) 
            self.pixel_buffer.add_color_target(pixel_id_primary, self.get_color_hsv(),self.blend_strength)
            if self.mirror:
                pixel_id_mirror = wrap_value(self.total_pixels - pixel_id_primary - 1, 0, self.total_pixels)
                self.pixel_buffer.add_color_target(pixel_id_mirror, self.get_color_hsv(),self.blend_strength)

            

    def move(self):
        self.position += (self.speed * self.direction)
        self.position %= 1
        self.hue = wrap_value(self.hue, 0, 1)
        self.age += 1


class PixelBuffer:
    def __init__(self, num_pixels, fade_speed=0.01):
        self.num_pixels = num_pixels
        self.hsv_target_buffer = [[((0.0, 0.0, 0.0),0.5)] for _ in range(num_pixels)]
        self.fade_speed = fade_speed
        self.rgb_target = []
        self.hsv_target = []

    def add_color_target(self, pixel_id, color, blend_strength):
        self.hsv_target_buffer[pixel_id].append((color, blend_strength))

    def clear_color_target(self, pixel_id):
        self.hsv_target_buffer[pixel_id] = [((0.0, 0.0, 0.0), 0.5)]

    def blend(self):
        self.rgb_target = []
        self.hsv_target = []
        for pixel_id in range(self.num_pixels):
            if len(self.hsv_target_buffer[pixel_id]) == 0:
                self.rgb_target.append((0, 0, 0))
                self.hsv_target.append((0.0, 0.0, 0.0))
                continue
            result_hsv, blend_strength = self.hsv_target_buffer[pixel_id][0]
            result_h, result_s, result_v = result_hsv
            while len(self.hsv_target_buffer[pixel_id]) > 1:
                first_hsv,fist_blend_strength = self.hsv_target_buffer[pixel_id][0]
                second_hsv,second_blend_strength = self.hsv_target_buffer[pixel_id][1]
                blend_strength = 1 - (1 - blend_strength) * (1 - second_blend_strength)
                if first_hsv[1] == 0:
                    result_h = second_hsv[0]
                elif second_hsv[1] == 0:
                    result_h = first_hsv[0]
                else:
                    result_h = lerp(first_hsv[0], second_hsv[0], blend_strength)
                result_s = lerp(first_hsv[1], second_hsv[1], blend_strength)
                result_v = lerp(first_hsv[2], second_hsv[2], blend_strength)
                # remove first color and repeat
                self.hsv_target_buffer[pixel_id].pop(0)
            self.hsv_target_buffer[pixel_id].pop(0)
            pixel_color_hsv = (result_h, result_s, result_v)
            pixel_color_rgb = hsv_to_rgb(*pixel_color_hsv)
            self.rgb_target.append(pixel_color_rgb)
            self.hsv_target.append(pixel_color_hsv)

    def fade_targets(self):
        for pixel_id in range(self.num_pixels):
            self.rgb_target[pixel_id] = lerp_color_int(self.rgb_target[pixel_id], (0, 0, 0), self.fade_speed)
            self.hsv_target[pixel_id] = int_rgb_to_float_hsv(*self.rgb_target[pixel_id])
tick_count = 0
pixel_count = 150
pixels = [(0, 0, 0) for _ in range(pixel_count)]
buf = PixelBuffer(pixel_count,fade_speed = 0.05)



clock = pygame.time.Clock()
pygame.init()
screen_width = 1080
screen_height = 100
pixel_width = screen_width // pixel_count
pixel_height = 50

screen = pygame.display.set_mode((screen_width, screen_height))

def update_loop(pixels):
    for i in range(pixel_count):
        current_rgb = pixels[i]
        current_hsv = int_rgb_to_float_hsv(*current_rgb)
        target_hsv = buf.hsv_target[i]
        if target_hsv is None: continue
        target_h, target_s, target_v = target_hsv
        target_rgb = hsv_to_rgb(target_h, target_s, target_v)
        new_color = lerp_color_int(current_rgb, target_rgb, buf.fade_speed)

        pixels[i] = new_color

def draw_screen_debug(pixels):
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    for i, color in enumerate(pixels):
        pygame.draw.rect(screen, color, (i * pixel_width, 0, pixel_width, pixel_height))
        font = pygame.font.SysFont(None, 24)
        # for i, color in enumerate(pixels):
        #     text_surface = font.render(f'{i}', True, (255, 255, 255))
        #     text_rect = text_surface.get_rect(center=(i * pixel_width + pixel_width // 2, pixel_height + 20))
        #     screen.blit(text_surface, text_rect)
    pygame.display.update()
    clock.tick(1000)

brushes = [Brush(
    pixel_buffer=buf,
    position=0,
    hue=0,
    sat=1,
    val=1,
    size=24,
    speed=0.001,
    direction=1,
    offset=0,
    step=1,
    mirror=False,
    blend_strength = 1.0
),
Brush(
    pixel_buffer=buf,
    position=0,
    hue=0.22,
    sat=1,
    val=0,
    size=20,
    speed=0.005,
    direction=1,
    offset=0,
    step=1,
    mirror=False,
    blend_strength = 1.0
),
# Brush(
#     pixel_buffer=buf,
#     position=0,
#     hue=0.44,
#     size=12,
#     speed=0.009,
#     direction=-1,
#     offset=0,
#     step=1,
#     mirror=True
# ),
# Brush(
#     pixel_buffer=buf,
#     position=0,
#     hue=0.66,
#     size=16,
#     speed=0.003,
#     direction=-1,
#     offset=0,
#     step=1,
#     mirror=True
# ),]
]

while True:

    for brush in brushes:
        brush.draw()
        brush.move()
    # brushes[0].hue += 0.001
    buf.blend()

    # update pixels
    update_loop(pixels)
    draw_screen_debug(pixels)
    
    tick_count += 1
