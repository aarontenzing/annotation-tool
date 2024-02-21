import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *

class Background:
    def __init__(self, filepath):
        self.image = pg.image.load(filepath).convert_alpha()
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image_data = pg.image.tostring(self.image, "RGBA", 1)
        self.width, self.height = self.image.get_size()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    def render(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(-1, -1)
        glTexCoord2f(1, 0)
        glVertex2f(1, -1)
        glTexCoord2f(1, 1)
        glVertex2f(1, 1)
        glTexCoord2f(0, 1)
        glVertex2f(-1, 1)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def destroy(self):
        glDeleteTextures([self.texture])

# Usage example:
# Initialize Pygame
pg.init()
display = (512, 512)
screen = pg.display.set_mode(display, pg.OPENGL | pg.DOUBLEBUF)
pg.display.set_caption("Transparent Background")

# Initialize OpenGL
glClearColor(0.0, 0.0, 0.0, 0.0)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(-1.0, 1.0, -1.0, 1.0)

# Create a background object
background = Background("data\\IMG_0587.JPG")  # Replace "background.png" with your image file path

# Main loop
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    glClear(GL_COLOR_BUFFER_BIT)
    background.render()
    pg.display.flip()

# Clean up
background.destroy()
pg.quit()
