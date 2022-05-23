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
  floor_108_1.transform = tr.matmul([tr.translate(0, 0, 5.4), tr.scale(1/3, 1/3, 10.8)])
  floor_108_1.childs += [object]
  
  floor_108_2 = sg.SceneGraphNode("floor_108_2")
  floor_108_2.transform = tr.matmul([tr.translate(-1/3, 0, 5.4), tr.scale(1/3, 1/3, 10.8)])
  floor_108_2.childs += [object]
  
  floor_90_1 = sg.SceneGraphNode("floor_90_1")
  floor_90_1.transform = tr.matmul([tr.translate(0, 1/3, 4.5), tr.scale(1/3, 1/3, 9)])
  floor_90_1.childs += [object]
  
  floor_90_2 = sg.SceneGraphNode("floor_90_2")
  floor_90_2.transform = tr.matmul([tr.translate(1/3, 0, 4.5), tr.scale(1/3, 1/3, 9)])
  floor_90_2.childs += [object]
  
  floor_90_3 = sg.SceneGraphNode("floor_90_3")
  floor_90_3.transform = tr.matmul([tr.translate(0, -1/3, 4.5), tr.scale(1/3, 1/3, 9)])
  floor_90_3.childs += [object]
  
  floor_66_1 = sg.SceneGraphNode("floor_66_1")
  floor_66_1.transform = tr.matmul([tr.translate(1/3, 1/3, 3.3), tr.scale(1/3, 1/3, 6.6)])
  floor_66_1.childs += [object]
  
  floor_66_2 = sg.SceneGraphNode("floor_66_2")
  floor_66_2.transform = tr.matmul([tr.translate(-1/3, -1/3, 3.3), tr.scale(1/3, 1/3, 6.6)])
  floor_66_2.childs += [object]
  
  floor_50_1 = sg.SceneGraphNode("floor_50_1")
  floor_50_1.transform = tr.matmul([tr.translate(-1/3, 1/3, 2.5), tr.scale(1/3, 1/3, 5)])
  floor_50_1.childs += [object]
  
  floor_50_2 = sg.SceneGraphNode("floor_50_2")
  floor_50_2.transform = tr.matmul([tr.translate(1/3, -1/3, 2.5), tr.scale(1/3, 1/3, 5)])
  floor_50_2.childs += [object]
  
  willisTower = sg.SceneGraphNode("willisTower")
  willisTower.transform = tr.translate(0,0,-3)
  willisTower.childs += [floor_108_1, floor_108_2, floor_90_1, floor_90_2, floor_90_3, floor_66_1, floor_66_2, floor_50_1, floor_50_2]
  
  return willisTower