# coding=utf-8
"""
Showing lighting effects over two textured objects: Flat, Gauraud and Phong.
"""

import glfw
import copy
from OpenGL.GL import *
import numpy as np
import sys
import os.path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.lighting_shaders as ls
from grafica.assets_path import getAssetPath
import grafica.scene_graph as sg





def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape


def createOFFShape(pipeline, r, g, b):
    shape = readOFF(getAssetPath('sphere.off'), (r, g, b))
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)

    return gpuShape


def readOFF(filename, color):
    vertices = []
    normals = []
    faces = []

    with open(filename, 'r') as file:
        line = file.readline().strip()
        assert line == "OFF"

        line = file.readline().strip()
        aux = line.split(' ')

        numVertices = int(aux[0])
        numFaces = int(aux[1])

        for i in range(numVertices):
            aux = file.readline().strip().split(' ')
            vertices += [float(coord) for coord in aux[0:]]

        vertices = np.asarray(vertices)
        vertices = np.reshape(vertices, (numVertices, 3))
        print(f'Vertices shape: {vertices.shape}')

        normals = np.zeros((numVertices, 3), dtype=np.float32)
        print(f'Normals shape: {normals.shape}')

        for i in range(numFaces):
            aux = file.readline().strip().split(' ')
            aux = [int(index) for index in aux[0:]]
            faces += [aux[1:]]

            vecA = [vertices[aux[2]][0] - vertices[aux[1]][0], vertices[aux[2]][1] - vertices[aux[1]][1],
                    vertices[aux[2]][2] - vertices[aux[1]][2]]
            vecB = [vertices[aux[3]][0] - vertices[aux[2]][0], vertices[aux[3]][1] - vertices[aux[2]][1],
                    vertices[aux[3]][2] - vertices[aux[2]][2]]

            res = np.cross(vecA, vecB)
            normals[aux[1]][0] += res[0]
            normals[aux[1]][1] += res[1]
            normals[aux[1]][2] += res[2]

            normals[aux[2]][0] += res[0]
            normals[aux[2]][1] += res[1]
            normals[aux[2]][2] += res[2]

            normals[aux[3]][0] += res[0]
            normals[aux[3]][1] += res[1]
            normals[aux[3]][2] += res[2]
            # print(faces)
        norms = np.linalg.norm(normals, axis=1)
        normals = normals / norms[:, None]

        color = np.asarray(color)
        color = np.tile(color, (numVertices, 1))

        vertexData = np.concatenate((vertices, color), axis=1)
        vertexData = np.concatenate((vertexData, normals), axis=1)

        print(vertexData.shape)

        indices = []
        vertexDataF = []
        index = 0

        for face in faces:
            vertex = vertexData[face[0], :]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[1], :]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[2], :]
            vertexDataF += vertex.tolist()

            indices += [index, index + 1, index + 2]
            index += 3

        return bs.Shape(vertexDataF, indices)

  ## Replace with desired texture ##
def createDice():
    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
        #   positions         tex coords   normals
        # Z+: number 1
        -0.5, -0.5, 0.5, 0, 1 / 3, 0, 0, 1,
        0.5, -0.5, 0.5, 1 / 2, 1 / 3, 0, 0, 1,
        0.5, 0.5, 0.5, 1 / 2, 0, 0, 0, 1,
        -0.5, 0.5, 0.5, 0, 0, 0, 0, 1,

        # Z-: number 6
        -0.5, -0.5, -0.5, 1 / 2, 1, 0, 0, -1,
        0.5, -0.5, -0.5, 1, 1, 0, 0, -1,
        0.5, 0.5, -0.5, 1, 2 / 3, 0, 0, -1,
        -0.5, 0.5, -0.5, 1 / 2, 2 / 3, 0, 0, -1,

        # X+: number 5
        0.5, -0.5, -0.5, 0, 1, 1, 0, 0,
        0.5, 0.5, -0.5, 1 / 2, 1, 1, 0, 0,
        0.5, 0.5, 0.5, 1 / 2, 2 / 3, 1, 0, 0,
        0.5, -0.5, 0.5, 0, 2 / 3, 1, 0, 0,

        # X-: number 2
        -0.5, -0.5, -0.5, 1 / 2, 1 / 3, -1, 0, 0,
        -0.5, 0.5, -0.5, 1, 1 / 3, -1, 0, 0,
        -0.5, 0.5, 0.5, 1, 0, -1, 0, 0,
        -0.5, -0.5, 0.5, 1 / 2, 0, -1, 0, 0,

        # Y+: number 4
        -0.5, 0.5, -0.5, 1 / 2, 2 / 3, 0, 1, 0,
        0.5, 0.5, -0.5, 1, 2 / 3, 0, 1, 0,
        0.5, 0.5, 0.5, 1, 1 / 3, 0, 1, 0,
        -0.5, 0.5, 0.5, 1 / 2, 1 / 3, 0, 1, 0,

        # Y-: number 3
        -0.5, -0.5, -0.5, 0, 2 / 3, 0, -1, 0,
        0.5, -0.5, -0.5, 1 / 2, 2 / 3, 0, -1, 0,
        0.5, -0.5, 0.5, 1 / 2, 1 / 3, 0, -1, 0,
        -0.5, -0.5, 0.5, 0, 1 / 3, 0, -1, 0
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2, 2, 3, 0,  # Z+
        7, 6, 5, 5, 4, 7,  # Z-
        8, 9, 10, 10, 11, 8,  # X+
        15, 14, 13, 13, 12, 15,  # X-
        19, 18, 17, 17, 16, 19,  # Y+
        20, 21, 22, 22, 23, 20]  # Y-

    return bs.Shape(vertices, indices)
      # Convenience function to ease initialization


