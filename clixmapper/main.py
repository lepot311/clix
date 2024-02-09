'''
Create OBJ meshes for Clix maps
'''
import itertools


class Cube:
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
    normals_flat = (
        (-0.750, -0.433,  0.500),
        ( 0.433, -0.750,  0.500),
        ( 0.750,  0.433,  0.500),
        (-0.433,  0.750,  0.500),
        (-0.433, -0.750, -0.500),
        (-0.750,  0.433, -0.500),
        ( 0.433,  0.750, -0.500),
        ( 0.750, -0.433, -0.500),
        (-0.500, -0.433, -0.750),
        (-0.500, -0.750,  0.433),
        (-0.500,  0.433,  0.750),
        (-0.500,  0.750, -0.433),
        ( 0.500, -0.750, -0.433),
        ( 0.500,  0.433, -0.750),
        ( 0.500,  0.750,  0.433),
        ( 0.500, -0.433,  0.750),
        (-0.750, -0.500, -0.433),
        ( 0.433, -0.500, -0.750),
        ( 0.750, -0.500,  0.433),
        (-0.433, -0.500,  0.750),
        (-0.433,  0.500, -0.750),
        (-0.750,  0.500,  0.433),
        ( 0.433,  0.500,  0.750),
        ( 0.750,  0.500, -0.433),
    )

    def __init__(self, x, y, height=1):
        self.x = x
        self.y = y

        self.height = height

        self.vertices = list(itertools.product((0.0, 1.0), repeat=3))

        # adjust height
        for i, v in enumerate(self.vertices):
            if v[2] == 1.0:
                v = self.vertices[i]
                self.vertices[i] = (v[0], v[1], v[2]+height)


class Grid:
    def __init__(self, width, height, heightmap=None):
        self.w = width
        self.h = height

        self.heightmap = heightmap

        self.cubes = []

        offset = 0
        count = 0

        for x in range(self.h):
            for y in range(self.w):
                offset = (self.w * x) + y
                cube = Cube(x, y, height=self.heightmap[offset])
                self.cubes.append(cube)

    @property
    def as_obj(self):
        '''
        Forward Y+
        Up      Z+
        '''
        result = ""
        # vertices
        for cube in self.cubes:
            for v in cube.vertices:
                result += f"v {v[0]+cube.x} {v[1]+cube.y} {v[2]}\n"

        # normals
        result += "\n"
        for normal in Cube.normals_flat:
            result += f"vn {normal[0]} {normal[1]} {normal[2]}\n"

        result += "s 0\n"  # smooth shading OFF

        # faces
        result += "\n"
        for i, cube in enumerate(self.cubes):
            offset = 8 * cube.x + (8 * self.h * cube.y)
            for ni, pattern in enumerate(Cube.face_patterns):
                result += f"f {pattern[0]+1+offset}//{ni*4+1} {pattern[1]+1+offset}//{ni*4+2} {pattern[2]+1+offset}//{ni*4+3} {pattern[3]+1+offset}//{ni*4+4}\n"

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
    W = 16
    H = 24

    grid = Grid(W, H, heightmap=heightmap_image())
    fh.write(grid.as_obj)
