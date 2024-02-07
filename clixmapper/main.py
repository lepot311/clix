'''
Create OBJ meshes for Clix maps
'''
import itertools


class Cube:
    vertices = list(itertools.product((0.0, 1.0), repeat=3))

    def __init__(self, x, y, height=1):
        self.x      = x
        self.y      = y
        self.height = height

        self.vertices = [
            (x + self.x, y + self.y, z * max(0.01, self.height)) for x, y, z
            in Cube.vertices
        ]


filename = "map.obj"

faces = (
    (1, 5, 7, 3),
    (1, 5, 6, 2),
    (1, 3, 4, 2),
    (8, 6, 2, 4),
    (8, 4, 3, 7),
    (8, 6, 5, 7),
)

with open(filename, 'w') as fh:
    fh.write("o clixmap\n")

    W = 16
    H = 24

    height = 0
    count = 0

    for x in range(W):
        for y in range(H):
            count += 1
            height = (1 / (W*H)) * count
            print(count, height)
            c = Cube(x, y, height=height)

            for vertex in c.vertices:
                fh.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
    print(f"{count} total cubes")

    for x in range(W):
        for y in range(H):
            for face in faces:
                offset = 8 * y + (8 * H * x)
                fh.write(f"f {face[0]+offset} {face[1]+offset} {face[2]+offset} {face[3]+offset}\n")
