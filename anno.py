import pygame as pg
from pygame import *
from OpenGL.GL import *
from OpenGL.GLU import *
from rectangle import RectangleMesh
import os

class Background:
    def __init__(self, filepath): 
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(filepath).convert_alpha()
        image_data = pg.image.tostring(image, "RGBA", 1)
        self.image_width, self.image_height = image.get_size() # depends on the image loaded
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.image_width, self.image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    
    def destroy(self):
        glDeleteTextures([self.texture])
        
     # Function to render the background
    def render_background(self, window_width, window_height):
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)  # Set the orthographic projection
        
        glPushMatrix()
        
        alpha = 0.8
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        
        glColor4f(1.0, 1.0, 1.0, alpha)  # Set the color with alpha
        
        glTexCoord2f(0, 0); glVertex2f(0, 0)  # left bottom
        glTexCoord2f(0, 1); glVertex2f(0, window_height)  # left top
        glTexCoord2f(1, 1); glVertex2f(window_width, window_height)  # right top
        glTexCoord2f(1, 0); glVertex2f(window_width, 0)  # right bottom
        
        glEnd()
        glDisable(GL_TEXTURE_2D)
        
        glPopMatrix()
        
        glLoadIdentity() # Reset the model-view matrix
        gluPerspective(45, window_width/window_height, 0.1, 50) # Set the perspective projection


class App:
    
    def __init__(self):
        
        # initialize pygame for GUI
        pg.init() 
        screen_info = pg.display.Info()
        print(screen_info.current_w, screen_info.current_h)
        
        # get the base directory
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.dir_data = os.path.join(BASE_DIR, 'data')
                
        # Check if the directory exists, if not create it
        if not os.path.exists(self.dir_data):
            os.makedirs(self.dir_data)
        
        self.background_path = [] # list of background images in dir data/
        
        for file in os.listdir(self.dir_data):
            if file.endswith(".jpg") or file.endswith(".JPG"):
                self.background_path.append(os.path.join(self.dir_data, file))
        
        print("background path: ", self.background_path[0])
        self.count_background = 0
               
        img_width = pg.image.load(self.background_path[0]).get_width()
        img_height = pg.image.load(self.background_path[0]).get_height()
        print("image size: ", img_width, img_height)
        
        i=1
        while (img_width / i) > screen_info.current_w or (img_height / i) > screen_info.current_h:
            i+=1
        print("scale is ", i)
        print("the windw will be: ", img_width/i, img_height/i)
        
        self.screen_size_factor=i
        self.window_width= img_width/self.screen_size_factor
        self.window_height=img_height/self.screen_size_factor
        
        self.display = (int(self.window_width), int(self.window_height))
        
        self.screen = pg.display.set_mode(self.display, pg.OPENGL | pg.DOUBLEBUF) # tell pygame we run OPENGL & DOUBLEBUFFERING, one frame vis & one drawing
        pg.display.set_caption("Annotation Tool 3D")     
     
        # initialize OpenGL
        glClearColor(0,0,0,1) # set the color of the background
    
        glEnable(GL_BLEND) # enable blending
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) # set the blending function
        
        
        glMatrixMode(GL_PROJECTION) # activate projection matrix
        glLoadIdentity()

        gluPerspective(45, self.display[0]/self.display[1], 0.1, 50)
        glTranslatef(0, 0, -15)
        self.projectionmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        
        glMatrixMode(GL_MODELVIEW) # activate model view matrix
        glLoadIdentity()
        
        # gluLookAt(0, 0, 15, 0, 0, 0, 0, 1, 0)
        
        # draw wired rectangle
        self.rectangle = RectangleMesh(4, 2, 6, [0,0,0], [0,0,0]) 
        self.rectangle.draw_wired_rect()
        
        # Background
        self.background = Background(self.background_path[0])
        
        # Text
        self.font = pg.font.Font(None, 24)
        
        # Main loop
        self.mainLoop()
    
    def quit(self):
        self.background.destroy()
        pg.quit()

    def drawText(self, x, y, text, color=(0,255,0)):                                                
        textSurface = self.font.render(text, True, color).convert_alpha() # text, antialiasing, color
        textData = pg.image.tostring(textSurface, "RGBA", True)
        glWindowPos2d(x, y)
        glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

    def new_background(self, select):
        # Destroy the current background object
        self.background.destroy()
        del self.background
        
        # Calculate the new index based on the selection
        if select == "next":
            self.count_background = (self.count_background + 1) % len(self.background_path)
        elif select == "previous":
            self.count_background = (self.count_background - 1) % len(self.background_path)

        # Create the new background object based on the new index
        self.background = Background(self.background_path[self.count_background])
        
    
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
                    self.background.destroy()
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
                    
                    if (event.key == pg.K_n):
                        self.new_background("next")
                        print("next background")
                    
                    if (event.key == pg.K_p):
                        self.new_background("previous")
                        print("previous background")
                     
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
                
                # draw wired rectangle
                self.rectangle.draw_wired_rect()
                
            if load:
                
                # Render background
                self.background.render_background(self.window_width, self.window_height)
                
            # --- Text --- #
            self.drawText(self.window_width-100, self.window_height-100, f"Step: {round(step, 1) if step > 0.1 else step}")
            self.drawText(10, 50, f"Rotation x : {round(self.rectangle.eulers[0])}, y : {round(self.rectangle.eulers[1])}, z : {round(self.rectangle.eulers[2])}")
            self.drawText(10, 70, f"Translation x : {round(self.rectangle.position[0])}, y : {round(self.rectangle.position[1])}, z : {round(self.rectangle.position[2])}")
            self.drawText(10, 90, f"Dimension w : {round(self.rectangle.width)}, h : {round(self.rectangle.height)}, d : {round(self.rectangle.depth)}")
            self.drawText(10, self.window_height-40, f"image loaded: {self.background_path[self.count_background]}")
            
            # --- Update the screen --- #    
            pg.display.flip()
            pg.time.wait(10)
        

if __name__ == "__main__":
    app = App()
    