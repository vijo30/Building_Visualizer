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


def readFaceVertex(faceDescription):
    aux = faceDescription.split('/')

    assert len(aux[0]), "Vertex index has not been defined."

    faceVertex = [int(aux[0]), None, None]

    assert len(aux) == 3, "Only faces where its vertices require 3 indices are defined."

    if len(aux[1]) != 0:
        faceVertex[1] = int(aux[1])

    if len(aux[2]) != 0:
        faceVertex[2] = int(aux[2])

    return faceVertex


def readOBJ(filename):
    vertices = []
    normals = []
    textCoords = []
    faces = []

    with open(filename, 'r') as file:
        for line in file.readlines():
            aux = line.strip().split(' ')

            if aux[0] == 'v':
                vertices += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vn':
                normals += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vt':
                assert len(aux[1:]) == 2, "Texture coordinates with different than 2 dimensions are not supported"
                textCoords += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'f':
                N = len(aux)
                faces += [[readFaceVertex(faceVertex) for faceVertex in aux[1:4]]]
                for i in range(3, N - 1):
                    faces += [[readFaceVertex(faceVertex) for faceVertex in [aux[i], aux[i + 1], aux[1]]]]

        vertexData = []
        indices = []
        index = 0

        # Per previous construction, each face is a triangle
        for face in faces:

            # Checking each of the triangle vertices
            for i in range(0, 3):
                vertex = vertices[face[i][0] - 1]
                textCoord = textCoords[face[i][1] - 1]
                normal = normals[face[i][2] - 1]


                vertexData += [
                    vertex[0], vertex[1], vertex[2],
                    textCoord[0], textCoord[1],
                    normal[0], normal[1], normal[2]
                ]

            # Connecting the 3 vertices to create a triangle
            indices += [index, index + 1, index + 2]
            index += 3

        return bs.Shape(vertexData, indices)



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


