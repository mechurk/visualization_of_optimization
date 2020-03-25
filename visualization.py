#!/usr/bin/python3

import re
from collections import Counter
import sys
import json

# --------------------------------------------------------------#
# variables
EPSILON = 0.01

# --------------------------------------------------------------#
# functions
# --------------------------------#
# parsing informations

# create dict with ID and new hight
def create_dict_new_body_height(center_matrix, height_center):
    new_height = {}
    for key_cm, value_cm in center_matrix.items():
        for key_hc, value_hc in height_center.items():
            if value_cm != 0:
                if value_hc != 0:
                    # print (key_cm,key_hc)
                    a = key_hc
                    a = re.sub('height_center_', '', a)
                    # print (a)

                    # parsing key from dict
                    if a in key_cm:
                        # var = str("\'center_matrix_('" + a + "\',_\'\'")
                        # print (var)
                        b = key_cm
                        b = re.sub('center_matrix_', '', b)
                        c = re.sub('\'\)$', '', b)
                        d = re.split(",_\'", c)
                        # print (d[1])
                        id_change = (d[1])
                        new_height[id_change] = value_hc
    return new_height


def create_dict_new_roof_height(center_matrix, height_roof_center):
    new_height = {}
    for key_cm, value_cm in center_matrix.items():
        for key_hc, value_hc in height_roof_center.items():
            if value_cm != 0:
                if value_hc != 0:
                    # print (key_cm,key_hc)
                    a = key_hc
                    a = re.sub('height_roof_center_', '', a)
                    # print (a)

                    # parsing key from dict
                    if a in key_cm:
                        var = str("\'center_matrix_('" + a + "\',_\'\'")
                        # print (var)
                        b = key_cm
                        b = re.sub('center_matrix_', '', b)
                        c = re.sub('\'\)$', '', b)
                        d = re.split(",_\'", c)
                        # print (d[1])
                        id_change = (d[1])
                        new_height[id_change] = value_hc
    return new_height


def calculate_new_z_cords_body(new_body_heights, z_footprints):
    new_z_coords_body = {}
    for key_b, value_b in new_body_heights.items():
        for key_f, value_f in z_footprints.items():
            # key_f_p=re.sub(r'\D','',key_f)
            # key_b_p=re.sub(r'\D','',key_b)
            key_b_s = str(key_b)
            key_b = key_b_s.replace("_", "-")
            if key_b == key_f:
                # sum=value_b+value_f
                sum = value_b + 0
                new_z_coords_body[key_f] = sum

    return new_z_coords_body


def calculate_new_z_cords_roof(new_roof_heights, z_max_body, z_max_roof):
    new_z_coords_body = {}
    for key_zmr, value_zmr in z_max_roof.items():
        if value_zmr != 0:
            for key_b, value_b in new_roof_heights.items():
                for key_f, value_f in z_max_body.items():
                    key_b_s = str(key_b)
                    key_b = key_b_s.replace("_", "-")
                    if key_b == key_f:
                        sum = value_b + value_f
                        new_z_coords_body[key_f] = sum


        else:
            new_z_coords_body[key_zmr] = 0

    return new_z_coords_body


# --------------------------------#
# working with OBJ


def load_obj(filename):
    header = []
    vertices = []
    objects = {}
    with open(sys.argv[1]) as f:
        # Parse header
        while True:
            line = f.readline()
            if line[0] == 'v':
                break
            header.append(line)

        # Parse vertices
        while True:
            if line[0] == 'o':
                break
            if len(line) < 7 or line[0] != 'v':
                print("Skipping line: {}".format(line))
                line = f.readline()
                continue
            (_, x, y, z) = line.strip().split(' ')
            vertices.append([float(x), float(y), float(z)])
            line = f.readline()

        # Parse objects
        aid = None
        faces = []
        while True:
            if line == '':
                if aid:
                    objects[aid] = faces
                    print(faces, aid)
                break
            if len(line) < 7 or line[0] not in ('o', 'f'):
                print("Skipping line: {}".format(line))
                line = f.readline()
                continue
            if line[0] == 'o':
                if aid:
                    objects[aid] = faces
                aid = line.strip().split(' ')[1][2:-2]
                faces = []
                line = f.readline()
                continue
            preface = line.strip().split(" ")[1:]
            faces.append(list(map(int, preface)))
            line = f.readline()
    return (header, vertices, objects)


