'''
Create OBJ meshes for Clix maps
'''
import itertools


class Cube:
    face_patterns = (
        (0, 2, 6, 4),
        (1, 5, 7, 3),
        (0, 1, 3, 2),
        (4, 6, 7, 5),
        (2, 3, 7, 6),
        (0, 4, 5, 1),
    )
    normals = (
        ( 0.0,  0.0,  1.0),
        ( 0.0,  0.0, -1.0),
        ( 1.0,  0.0,  0.0),
        (-1.0,  0.0,  0.0),
        ( 0.0,  1.0,  0.0),
        ( 0.0, -1.0,  0.0),
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

    def __init__(self, height=1):
        self.height = height

        self.vertices = list(itertools.product((0.0, 1.0), repeat=3))

    def translate(self, x, y, z):
        for i, v in enumerate(self.vertices):
            self.vertices[i] = (
                v[0] + x,
                v[1] + y,
                v[2] + z,
            )

    @property
    def obj_vertices(self):
        result = ""
        for v in self.vertices:
            result += f"v {v[0]} {v[1]} {v[2]}\n"
        return result

    @property
    def obj_uvs(self):
        # vertex texture coords (UVs)
        # load the map image
        # rotate the map image as needed
        # figure out how many pixels per cell in x and y directions
        # coords are 0..1??

        for i, cube in enumerate(self.cubes):
            offset_cube_x = (1/self.w) * cube.x
            offset_cube_y = (1/self.h) * cube.y

            order = (
                (0, 1),
                (0, 0),
                (1, 0),
                (1, 1),
            )

            # write four coords
            for ox, oy in order:
                u = offset_cube_x + ((1/self.w) * ox)
                v = offset_cube_y + ((1/self.h) * oy)

                result += f"vt {u} {v}\n"

    @property
    def obj_normals(self):
        # normals
        result += "\n"
        for normal in Cube.normals:
            result += f"vn {normal[0]} {normal[1]} {normal[2]}\n"

    def obj_faces(self, x, y):
        result = "\n"
        offset = x * 8

        for pattern in Cube.face_patterns:
            result += "f "
            for n in range(4):
                result += f"{pattern[n]+1+offset} "
            result += "\n"

        #for i, cube in enumerate(self.cubes):
        #    offset = 8 * cube.x + (8 * self.h * cube.y)

        #for ni, pattern in enumerate(Cube.face_patterns):
        #    result += f"f {pattern[0]+1+offset}//{ni+1} {pattern[1]+1+offset}//{ni+1} {pattern[2]+1+offset}//{ni+1} {pattern[3]+1+offset}//{ni+1}\n"

            #if ni == 0:
                # TODO may need to flip the order like we did when writing the vt coords....
                # add uv to top faces only
            #    result += f"f {pattern[0]+1+offset}/{i*4+1}/{ni+1} {pattern[1]+1+offset}/{i*4+2}/{ni+1} {pattern[2]+1+offset}/{i*4+3}/{ni+1} {pattern[3]+1+offset}/{i*4+4}/{ni+1}\n"
            #else:
            #    result += f"f {pattern[0]+1+offset}//{ni+1} {pattern[1]+1+offset}//{ni+1} {pattern[2]+1+offset}//{ni+1} {pattern[3]+1+offset}//{ni+1}\n"

        return result


class Grid:
    def __init__(self, width, height, heightmap=None):
        self.w = width
        self.h = height

        self.heightmap = heightmap

        self.cubes = [
            Cube()
            for n in range(self.w * self.h)
        ]

    @property
    def as_obj(self):
        '''
        Forward Y+
        Up      Z+
        '''
        result = "s 0\n"  # smooth shading OFF

        # translate
        for row in range(self.h):
            for col in range(self.w):
                offset = col + (row * col)
                cube = self.cubes[offset]
                # translate in-place
                cube.translate(col, row-1, 0)


        # vertices
        for cube in self.cubes:
            result += cube.obj_vertices

        #for cube in self.cubes:
        #    result += cube.obj_uvs

        #for cube in self.cubes:
        #    result += cube.obj_normals

        for row in range(self.h):
            for col in range(self.w):
                result += cube.obj_faces(col, row)

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
    W = 2
    H = 1

    grid = Grid(W, H, heightmap=heightmap_image())
    fh.write(grid.as_obj)
