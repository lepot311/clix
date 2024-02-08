'''
Create OBJ meshes for Clix maps
'''
import itertools


class Cube:
    vertices = list(itertools.product((0.0, 1.0), repeat=3))
    face_patterns = (
        (1, 5, 7, 3), # z=0 down
        (0, 2, 6, 4), # z=1 up
        (0, 1, 3, 2), # x=0 west
        (4, 6, 7, 5), # x=1 east
        (0, 4, 5, 1), # y=0 south
        (2, 3, 7, 6), # y=1 north
    )
    normals = (
        ( 0.0,  0.0, -1.0),
        ( 0.0,  0.0,  1.0),
        (-1.0,  0.0,  0.0),
        ( 1.0,  0.0,  0.0),
        ( 0.0, -1.0,  0.0),
        ( 0.0,  1.0,  0.0),
    )

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Grid:
    def __init__(self, width, height):
        self.w = width
        self.h = height

        self.cubes = []

        for x in range(self.h):
            for y in range(self.w):
                cube = Cube(x, y)
                self.cubes.append(cube)

    @property
    def as_obj(self):
        result = ""
        # vertices
        for cube in self.cubes:
            for v in cube.vertices:
                result += f"v {v[0]+cube.x} {v[1]+cube.y} {v[2]}\n"

        # normals
        result += "\n"
        for normal in Cube.normals:
            result += f"vn {normal[0]} {normal[1]} {normal[2]}\n"

        # faces
        result += "\n"
        for i, cube in enumerate(self.cubes):
            offset = 8 * cube.x + (8 * self.h * cube.y)
            for ni, pattern in enumerate(Cube.face_patterns):
                result += f"f {pattern[0]+1+offset}//{ni+1} {pattern[1]+1+offset}//{ni+1} {pattern[2]+1+offset}//{ni+1} {pattern[3]+1+offset}//{ni+1}\n"

        result += "s 0\n"  # smooth shading OFF

        return result


def heightmap_random(max_height=4):
    import random
    return [
        random.randrange(max_height)
        for n in range(W*H)
    ]

def heightmap_simplex():
    from noise import snoise2
    max_height = 4
    octaves = 4
    freq = 4 * octaves
    count = 0
    result = []
    for x in range(W):
        for y in range(H):
            height = snoise2(x / freq, y / freq, octaves)
            count += 1
            clamped = int(max_height * height) + (max_height / 2)
            result.append(clamped)
    return result

def heightmap_image():
    return [
      2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
      2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
      2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0,
      2, 2, 2, 2, 2, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 0,
      2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0,
      2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0,
      2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0,
      2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0,   #8
      2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1,
      2, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1,
      2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1,
      2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
      2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
      2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
      2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
      2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1,   #16
      2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      2, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      2, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      2, 2, 2, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0,
      2, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 1, 0, 0, 0, 0,
      2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
      2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    ]


filename = "map.obj"

with open(filename, 'w') as fh:
    #fh.write("o clixmap\n")

    W = 16
    H = 24

    height = 0
    count = 0

    heightmap = heightmap_image()

    grid = Grid(W, H)
    fh.write(grid.as_obj)