def change_height(obj, vertices, old, new):
    for f in obj:
        for vidx in f:
            if abs(vertices[vidx - 1][2] - old) < EPSILON:
                vertices[vidx - 1][2] = new
                print("Changed {} to {}".format(old, new))


def change_height_footprints(obj, vertices, old):
    for f in obj:
        for vidx in f:
            if abs(vertices[vidx - 1][2] - old) < EPSILON:
                vertices[vidx - 1][2] = 0
                print("Changed {} to {}".format(old, 0))


def modify_objects(objects, vertices, fdict, tdict):
    for (obj_id, old_height) in fdict.items():
        new_height = tdict[obj_id]
        if old_height == 0 or new_height == 0:
            continue
        if obj_id not in objects:
            print("No object with id {}".format(obj_id))
            continue
        print("Changing height {} to {} on object {}".format(old_height, new_height, obj_id))
        change_height(objects[obj_id], vertices, old_height, new_height)


def modify_objects_footprints(objects, vertices, fdict):
    for (obj_id, old_height) in fdict.items():
        # new_height = tdict[obj_id]
        if old_height == 0:
            continue
        if obj_id not in objects:
            print("No object with id {}".format(obj_id))
            continue
        print("Changing height {} to {} on object {}".format(old_height, 0, obj_id))
        change_height_footprints(objects[obj_id], vertices, old_height)


def save_obj(header, vertices, objects, filename,centers):
    with open(filename, "w", encoding="utf-8") as f:
        for l in header:
            f.write(l)
        f.write("\n")
        for v in vertices:
            f.write("v {}\n".format(" ".join(map(str, v))))
        f.write("\n")
        for obj_id, faces in objects.items():
                for key_c, items_c in centers.items():
                    if key_c==obj_id:
                        f.write("o ['{}']\n".format(obj_id))
                        f.write("g ['{}']\n".format(items_c))
                        for face in faces:
                            f.write("f {} \n".format(" ".join(map(str, face))))

def create_center_groups(center_matrix):
    centers ={}
    for key_cm, items_cm in center_matrix.items():
        if items_cm !=0:
            b = key_cm
            b = re.sub('center_matrix_', '', b)
            c = re.sub('\'\)$', '', b)
            d = re.sub('\(\'','',c)
            e = re.split("\',_\'", d)
            e0= str(e[0])
            e1= str(e[1])
            pe0=e0.replace("_", "-")
            pe1=e1.replace("_", "-")

            #id_change = (f[1])
            centers[pe1] = pe0
    return centers

# --------------------------------------------------------------#
solution_all = json.load(open(sys.argv[2]))

with open(sys.argv[3], 'r') as fd:
    all=json.load(fd)

z_footprints=all[0]
z_max_body =all [1]
z_max_roof =all[2]

cm = "center_matrix_"
hc = "height_center"
hrc = "height_roof_center"

# create dictionaries from solution of optimization
center_matrix = dict(filter(lambda item: cm in item[0], solution_all.items()))
height_center = dict(filter(lambda item: hc in item[0], solution_all.items()))
height_roof_center = dict(filter(lambda item: hrc in item[0], solution_all.items()))

print(center_matrix)
print(height_center)
print(height_roof_center)
# --------------------------------------------------------------#
# calling functions

new_body_heights = create_dict_new_body_height(center_matrix, height_center)
new_roof_heights = create_dict_new_roof_height(center_matrix, height_roof_center)

new_z_coords_body = calculate_new_z_cords_body(new_body_heights, z_footprints)
new_z_coords_roof = calculate_new_z_cords_roof(new_roof_heights, new_z_coords_body, z_max_roof)
print("results:")
print("new_heights_body=",new_body_heights)
print("new_heights_roof=",new_roof_heights)

print(len(new_z_coords_body))
print(len(new_z_coords_roof))

(header, vertices, objects) = load_obj(sys.argv[1])
print(objects.keys())
modify_objects(objects, vertices, z_max_roof, new_z_coords_roof)
modify_objects(objects, vertices, z_max_body, new_z_coords_body)
modify_objects_footprints(objects, vertices, z_footprints)
centers = create_center_groups(center_matrix)
save_obj(header, vertices, objects, "out.obj",centers)