def createWillisTower(object):
  # Note: the vertex attribute layout (stride) is the same for the 3 lighting pipelines in
  # this case: flatPipeline, gouraudPipeline and phongPipeline. Hence, the VAO setup can
  # be the same.
  
  floor_108_1 = sg.SceneGraphNode("floor_108_1")
  floor_108_1.transform = tr.matmul([tr.translate(0, 0, 5.4/3), tr.scale(1/3, 1/3, 10.8/3)])
  floor_108_1.childs += [object]
  
  
  
  floor_108_2 = sg.SceneGraphNode("floor_108_2")
  floor_108_2.transform = tr.matmul([tr.translate(-1/3, 0, 5.4/3), tr.scale(1/3, 1/3, 10.8/3)])
  floor_108_2.childs += [object]
  
  floor_90_1 = sg.SceneGraphNode("floor_90_1")
  floor_90_1.transform = tr.matmul([tr.translate(0, 1/3, 4.5/3), tr.scale(1/3, 1/3, 9/3)])
  floor_90_1.childs += [object]
  
  floor_90_2 = sg.SceneGraphNode("floor_90_2")
  floor_90_2.transform = tr.matmul([tr.translate(1/3, 0, 4.5/3), tr.scale(1/3, 1/3, 9/3)])
  floor_90_2.childs += [object]
  
  floor_90_3 = sg.SceneGraphNode("floor_90_3")
  floor_90_3.transform = tr.matmul([tr.translate(0, -1/3, 4.5/3), tr.scale(1/3, 1/3, 9/3)])
  floor_90_3.childs += [object]
  
  floor_66_1 = sg.SceneGraphNode("floor_66_1")
  floor_66_1.transform = tr.matmul([tr.translate(1/3, 1/3, 3.3/3), tr.scale(1/3, 1/3, 6.6/3)])
  floor_66_1.childs += [object]
  
  floor_66_2 = sg.SceneGraphNode("floor_66_2")
  floor_66_2.transform = tr.matmul([tr.translate(-1/3, -1/3, 3.3/3), tr.scale(1/3, 1/3, 6.6/3)])
  floor_66_2.childs += [object]
  
  floor_50_1 = sg.SceneGraphNode("floor_50_1")
  floor_50_1.transform = tr.matmul([tr.translate(-1/3, 1/3, 2.5/3), tr.scale(1/3, 1/3, 5/3)])
  floor_50_1.childs += [object]
  
  floor_50_2 = sg.SceneGraphNode("floor_50_2")
  floor_50_2.transform = tr.matmul([tr.translate(1/3, -1/3, 2.5/3), tr.scale(1/3, 1/3, 5/3)])
  floor_50_2.childs += [object]
  
  willisTower = sg.SceneGraphNode("willisTower")
  willisTower.transform = tr.translate(0, 0, -1.5)
  willisTower.childs += [floor_108_1, floor_108_2, floor_90_1, floor_90_2, floor_90_3, floor_66_1, floor_66_2, floor_50_1, floor_50_2]
  
  return willisTower



