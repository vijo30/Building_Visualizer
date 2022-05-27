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
import tarea2modelos as modelo
import grafica.scene_graph as sg

__author__ = "Daniel Calderon"
__license__ = "MIT"

LIGHT_FLAT = 0
LIGHT_GOURAUD = 1
LIGHT_PHONG = 2

VIEW_1 = 1
VIEW_2 = 2
VIEW_3 = 3
VIEW_4 = 4
VIEW_5 = 5

PERSPECTIVE = 0
ORTHOGRAPHIC = 1


WILLIS_TOWER = 0
EMPIRE_STATE = 1
BURJ_AL_ARAB = 2

def linear_interpol(t, a, b):
    return a * t + b * (1 - t)





#linear_interpol(time_frames[time_index],a,b)
# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = False
        self.lightingModel = LIGHT_PHONG
        self.view = VIEW_5
        self.projection = PERSPECTIVE
        self.day = True
        self.building = BURJ_AL_ARAB


# We will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):
    if action != glfw.PRESS:
        return

    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_LEFT_CONTROL:
        controller.showAxis = not controller.showAxis

    elif key == glfw.KEY_7:
        controller.lightingModel = LIGHT_FLAT

    elif key == glfw.KEY_8:
        controller.lightingModel = LIGHT_GOURAUD

    elif key == glfw.KEY_9:
        controller.lightingModel = LIGHT_PHONG
        
    elif key == glfw.KEY_P:
        controller.projection = PERSPECTIVE
        
    elif key == glfw.KEY_O:
        controller.projection = ORTHOGRAPHIC
        
    elif key == glfw.KEY_1:
        controller.view = VIEW_1
        
    elif key == glfw.KEY_2:
        controller.view = VIEW_2
        
    elif key == glfw.KEY_3:
        controller.view = VIEW_3
        
    elif key == glfw.KEY_4:
        controller.view = VIEW_4
        
    elif key == glfw.KEY_5:
        controller.view = VIEW_5
        
    elif key == glfw.KEY_L:
        controller.day = not controller.day
        glfw.set_time(0)
        
    elif key == glfw.KEY_W:
        controller.building = WILLIS_TOWER
        
    elif key == glfw.KEY_E:
        controller.building = EMPIRE_STATE
        
    elif key == glfw.KEY_B:
        controller.building = BURJ_AL_ARAB

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

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


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 1280
    height = 720

    window = glfw.create_window(width, height, "Homework 2C demo", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)
        
    # Resize window
    def window_resize(window, width, height):
        glViewport(0, 0, width, height)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)
    glfw.set_window_size_callback(window, window_resize)

    # Different shader programs for different lighting strategies
    textureFlatPipeline = ls.SimpleTextureFlatShaderProgram()
    textureGouraudPipeline = ls.SimpleTextureGouraudShaderProgram()
    texturePhongPipeline = ls.SimpleTexturePhongShaderProgram()

    # This shader program does not consider lighting
    colorPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)


    # Convenience function to ease initialization
    def createGPUShape(pipeline, shape):
        gpuShape = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuShape)
        gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
        return gpuShape


    # Creating shapes on GPU memory
    gpuAxis = createGPUShape(colorPipeline, bs.createAxis(4))

    # Note: the vertex attribute layout (stride) is the same for the 3 lighting pipelines in
    # this case: flatPipeline, gouraudPipeline and phongPipeline. Hence, the VAO setup can
    # be the same.
    shapeDice = createDice()
    gpuDice = createGPUShape(textureGouraudPipeline, shapeDice)
    gpuDice.texture = es.textureSimpleSetup(
        getAssetPath("dice2.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    
    willisTower = modelo.createWillisTower(gpuDice)


    # Since the only difference between both dices is the texture, we can just use the same
    # GPU data, but with another texture.
    # copy.deepcopy generate a true copy, so if we change gpuDiceBlue.texture (or any other
    # member), we will not change gpuDice.texture
    gpuDice3 = copy.deepcopy(gpuDice)
    gpuDice3.texture = es.textureSimpleSetup(
        getAssetPath("dice3.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

    empireState = modelo.createEmpireState(gpuDice3)
    
    gpuDice4 = copy.deepcopy(gpuDice)
    gpuDice4.texture = es.textureSimpleSetup(
        getAssetPath("dice4.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    
    
    
    burjAlArab = modelo.createBurjAlArab(gpuDice4, texturePhongPipeline)
    
    floor = modelo.create_floor(texturePhongPipeline)
    
    t0 = glfw.get_time()
    camera_theta = np.pi / 4
    cameraZ = 1

    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1
        
        time = min(t1/3,1)
        
        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2 * dt
            
        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
            cameraZ += 1 * dt
            
        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
            cameraZ -= 1 * dt        

        # Selecting projection
        if controller.projection == PERSPECTIVE:
          projection = tr.perspective(45, float(width) / float(height), 0.1, 100)
          
        elif controller.projection == ORTHOGRAPHIC:
          projection = tr.ortho(2 * -float(width) / float(height), 2 * float(width) / float(height), -2, 2, 0.1, 100)
          
        # Selecting view
        
        if controller.view == VIEW_1:
          camX = 0
          camY = 3
          camZ = 1
          viewPos = np.array([camX, camY, camZ])
          view = tr.lookAt(
            viewPos,
            np.array([0, 0, camZ]),
            np.array([0, 0, 1])
        )
          
        elif controller.view == VIEW_2:
          camX = 3 * np.sin(camera_theta)
          camY = 3 * np.cos(camera_theta)
          camZ = cameraZ
          viewPos = np.array([camX, camY, camZ])
          view = tr.lookAt(
            viewPos,
            np.array([0, 0, 0]),
            np.array([0, 0, 1])
        )
          
        elif controller.view == VIEW_3:
          camX = 1
          camY = 0
          camZ = 3
          viewPos = np.array([camX, camY, camZ])
          view = tr.lookAt(
            viewPos,
            np.array([0, 0, 0]),
            np.array([0, 0, 1])
        )
          
        elif controller.view == VIEW_4:
          camX = 0.00000001
          camY = 0.00000001
          camZ = 3
          viewPos = np.array([camX, camY, camZ])
          view = tr.lookAt(
            viewPos,
            np.array([0, 0, 0]),
            np.array([0, 0, 1])
        )
          
        elif controller.view == VIEW_5:
          camX = 3 * np.sin(camera_theta)
          camY = 3 * np.cos(camera_theta)
          camZ = cameraZ
          viewPos = np.array([camX, camY, camZ])
          view = tr.lookAt(
            viewPos,
            np.array([0, 0, camZ]),
            np.array([0, 0, 1])
        )


        #print(camX, camY, camZ)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # The axis is drawn without lighting effects
        if controller.showAxis:
            glUseProgram(colorPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            colorPipeline.drawCall(gpuAxis, GL_LINES)

        # Selecting the lighting shader program
        if controller.lightingModel == LIGHT_FLAT:
            lightingPipeline = textureFlatPipeline
        elif controller.lightingModel == LIGHT_GOURAUD:
            lightingPipeline = textureGouraudPipeline
        elif controller.lightingModel == LIGHT_PHONG:
            lightingPipeline = texturePhongPipeline
        else:
            raise Exception()

        glUseProgram(lightingPipeline.shaderProgram)         


        # Drawing
        
        if controller.building == WILLIS_TOWER:
          if controller.day:
              glClearColor(linear_interpol(time,135/255,42/255), linear_interpol(time,206/255,42/255), linear_interpol(time,235/255,53/255), 1.0) 
              
              #glClearColor(linear_interpol(time,42/255,135/255), linear_interpol(time,42/255,206/255), linear_interpol(time,53/255,235/255), 1.0)
              
              # Setting all uniform shader variables
              # linear_interpol(time_frames[time_index],0.1,1.0)
              # White light in all components: ambient, diffuse and specular.
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), linear_interpol(time,0.9,0.2), linear_interpol(time,0.94,0.2), linear_interpol(time,0.96,0.3))
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), linear_interpol(time,1.0,0.3), linear_interpol(time,1.0,0.3), linear_interpol(time,1.0,0.35))
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), linear_interpol(time,1.0,0.4), linear_interpol(time,1.0,0.4), linear_interpol(time,1.0,0.4))

              # Object is barely visible at only ambient. Bright white for diffuse and specular components.
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

              # TO DO: Explore different parameter combinations to understand their effect!

              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), 2, 2, 4)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1],
                          viewPos[2])
              glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)

              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)
          
          elif not controller.day:
              glClearColor(linear_interpol(time,42/255,135/255), linear_interpol(time,42/255,206/255), linear_interpol(time,53/255,235/255), 1.0)
              # Setting all uniform shader variables

              # White light in all components: ambient, diffuse and specular.
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), linear_interpol(time,0.2,0.9), linear_interpol(time,0.2,0.94), linear_interpol(time,0.3,0.96))
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), linear_interpol(time,0.3,1.0), linear_interpol(time,0.3,1.0), linear_interpol(time,0.35,1.0))
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), linear_interpol(time,0.4,1.0),  linear_interpol(time,0.4,1.0),  linear_interpol(time,0.4,1.0))

              # Object is barely visible at only ambient. Bright white for diffuse and specular components.
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

              # TO DO: Explore different parameter combinations to understand their effect!

              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), 2, 2, 4)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1],
                          viewPos[2])
              glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)

              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)
              


          
          ##
          glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
          glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)    
          sg.drawSceneGraphNode(willisTower, lightingPipeline, "model")
          sg.drawSceneGraphNode(floor, lightingPipeline, "model")
          
        elif controller.building == EMPIRE_STATE:
          if controller.day:
              glClearColor(linear_interpol(time,135/255,42/255), linear_interpol(time,206/255,42/255), linear_interpol(time,235/255,53/255), 1.0) 
              
              #glClearColor(linear_interpol(time,42/255,135/255), linear_interpol(time,42/255,206/255), linear_interpol(time,53/255,235/255), 1.0)
              
              # Setting all uniform shader variables
              # linear_interpol(time_frames[time_index],0.1,1.0)
              # White light in all components: ambient, diffuse and specular.
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), linear_interpol(time,0.9,0.2), linear_interpol(time,0.94,0.2), linear_interpol(time,0.96,0.3))
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), linear_interpol(time,1.0,0.3), linear_interpol(time,1.0,0.3), linear_interpol(time,1.0,0.35))
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), linear_interpol(time,1.0,0.4), linear_interpol(time,1.0,0.4), linear_interpol(time,1.0,0.4))

              # Object is barely visible at only ambient. Bright white for diffuse and specular components.
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

              # TO DO: Explore different parameter combinations to understand their effect!

              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), 2, 2, 4)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1],
                          viewPos[2])
              glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)

              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)
          
          elif not controller.day:
              glClearColor(linear_interpol(time,42/255,135/255), linear_interpol(time,42/255,206/255), linear_interpol(time,53/255,235/255), 1.0)
              # Setting all uniform shader variables

              # White light in all components: ambient, diffuse and specular.
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), linear_interpol(time,0.2,0.9), linear_interpol(time,0.2,0.94), linear_interpol(time,0.3,0.96))
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), linear_interpol(time,0.3,1.0), linear_interpol(time,0.3,1.0), linear_interpol(time,0.35,1.0))
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), linear_interpol(time,0.4,1.0),  linear_interpol(time,0.4,1.0),  linear_interpol(time,0.4,1.0))

              # Object is barely visible at only ambient. Bright white for diffuse and specular components.
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

              # TO DO: Explore different parameter combinations to understand their effect!

              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), 2, 2, 4)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1],
                          viewPos[2])
              glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)

              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)
              


          
          ##
          glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
          glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)    
          sg.drawSceneGraphNode(empireState, lightingPipeline, "model")
          sg.drawSceneGraphNode(floor, lightingPipeline, "model")
          
        elif controller.building == BURJ_AL_ARAB:
          if controller.day:
              glClearColor(linear_interpol(time,255/255,42/255), linear_interpol(time,229/255,42/255), linear_interpol(time,119/255,53/255), 1.0) 
              
              #glClearColor(linear_interpol(time,42/255,135/255), linear_interpol(time,42/255,206/255), linear_interpol(time,53/255,235/255), 1.0)
              
              # Setting all uniform shader variables
              # linear_interpol(time_frames[time_index],0.1,1.0)
              # White light in all components: ambient, diffuse and specular.
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), linear_interpol(time,0.99,0.2), linear_interpol(time,0.81,0.2), linear_interpol(time,0.27,0.3))
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), linear_interpol(time,1.0,0.3), linear_interpol(time,1.0,0.3), linear_interpol(time,1.0,0.35))
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), linear_interpol(time,1.0,0.4), linear_interpol(time,1.0,0.4), linear_interpol(time,1.0,0.4))

              # Object is barely visible at only ambient. Bright white for diffuse and specular components.
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

              # TO DO: Explore different parameter combinations to understand their effect!

              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), 2, 2, 4)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1],
                          viewPos[2])
              glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)

              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)
          
          elif not controller.day:
              glClearColor(linear_interpol(time,42/255,255/255), linear_interpol(time,42/255,229/255), linear_interpol(time,53/255,119/255), 1.0)
              # Setting all uniform shader variables

              # White light in all components: ambient, diffuse and specular.
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), linear_interpol(time,0.2,0.99), linear_interpol(time,0.2,0.81), linear_interpol(time,0.3,0.27))
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), linear_interpol(time,0.3,1.0), linear_interpol(time,0.3,1.0), linear_interpol(time,0.35,1.0))
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), linear_interpol(time,0.4,1.0),  linear_interpol(time,0.4,1.0),  linear_interpol(time,0.4,1.0))

              # Object is barely visible at only ambient. Bright white for diffuse and specular components.
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

              # TO DO: Explore different parameter combinations to understand their effect!

              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), 2, 2, 4)
              glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1],
                          viewPos[2])
              glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)

              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
              glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)
              


          
          ##
          glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
          glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)    
          sg.drawSceneGraphNode(burjAlArab, lightingPipeline, "model")
          sg.drawSceneGraphNode(floor, lightingPipeline, "model")

        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()
    gpuDice.clear()
    gpuDice3.clear()

    glfw.terminate()
