import random

# Constants for map size
WIDTH = 80
HEIGHT = 50

# Custom implementation of Map
class Map:
    def __init__(self):
        self.tiles = [(ord('.'), (100, 100, 100)) for _ in range(WIDTH * HEIGHT)]

    def clear(self, tile, color):
        self.tiles = [(tile, color) for _ in range(WIDTH * HEIGHT)]

    def clear_default(self):
        self.clear(ord('.'), (100, 100, 100))

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
        # Print the map tiles in the terminal
        for y in range(HEIGHT):
            for x in range(WIDTH):
                idx = y * WIDTH + x
                glyph, color = self.frames[self.current_frame][0].tiles[idx]
                print(chr(glyph), end="")
            print()

        print(self.frames[self.current_frame][1])  # Print the frame's name

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
                    map_obj.set(Point(x, y), ord('.'), (100, 100, 100))
                else:
                    map_obj.set(Point(x, y), ord('#'), (0, 255, 0))

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
                            map_obj.set(pt, ord('$'), (255, 215, 0))
                        elif string_vec[i] == "^":
                            map_obj.set(pt, ord('^'), (255, 0, 0))
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
                    map_obj.tiles[idx] = (ord('.'), (100, 100, 100))
                elif neighbors < 5:
                    map_obj.tiles[idx] = (ord('#'), (0, 255, 0))
                else:
                    map_obj.tiles[idx] = (ord('.'), (100, 100, 100))

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

# Create the RoomBuilder and State objects, and run the game
builder = RoomBuilder()
state = State(builder)
state.run()
