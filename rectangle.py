from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import itertools

class RectangleMesh:

    def __init__(self, width, height, depth, eulers, position):
            
        self.width = width
        self.height = height
        self.depth = depth
        self.eulers= np.array(eulers, dtype=np.float32) # angle
        self.position= np.array(position, dtype=np.float32) # position
        self.center = (0,0,0,0) # drew rect around (0,0,0)
        self.modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        
        # Cube vertices and edges
        self.vertices = (
            (self.width / 2.0,  self.height / 2.0,  self.depth / 2.0),  # top right back
            (-self.width / 2.0, self.height / 2.0, self.depth / 2.0),  # top left back
            (-self.width / 2.0, -self.height / 2.0, self.depth / 2.0),  # bottom left back
            (self.width / 2.0, -self.height / 2.0, self.depth / 2.0),  # bottom right back
            (self.width / 2.0, self.height / 2.0, -self.depth / 2.0),  # top right front
            (-self.width / 2.0, self.height / 2.0, -self.depth / 2.0),  # top left front
            (-self.width / 2.0, -self.height / 2.0, -self.depth / 2.0),  # bottom left front
            (self.width / 2.0, -self.height / 2.0, -self.depth / 2.0)   # bottom right front
        )

        self.edges = (
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7)
        )
    
    def set_translation(self, pos_x, pos_y , pos_z):
        self.position = np.array((pos_x, pos_y, pos_z), dtype=np.float32)
    
    def set_rotation(self, rot_x, rot_y, rot_z):
        self.eulers = np.array((rot_x, rot_y, rot_z), dtype=np.float32)

    def set_vertices(self, width, height, depth):
        self.vertices = (
            (width / 2.0,  height / 2.0,  depth / 2.0),   # top right back
            (-width / 2.0, height / 2.0,  depth / 2.0),   # top left back
            (-width / 2.0, -height / 2.0, depth / 2.0),   # bottom left back
            (width / 2.0,  -height / 2.0, depth / 2.0),   # bottom right back
            (width / 2.0,  height / 2.0, -depth / 2.0),   # top right front
            (-width / 2.0, height / 2.0, -depth / 2.0),   # top left front
            (-width / 2.0, -height / 2.0, -depth / 2.0),  # bottom left front
            (width / 2.0,  -height / 2.0, -depth / 2.0)   # bottom right front
        )
    
    def translate(self, direction, step=1):
        
        if (direction == 'reset'):
            self.position = np.array((0,0,0), dtype=np.float32)
        
        elif (direction == 'up'):
            self.position[1] += step
            
        elif (direction == 'down'):
            self.position[1] -= step
            
        elif (direction == 'left'):
            self.position[0] -= step
            
        elif (direction == 'right'):
            self.position[0] += step
            
        elif (direction == 'forward'):
            self.position[2] += step
        
        elif (direction == 'backward'):
            self.position[2] -= step
        
    def rotate(self, direction, step=1):
        
        if (direction == 'reset'):
            self.eulers = np.array((0,0,0), dtype=np.float32)
        
        elif (direction == 'x'):
            self.eulers[0] += step
            
        elif (direction == 'y'):
            self.eulers[1] += step
            
        elif (direction == 'z'):
            self.eulers[2] += step 

    
    def set_dimension(self, w, h, d):
        self.width = w
        self.height = h
        self.depth = d
        self.set_vertices(self.width, self.height, self.depth)
    
    
    def draw_wired_rect(self, orientation_matrix=None, translation_matrix=None):
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix() 
        glLoadIdentity()

        glTranslatef(self.position[0], self.position[1], self.position[2])
        
        if orientation_matrix is not None:

            glRotatef(orientation_matrix[0], 1, 0, 0)
            glRotatef(orientation_matrix[1], 0, 1, 0)
            glRotatef(orientation_matrix[2], 0, 0, 1)
            glTranslatef(translation_matrix[0], translation_matrix[1], -translation_matrix[2])
                
        glRotatef(self.eulers[0], 1, 0, 0)
        glRotatef(self.eulers[1], 0, 1, 0)
        glRotatef(self.eulers[2], 0, 0, 1) 
        
        glEnable(GL_LINE_SMOOTH)  # Enable line smoothing
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)  # Use the highest quality for line smoothing
        glLineWidth(2)
        
        glBegin(GL_LINES)
        glColor3f(0.0, 1.0, 0.0)  
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()
        
        self.modelview = glGetDoublev(GL_MODELVIEW_MATRIX) # save the modelview matrix 
        
        glPopMatrix()

    # Given a matrix, function will transform to matrix for OpenGL
    def RotMult_matrix(self, matrix):  
        identity_matrix = np.eye(4)
        identity_matrix[:3, :3] = matrix
        flattend_matrix = identity_matrix.flatten()
        # glLoadMatrixf(flattend_matrix)
        return flattend_matrix

    def get_norm_dim(self):
        # normalize dimensions
        w = self.width / self.height
        h = 1
        d = self.depth / self.height
        return [w,h,d]