def createEmpireState(object):
  block_1 = sg.SceneGraphNode("block_1")
  block_1.transform = tr.matmul([tr.translate(0, 0, 0.25/3), tr.scale(1, 0.5, 0.5/3)])
  block_1.childs += [object]
  
  block_2_1 = sg.SceneGraphNode("block_2_1")
  block_2_1.transform = tr.scale(0.65, 0.4, 2.4/3)
  block_2_1.childs += [object]
  
  
  block_2_2 = sg.SceneGraphNode("block_2_2")
  block_2_2.transform = tr.matmul([tr.translate(0.2, 0, -0.2/3), tr.scale(0.6/3, 0.45, 2.0/3)])
  block_2_2.childs += [object]
  
    
  block_2_3 = sg.SceneGraphNode("block_2_3")
  block_2_3.transform = tr.matmul([tr.translate(-0.2, 0, -0.2/3), tr.scale(0.6/3, 0.45, 2.0/3)])
  block_2_3.childs += [object]
  
  block_2_4 = sg.SceneGraphNode("block_2_4")
  block_2_4.transform = tr.matmul([tr.translate(0.3, 0, -0.3/3), tr.scale(0.35/2, 0.7/2, 1.8/3)])
  block_2_4.childs += [object]
  
    
  block_2_5 = sg.SceneGraphNode("block_2_5")
  block_2_5.transform = tr.matmul([tr.translate(-0.3, 0, -0.3/3), tr.scale(0.35/2, 0.7/2, 1.8/3)])
  block_2_5.childs += [object]
  

  block_2 = sg.SceneGraphNode("block_2")
  block_2.transform = tr.translate(0, 0, (0.5+1.2)/3)
  block_2.childs += [block_2_1, block_2_2, block_2_3, block_2_4, block_2_5]
  

  block_3_1 = sg.SceneGraphNode("block_3_1")
  block_3_1.transform = tr.scale(0.5, 0.3, 5.5/3)
  block_3_1.childs += [object]
  
  block_3_2 = sg.SceneGraphNode("block_3_2")
  block_3_2.transform = tr.matmul([tr.translate(0.2, 0, -0.25), tr.scale(0.6/3, 0.4, 4.0/3)])
  block_3_2.childs += [object]
  
  
  block_3_3 = sg.SceneGraphNode("block_3_3")
  block_3_3.transform = tr.matmul([tr.translate(-0.2, 0, -0.25), tr.scale(0.6/3, 0.4, 4.0/3)])
  block_3_3.childs += [object]
  
  
  block_3_4 = sg.SceneGraphNode("block_3_4")
  block_3_4.transform = tr.matmul([tr.translate(0.18, 0, 0.65), tr.scale(0.5/3, 0.4, 1.5/3)])
  block_3_4.childs += [object]
  
  
  block_3_5 = sg.SceneGraphNode("block_3_5")
  block_3_5.transform = tr.matmul([tr.translate(-0.18, 0, 0.65), tr.scale(0.5/3, 0.4, 1.5/3)])
  block_3_5.childs += [object]

  
  block_3 = sg.SceneGraphNode("block_3")
  block_3.transform = tr.translate(0, 0, (0.5+2.4+2.75)/3)
  block_3.childs += [block_3_1, block_3_2, block_3_3, block_3_4, block_3_5]
  
  
  block_4_1 = sg.SceneGraphNode("block_4_1")
  block_4_1.transform = tr.scale(0.5, 0.3, 0.6/3)
  block_4_1.childs += [object]
  
  
  block_4 = sg.SceneGraphNode("block_4")
  block_4.transform = tr.translate(0, 0, (0.5+2.4+5.5+0.3)/3)
  block_4.childs += [block_4_1]
  
  block_5_1 = sg.SceneGraphNode("block_5_1")
  block_5_1.transform = tr.scale(0.4, 0.2, 0.6/3)
  block_5_1.childs += [object]
  
  block_5 = sg.SceneGraphNode("block_5")
  block_5.transform = tr.translate(0, 0, (0.5+2.4+5.5+0.3+0.3)/3)
  block_5.childs += [block_5_1]
  
  pillar = sg.SceneGraphNode("pillar")
  pillar.transform = tr.matmul([tr.translate(0, 0, (0.5+2.4+5.5+0.3+0.3+1)/3), tr.scale(0.1, 0.1, 2/3)])
  pillar.childs += [object]
  
  
  lighting_rod = sg.SceneGraphNode("lighting_rod")
  lighting_rod.transform =tr.matmul([tr.translate(0, 0, (0.5+2.4+5.5+0.3+0.3+1+1+0.005)/3), tr.scale(0.01, 0.01, 2/3)])
  lighting_rod.childs += [object]
  
  
  
  empireState = sg.SceneGraphNode("empireState")
  empireState.transform = tr.translate(0, 0, -1.5)
  empireState.childs += [block_1, block_2, block_3, block_4, block_5, pillar, lighting_rod]
  
  return empireState
  
  
def createBurjAlArab(object):
  
  left_pillar = sg.SceneGraphNode("left_pillar")
  left_pillar.transform = tr.matmul([tr.translate(-0.1, -0.9, 2), tr.scale(0.1, 0.1, 12/3)])
  left_pillar.childs += [object]
  
  right_pillar = sg.SceneGraphNode("right_pillar")
  right_pillar.transform = tr.matmul([tr.translate(0.1, -0.9, 2), tr.scale(0.1, 0.1, 12/3)])
  right_pillar.childs += [object]  
  
  center_pillar = sg.SceneGraphNode("center_pillar")
  center_pillar.transform = tr.matmul([tr.translate(0, -1, 2), tr.scale(0.1, 0.1, 12/3)])
  center_pillar.childs += [object]  
  
  burjAlArab = sg.SceneGraphNode("burjAlArab")
  burjAlArab.transform = tr.translate(0, 0, -1.5)
  burjAlArab.childs += [left_pillar, right_pillar, center_pillar]
  
  return burjAlArab