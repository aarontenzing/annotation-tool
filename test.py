import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def load_texture(filepath):
    image = pygame.image.load(filepath).convert_alpha()
    image_data = pygame.image.tostring(image, "RGBA", 1)
    width, height = image.get_width(), image.get_height()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    return texture_id, width, height

def draw_background(texture_id, width, height):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)
    glColor4f(1.0, 1.0, 1.0, 0.5)  # Set the color with alpha
        
    glTexCoord2f(0, 0); glVertex3f(-width/2, -height/2, 0) # left bottom
    
    glTexCoord2f(0, 1); glVertex3f(-width/2, height/2, 0) # left top
    
    glTexCoord2f(1, 1); glVertex3f(width/2, height/2, 0) # right top
    
    glTexCoord2f(1, 0); glVertex3f(width/2, -height/2, 0) # right bottom
    glEnd()
    glDisable(GL_TEXTURE_2D)

def main():
    pygame.init()
    display = (1368, 912)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    texture_id, width, height = load_texture("data/IMG_0587.JPG")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_background(texture_id, width, height)
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()

