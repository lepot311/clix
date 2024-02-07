'''
Create OBJ meshes for Clix maps
'''
import itertools


class Cube:
    vertices = list(itertools.product((0.0, 1.0), repeat=3))
    faces = (
        (1, 5, 7, 3),
        (1, 5, 6, 2),
        (1, 3, 4, 2),
        (8, 6, 2, 4),
        (8, 4, 3, 7),
        (8, 6, 5, 7),
    )

    def __init__(self, x, y, index=0, height=1):
        self.x      = x
        self.y      = y
        self.index  = index
        self.height = height

        self.vertices = [
            (x + self.x * -1, y + self.y * -1, z * max(0.01, self.height)) for x, y, z
            in Cube.vertices
        ]

    @property
    def vertices_str(self):
        return "".join([
            f"v {vertex[0]} {vertex[1]} {vertex[2]}\n"
            for vertex in self.vertices
        ])


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
      2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 0, 
      2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 
      2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 
      2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 
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
      2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      2, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,
      2, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,
      2, 2, 2, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0,
      2, 2, 2, 2, 2, 1, 1, 1, 2, 2, 1, 0, 0, 0, 0, 0,
      2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
      2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
    ]


filename = "map.obj"

with open(filename, 'w') as fh:
    fh.write("o clixmap\n")

    W = 16
    H = 24

    height = 0
    count = 0

    heightmap = heightmap_image()

    offset = 0
    for x in range(W):
        for y in range(H):
            offset = (W * y) + x
            height = heightmap[offset]
            print('x', x, 'y', y, 'offset', offset, 'height', height)
            count += 1
            #print(count, height)
            c = Cube(x, y, index=count, height=height)
            fh.write(c.vertices_str)
    print(f"{count} total cubes")

    for x in range(W):
        for y in range(H):
            for face in Cube.faces:
                offset = 8 * y + (8 * H * x)
                fh.write(f"f {face[0]+offset} {face[1]+offset} {face[2]+offset} {face[3]+offset}\n")