def create_floor(pipeline):
    shapeFloor = bs.createTextureQuadWithNormal(8, 8)
    gpuFloor = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuFloor)
    gpuFloor.texture = es.textureSimpleSetup(
        getAssetPath("grass.jfif"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    gpuFloor.fillBuffers(shapeFloor.vertices, shapeFloor.indices, GL_STATIC_DRAW)

    floor = sg.SceneGraphNode("floor")
    floor.transform = tr.matmul([tr.translate(0, 0, -0.01-0.5),tr.scale(1, 1, 1)])
    floor.childs += [gpuFloor]

    return floor



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
  willisTower.transform = tr.matmul([tr.translate(0, 0, -0.5), tr.scale(0.5, 0.5, 0.5)])
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
  
  block_5_2 = sg.SceneGraphNode("block_5_2")
  block_5_2.transform = tr.matmul([tr.translate(0, 0, 0.4/3), tr.scale(0.3, 0.15, 0.2/3)])
  block_5_2.childs += [object]
     
  block_5_3 = sg.SceneGraphNode("block_5_3")
  block_5_3.transform = tr.matmul([tr.translate(0, 0, 0.5/3), tr.scale(0.2, 0.15, 0.1/3)])
  block_5_3.childs += [object]
  
  block_5 = sg.SceneGraphNode("block_5")
  block_5.transform = tr.translate(0, 0, (0.5+2.4+5.5+0.3+0.3)/3)
  block_5.childs += [block_5_1, block_5_2, block_5_3]
  
  
  pillar = sg.SceneGraphNode("pillar")
  pillar.transform = tr.matmul([tr.translate(0, 0, (0.5+2.4+5.5+0.3+0.3+1)/3), tr.scale(0.1, 0.1, 2/3)])
  pillar.childs += [object]
  
  
  lighting_rod = sg.SceneGraphNode("lighting_rod")
  lighting_rod.transform =tr.matmul([tr.translate(0, 0, (0.5+2.4+5.5+0.3+0.3+1+1+0.005)/3), tr.scale(0.01, 0.01, 2/3)])
  lighting_rod.childs += [object]
  
  
  
  empireState = sg.SceneGraphNode("empireState")
  empireState.transform = tr.matmul([tr.translate(0, 0, -0.5), tr.scale(0.5, 0.5, 0.5)])
  empireState.childs += [block_1, block_2, block_3, block_4, block_5, pillar, lighting_rod]
  
  return empireState
  
  
def createBurjAlArab(object, pipeline):
  
  shapeBase = readOBJ(getAssetPath('cilinder_triangle_base.obj'))
  gpuBase = createGPUShape(pipeline, shapeBase)
  gpuBase.texture = es.textureSimpleSetup(getAssetPath("dice5.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
  
  shape2Base = readOBJ(getAssetPath('bender_pillar.obj'))
  gpu2Base = createGPUShape(pipeline, shape2Base)
  gpu2Base.texture = es.textureSimpleSetup(getAssetPath("dice6.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
  
  
  left_pillar = sg.SceneGraphNode("left_pillar")
  left_pillar.transform = tr.matmul([tr.translate(-0.13, -0.4, 1.5), tr.rotationZ(-np.pi/3), tr.scale(0.2, 0.1, 9/3)])
  left_pillar.childs += [object]
  

  
  right_pillar = sg.SceneGraphNode("right_pillar")
  right_pillar.transform = tr.matmul([tr.translate(0.13, -0.4, 1.5), tr.rotationZ(np.pi/3), tr.scale(0.2, 0.1, 9/3)])
  right_pillar.childs += [object]  
  

  
  center_pillar = sg.SceneGraphNode("center_pillar")
  center_pillar.transform = tr.matmul([tr.translate(0, -0.5, 7/6), tr.scale(0.1, 0.1, 7/3)])
  center_pillar.childs += [object]  
  
  center_pillar2 = sg.SceneGraphNode("center_pillar2")
  center_pillar2.transform = tr.matmul([tr.translate(0, -0.5, (5/6)+7/3), tr.scale(0.05, 0.05, 5/3)])
  center_pillar2.childs += [object]  
    
  
  
  horizontal_left1 = sg.SceneGraphNode("horizontal_left1")
  horizontal_left1.transform = tr.matmul([tr.translate(-0.03, np.sqrt(3)*0.03+0.3, 0), tr.rotationZ(-np.pi/3), tr.scale(1.0, 0.05, 0.05)])
  horizontal_left1.childs += [object] 
  
    
  horizontal_left2 = sg.SceneGraphNode("horizontal_left2")
  horizontal_left2.transform = tr.matmul([tr.translate(-0.025, np.sqrt(3)*+0.025+0.3, 9/12), tr.rotationZ(-np.pi/3), tr.scale(0.9, 0.05, 0.05)])
  horizontal_left2.childs += [object]
    
  horizontal_left3 = sg.SceneGraphNode("horizontal_left3")
  horizontal_left3.transform = tr.matmul([tr.translate(0.03, np.sqrt(3)*-0.03+0.3, 2*9/12), tr.rotationZ(-np.pi/3), tr.scale(0.65, 0.05, 0.05)])
  horizontal_left3.childs += [object]
   
  horizontal_right1 = sg.SceneGraphNode("horizontal_right1")
  horizontal_right1.transform = tr.matmul([tr.translate(0.015, np.sqrt(3)*0.015+0.3, 0), tr.rotationZ(np.pi/3), tr.scale(1.1, 0.05, 0.05)])
  horizontal_right1.childs += [object] 
  
    
  horizontal_right2 = sg.SceneGraphNode("horizontal_right2")
  horizontal_right2.transform = tr.matmul([tr.translate(0.025, np.sqrt(3)*0.025+0.3, 9/12), tr.rotationZ(np.pi/3), tr.scale(0.9, 0.05, 0.05)])
  horizontal_right2.childs += [object]
    
  horizontal_right3 = sg.SceneGraphNode("horizontal_right3")
  horizontal_right3.transform = tr.matmul([tr.translate(-0.03, np.sqrt(3)*-0.03+0.3, 2*9/12), tr.rotationZ(np.pi/3), tr.scale(0.65, 0.05, 0.05)])
  horizontal_right3.childs += [object]
     
    
  horizontal_left = sg.SceneGraphNode("horizontal_left")
  horizontal_left.transform = tr.translate(-0.3-0.05, -0.3, 9/12)
  horizontal_left.childs += [horizontal_left1, horizontal_left2, horizontal_left3]
  
  horizontal_right = sg.SceneGraphNode("horizontal_right")
  horizontal_right.transform = tr.translate(0.3+0.05, -0.3, 9/12)
  horizontal_right.childs += [horizontal_right1, horizontal_right2, horizontal_right3]
  
  base = sg.SceneGraphNode("base")
  base.transform = tr.matmul([tr.translate(0, 0, 1.2), tr.rotationX(np.pi/2), tr.scale(0.5, 1.2, 0.5)])
  base.childs += [gpuBase]
  
  pillar = sg.SceneGraphNode("pillar")
  pillar.transform = tr.matmul([tr.translate(-0.28-0.35, -0.28*-np.sqrt(3), 0.88), tr.rotationZ(-np.pi/3), tr.rotationX(np.pi/2), tr.scale(0.35, 0.35, 0.25)])
  pillar.childs += [gpu2Base]
  
  pillar2 = sg.SceneGraphNode("pillar2")
  pillar2.transform = tr.matmul([tr.translate(0.28+0.35, -0.28*-np.sqrt(3), 0.88), tr.rotationZ(np.pi+np.pi/3), tr.rotationX(np.pi/2), tr.scale(0.35, 0.35, 0.25)])
  pillar2.childs += [gpu2Base]
  
  quad = sg.SceneGraphNode("quad")
  quad.transform = tr.matmul([tr.translate(0, -0.5, 3*9/12), tr.scale(0.6, 0.2, 0.1)])
  quad.childs += [object]
  
  burjAlArab = sg.SceneGraphNode("burjAlArab")
  burjAlArab.transform = tr.matmul([tr.translate(0, 0, -0.5), tr.scale(0.5, 0.5, 0.5)])
  burjAlArab.childs += [left_pillar, right_pillar, center_pillar, center_pillar2, horizontal_left, horizontal_right, base, pillar, pillar2, quad]
  

  
  return burjAlArab