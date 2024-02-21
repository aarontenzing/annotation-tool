import pygame as pg
from pygame import *
from OpenGL.GL import *
from OpenGL.GLU import *
from rectangle import RectangleMesh
import os

class Background():
    def __init__(self,  filepath):
        self.texture=glGenTextures(1) # Texture handle
        glBindTexture(GL_TEXTURE_2D, self.texture)  # Bind the texture
        
        # Set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT) # horizontal
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)  # vertical
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST) # downsample img
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)  # upscale linearly
        
        # Load the image
        image=pg.image.load(filepath).convert_alpha()
        image_width, image_height= image.get_rect().size
        image_data=pg.image.tostring(image, "RGBA")
        
        # Generate the texture
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        
    def destroy(self):
        glDeleteTextures(1, (self.texture,))
    

class App:
    
    def __init__(self):
        
        # initialize pygame for GUI
        pg.init() 
        self.display = (512,512)
        self.screen = pg.display.set_mode(self.display, pg.OPENGL|pg.DOUBLEBUF) # tell pygame we run OPENGL & DOUBLEBUFFERING, one frame vis & one drawing
        pg.display.set_caption("Wireframe generator")
            
        # get the base directory
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.dir_data = os.path.join(BASE_DIR, 'data')
            
        # Check if the directory exists, if not create it
        if not os.path.exists(self.dir_data):
            os.makedirs(self.dir_data)
                
        # initialize OpenGL
        glClearColor(0,0,0,1) # set the color of the background
        glMatrixMode(GL_PROJECTION) # activate projection matrix
        glLoadIdentity()
        glEnable(GL_BLEND) # enable blending
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) # set the blending function
        gluPerspective(45, self.display[0]/self.display[1], 0.1, 50)
        self.projectionmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        
        glMatrixMode(GL_MODELVIEW) # activate model view matrix
        glLoadIdentity()
        gluLookAt(0, 0, 15, 0, 0, 0, 0, 1, 0)
        
        
        # draw wired rectangle
        self.rectangle = RectangleMesh(4, 2, 6, [0,0,0], [0,0,0]) 
        self.rectangle.draw_wired_rect()
        
        # Text
        self.font = pg.font.Font(None, 24)
        
        # Main loop
        self.mainLoop()
    
    def quit(self):
        pg.quit()

    def drawText(self, x, y, text, color=(255,255,255)):                                                
        textSurface = self.font.render(text, True, color).convert_alpha() # text, antialiasing, color
        textData = pg.image.tostring(textSurface, "RGBA", True)
        glWindowPos2d(x, y)
        glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)
    
    # Function to render the background
    def render_background(self, background):
        background.use()
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
    
    def mainLoop(self):
        
        draw = True
        load = False
        step = 1
        
        running = True
        while running:
            # Event handling
            for event in pg.event.get():
                
                if event.type == pg.QUIT:
                    running = False
                    self.quit()
                
                # key pressed
                if (event.type == pg.KEYDOWN):
                    
                    if (event.key == pg.K_e):
                        draw = not draw
                    
                    if (event.key == pg.K_s):
                        if (event.mod & pg.KMOD_CAPS or event.mod & pg.KMOD_SHIFT):
                            if (step < 0.1):
                                step *= 2
                            else:
                                step += 0.1
                            print('Step decrement: ', float(step))
                        else: 
                            step /= 2
                            print('Step increment: ', float(step))
                    
                    if (event.key == pg.K_l):
                        load = not load
                    
                    if (event.key == pg.K_r):
                        if (event.mod & pg.KMOD_CAPS or event.mod & pg.KMOD_SHIFT):
                            self.rectangle.rotate('reset')
                        else:
                            self.rectangle.translate('reset')    
                    
                    if (event.key == pg.K_1):
                        self.rectangle.dimension('reset')
                        print("reset dimension (1, 1, 1)") 
                        
                    # Dimension
                    if (event.key == pg.K_w):
                        if (event.mod & pg.KMOD_CAPS or event.mod & pg.KMOD_SHIFT):
                            self.rectangle.dimension('w', -step)
                        else:
                            self.rectangle.dimension('w', step)
                    if (event.key == pg.K_h):
                        if (event.mod & pg.KMOD_CAPS or event.mod & pg.KMOD_SHIFT):
                            self.rectangle.dimension('h', -step)
                        else:
                            self.rectangle.dimension('h', step)
                    
                    if (event.key == pg.K_d):
                        if (event.mod & pg.KMOD_CAPS or event.mod & pg.KMOD_SHIFT):
                            self.rectangle.dimension('d', -step)
                        else:
                            self.rectangle.dimension('d', step)
                                           
                    
                    # Translation
                    if (event.key == pg.K_UP):
                        self.rectangle.translate('up', step)
                    
                    if (event.key == pg.K_DOWN):
                        self.rectangle.translate('down', step)
                        
                    if (event.key == pg.K_LEFT):
                        self.rectangle.translate('left', step)
                    
                    if (event.key == pg.K_RIGHT):
                        self.rectangle.translate('right', step)
                    
                    if (event.key == pg.K_PAGEUP):
                        self.rectangle.translate('forward', step)
                    
                    if (event.key == pg.K_PAGEDOWN):
                        self.rectangle.translate('backward', step)
                    
                    # Rotation
                    if (event.key == pg.K_x):
                        if (event.mod & pg.KMOD_CAPS or event.mod & pg.KMOD_SHIFT):
                            self.rectangle.rotate('x', -step)   
                        else :
                            self.rectangle.rotate('x', step)
                    
                    if (event.key == pg.K_y):
                        if (event.mod & pg.KMOD_CAPS or event.mod & pg.KMOD_SHIFT):
                            self.rectangle.rotate('y', -step)   
                        else :
                            self.rectangle.rotate('y', step)
                    
                    if (event.key == pg.K_z):
                        if (event.mod & pg.KMOD_CAPS or event.mod & pg.KMOD_SHIFT):
                            self.rectangle.rotate('z', -step)   
                        else :
                            self.rectangle.rotate('z', step)
                    

            # --- Drawing the scene --- #
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            if draw:
                
                
                self.rectangle.draw_wired_rect()
                
            
            # --- Text --- #
            self.drawText(420, 480, f"Step: {round(step, 1) if step > 0.1 else step}")
            self.drawText(150, 50, f"Rotation x : {round(self.rectangle.eulers[0])}, y : {round(self.rectangle.eulers[1])}, z : {round(self.rectangle.eulers[2])}")
            self.drawText(150, 70, f"Translation x : {round(self.rectangle.position[0])}, y : {round(self.rectangle.position[1])}, z : {round(self.rectangle.position[2])}")
            self.drawText(150, 90, f"Dimension w : {round(self.rectangle.width)}, h : {round(self.rectangle.height)}, d : {round(self.rectangle.depth)}")
            
            # --- Update the screen --- #    
            pg.display.flip()
            pg.time.wait(10)

if __name__ == "__main__":
    app = App()
    