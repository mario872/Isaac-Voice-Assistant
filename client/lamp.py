import time
import board
import neopixel

num_pixels = 10
ORDER = neopixel.RGB

pixels = neopixel.NeoPixel(board.D21, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
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
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)
        
def lamp_colour(colour: str):
    colours = {'white': (255, 255, 255),
               'red': (255, 0, 0),
               'green': (0, 255, 0),
               'blue': (0, 0, 255),
               'orange': (255, 175, 0),
               'yellow': (200, 255, 0),
               'aqua': (0, 200, 150),
               'purple': (200, 0, 255),
               'pink': (255, 0, 175)}
    
    pixels.fill(colours[colour])
    pixels.show()
    
lamp_colour(input('Lamp colour: ').lower())