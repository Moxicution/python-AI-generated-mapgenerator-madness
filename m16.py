import random
import time
import os
import ctypes

# Constants for map size
WIDTH = 80
HEIGHT = 50
ROOM_WIDTH = 6
ROOM_HEIGHT = 5

# Windows API constants
STD_OUTPUT_HANDLE = -11
FOREGROUND_BLACK = 0x0000
FOREGROUND_RED = 0x0004
FOREGROUND_GREEN = 0x0002
FOREGROUND_YELLOW = FOREGROUND_RED | FOREGROUND_GREEN
FOREGROUND_WHITE = FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLACK
FOREGROUND_INTENSITY = 0x0008
BACKGROUND_BLACK = 0x0000
BACKGROUND_RED = 0x0040
BACKGROUND_GREEN = 0x0020
BACKGROUND_YELLOW = BACKGROUND_RED | BACKGROUND_GREEN
BACKGROUND_WHITE = BACKGROUND_RED | BACKGROUND_GREEN | BACKGROUND_BLACK
BACKGROUND_INTENSITY = 0x0080

# Custom implementation of Map
class Map:
    def __init__(self):
        self.tiles = [(ord('.'), FOREGROUND_WHITE | BACKGROUND_BLACK) for _ in range(WIDTH * HEIGHT)]

    def clear(self, tile, color):
        self.tiles = [(tile, color) for _ in range(WIDTH * HEIGHT)]

    def clear_default(self):
        self.clear(ord('.'), FOREGROUND_WHITE | BACKGROUND_BLACK)

    def set(self, position, glyph, color):
        idx = position.y * WIDTH + position.x
        self.tiles[idx] = (glyph, color)

    def in_bounds(self, point):
        return 0 <= point.x < WIDTH and 0 <= point.y < HEIGHT

    def try_idx(self, point):
        if not self.in_bounds(point):
            return None
        return self.mapidx(point.x, point.y)

    def mapidx(self, x, y):
        return y * WIDTH + x

# Custom implementation of State
class State:
    def __init__(self, builder):
        self.builder = builder
        self.frames = []
        self.current_frame = 0

    def tick(self):
        os.system('cls')  # Clear the terminal

        # Print the map tiles in the terminal
        for y in range(HEIGHT):
            for x in range(WIDTH):
                idx = y * WIDTH + x
                glyph, color = self.frames[self.current_frame][0].tiles[idx]
                draw_char(glyph, color)
            print()

        print_color_centered(0, "WHITE", "BLACK", self.frames[self.current_frame][1])

        # Move to the next frame if Return key is pressed
        should_continue = True
        key = input("Press Enter to continue to the next frame, or any other key to quit.")
        if key == "":
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                should_continue = False

        return should_continue

    def run(self):
        self.builder.setup()
        self.frames = self.builder.build()

        while self.current_frame < len(self.frames):
            if not self.tick():
                break

# Custom implementation of RoomBuilder (similar to the Rust version)
class RoomBuilder:
    def new(self):
        return self

    def setup(self):
        pass

    def build(self):
        frames = []

        map_obj = Map()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                roll = random.randint(0, 99)
                if roll < 55:
                    map_obj.set(Point(x, y), ord('.'), FOREGROUND_WHITE | BACKGROUND_BLACK)
                else:
                    map_obj.set(Point(x, y), ord('#'), FOREGROUND_GREEN | BACKGROUND_BLACK)

        for _ in range(10):
            self.iterate(map_obj)

        frames.append((map_obj, "Cellular Automata Map"))

        not_trap = """
......
.^^^^.
.^$$^.
.^^^^.
......
"""

        string_vec = [c for c in not_trap if c not in ("\r", "\n")]

        while True:
            base = Point(random.randint(1, WIDTH - 11), random.randint(1, HEIGHT - 10))
            can_build = True
            target = Rect(base.x, base.y, 6, 5)
            for p in target:
                idx = map_obj.mapidx(p.x, p.y)
                if map_obj.tiles[idx][0] != ord('#'):
                    can_build = False
                    break

            if can_build:
                i = 0
                for y in range(5):
                    for x in range(6):
                        pt = Point(x, y) + base
                        if string_vec[i] == "$":
                            map_obj.set(pt, ord('$'), FOREGROUND_YELLOW | BACKGROUND_BLACK)
                        elif string_vec[i] == "^":
                            map_obj.set(pt, ord('^'), FOREGROUND_RED | BACKGROUND_BLACK)
                        elif string_vec[i] == "|":
                            map_obj.set(pt, ord('|'), FOREGROUND_RED | BACKGROUND_BLACK)   
                        i += 1
                break

        frames.append((map_obj, "Found a place for the prefab"))

        return frames

    def iterate(self, map_obj):
        map_copy = Map()
        map_copy.tiles = list(map_obj.tiles)

        for y in range(1, HEIGHT - 1):
            for x in range(1, WIDTH - 1):
                neighbors = self.count_neighbors(map_copy, x, y)
                idx = y * WIDTH + x
                if neighbors == 0:
                    map_obj.tiles[idx] = (ord('.'), FOREGROUND_WHITE | BACKGROUND_BLACK)
                elif neighbors < 5:
                    map_obj.tiles[idx] = (ord('#'), FOREGROUND_GREEN | BACKGROUND_BLACK)
                else:
                    map_obj.tiles[idx] = (ord('.'), FOREGROUND_WHITE | BACKGROUND_BLACK)

    def count_neighbors(self, map_obj, x, y):
        n = 0
        for ty in range(-1, 2):
            for tx in range(-1, 2):
                if not (ty == 0 and tx == 0):
                    if map_obj.in_bounds(Point(x + tx, y + ty)):
                        idx = map_obj.mapidx(x + tx, y + ty)
                        if map_obj.tiles[idx][0] == ord('.'):
                            n += 1
        return n

# Point class to represent (x, y) coordinates
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

# Rect class to represent a rectangle
class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __iter__(self):
        for y in range(self.y, self.y + self.height):
            for x in range(self.x, self.x + self.width):
                yield Point(x, y)

def draw_char(glyph, color):
    ctypes.windll.kernel32.SetConsoleTextAttribute(ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE), color)
    print(chr(glyph), end='')

def print_color_centered(y, color, background_color, text):
    ctypes.windll.kernel32.SetConsoleTextAttribute(ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE), get_color_code(color, background_color))
    text = text.center(WIDTH)
    print(text[:WIDTH])

def get_color_code(foreground, background):
    color_map = {
        "BLACK": FOREGROUND_BLACK,
        "RED": FOREGROUND_RED,
        "GREEN": FOREGROUND_GREEN,
        "YELLOW": FOREGROUND_YELLOW,
        "WHITE": FOREGROUND_WHITE,
    }
    bg_color_map = {
        "BLACK": BACKGROUND_BLACK,
        "RED": BACKGROUND_RED,
        "GREEN": BACKGROUND_GREEN,
        "YELLOW": BACKGROUND_YELLOW,
        "WHITE": BACKGROUND_WHITE,
    }
    return color_map.get(foreground, FOREGROUND_WHITE) | bg_color_map.get(background, BACKGROUND_BLACK)

def key_pressed(key_code=""):
    key = input()  # Read a single character from the user
    return key

def tick(frames_per_second):
    # Replace this with your custom game loop code.
    # For example, using the Python `time.sleep` function to control the frame rate.
    time.sleep(1 / frames_per_second)

def main():
    gen = RoomBuilder()
    frames = gen.build()
    current_frame = 0

    while current_frame < len(frames):
        map_obj, title = frames[current_frame]

        for y in range(HEIGHT):
            for x in range(WIDTH):
                glyph, color = map_obj.tiles[y * WIDTH + x]
                draw_char(glyph, color)
            print()  # Add a line break after each row

        print_color_centered(0, "WHITE", "BLACK", title)

        if key_pressed(""):
            current_frame += 1

        tick(30)

if __name__ == "__main__":
    main()
