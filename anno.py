import pygame as pg
from pygame import *
from OpenGL.GL import *
from OpenGL.GLU import *
from rectangle import RectangleMesh
import os
from handle_json import *
import pprint

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
        
        # Save the current matrix state
        glPushMatrix()
        
        # Switch to the projection matrix mode and set up the orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()  # Reset the projection
        gluOrtho2D(0, window_width, 0, window_height)  # Set the orthographic projection
        
        # Switch back to the model-view matrix mode
        glMatrixMode(GL_MODELVIEW)
        
        # Render the background
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
        
        # Restore the previous matrix state
        glPopMatrix()
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, window_width/window_height, 0.1, 200) # Set the perspective projection
        glTranslatef(0.0,0.0, -60)
        

class App:
    
    def __init__(self, boxSize=None):
        
        # -- initialize pygame for GUI --
        pg.init() 
        self.screen_info = pg.display.Info()
        print(self.screen_info.current_w, self.screen_info.current_h)
        
        # -- Read backgrounds from data/ --
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.dir_data = os.path.join(BASE_DIR, 'data')
        
        if not os.path.exists(self.dir_data):
            os.makedirs(self.dir_data)
        
        self.background_path = [] # list of background images 
        self.image_name = []
        
        if boxSize is None:
            self.boxSize = [1,1,1]
        else:
            self.boxSize = boxSize
        
        for file in os.listdir(self.dir_data):
            if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".PNG"):
                self.image_name.append(file)
                self.background_path.append(os.path.join(self.dir_data, file))
        
        print("background path: ", self.background_path[0])
        self.count_background = 0

        img_width = pg.image.load(self.background_path[0]).get_width()
        img_height = pg.image.load(self.background_path[0]).get_height()
        print("image size: ", img_width, img_height)
        
        # -- Creating window with appropriate size --
        scale = self.calculateWindowRatio(img_width, img_height)
        self.changeWindowSize(scale, img_width, img_height)
        pg.display.set_caption("Annotation Tool 3D")     

        # -- Initialize OpenGL --
        glClearColor(0,0,0,1) # set the color of the background
    
        glEnable(GL_BLEND) # enable blending
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) # set the blending function
        
        # -- Projection matrix --
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.display[0]/self.display[1], 0.1, 200)
        # glTranslatef(0.0,0.0, -50)
        # gluLookAt(0, 0, 15, 0, 0, 0, 0, 1, 0)
        self.projectionmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        print("Initial PJM: \n",self.projectionmatrix)
        
        # - Modelview matrix --
        glMatrixMode(GL_MODELVIEW) 
        glLoadIdentity()
        
        # -- Setting background --
        self.background = Background(self.background_path[0])
        
        # -- Draw wired rectangle --
        self.rectangle = RectangleMesh(self.boxSize[0], self.boxSize[1], self.boxSize[2], [0,0,0], [0,0,0])
        self.rectangle.draw_wired_rect()
        
        # -- Text --
        self.font = pg.font.Font(None, 24)
        
        self.orientation_matrix = None
        
        # -- Main loop --
        self.mainLoop()
 
    
    def quit(self):
        self.background.destroy()
        pg.quit()


    def drawText(self, x, y, text, color=(0,255,0)):                                                
        textSurface = self.font.render(text, True, color).convert_alpha() # text, antialiasing, color
        textData = pg.image.tostring(textSurface, "RGBA", True)
        glWindowPos2d(x, y)
        glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)


    def calculateWindowRatio(self, img_width : int, img_height : int) -> int:
        scale = 1
        print(img_width, img_height)
        while (img_width/scale) > 1920 or (img_height/scale) > 1080:
            scale += 1
        return scale


    def changeWindowSize(self, ratio : int, background_width, background_height):
        print("new ratio: ", ratio)
        self.screen_size_factor = ratio
        self.window_width = background_width/ratio
        self.window_height = background_height/ratio
        self.display = (int(self.window_width), int(self.window_height))
        print("change window size: ", self.screen_size_factor, self.display)
        self.screen = pg.display.set_mode(self.display, pg.OPENGL | pg.DOUBLEBUF) # tell pygame we run OPENGL & DOUBLEBUFFERING, one frame vis & one drawing


    def new_background(self, select): # select = "next" or "previous"

        # Destroy the current background object
        shape = (self.background.image_width, self.background.image_height) # get the size of the current background image
        self.background.destroy()
        del self.background
        
        # Calculate the new index based on the selection
        if select == "next":
            self.count_background = (self.count_background + 1) % len(self.background_path)
        elif select == "previous":
            self.count_background = (self.count_background - 1) % len(self.background_path)

        # Create the new background object based on the new index
        new_back = pg.image.load(self.background_path[self.count_background])
        img_width, img_height = new_back.get_size()
        
        # different image dimensions -> calculate new window
        if (shape != (img_width, img_height)):
            self.changeWindowSize(self.calculateWindowRatio(img_width, img_height), img_width, img_height)
            self.background = Background(self.background_path[self.count_background])
            print(f"new window dimensions, {self.window_width, self.window_height}")
        else:
            # create back
            self.background = Background(self.background_path[self.count_background])


    def get_annotations(self, model_view, projection, viewport):
        # Calculate world and pixel coordinates of vertices rectangle
        world_coordinates = []
        pixel_coordinates = []
        
        for vertex in self.rectangle.vertices:
            x_screen, y_screen, _ =  gluProject(vertex[0], vertex[1], vertex[2], model_view, projection, viewport)
            pixel_coordinates.append((int(x_screen),int(y_screen)))
            x_world, y_world, z_world = gluUnProject( x_screen, y_screen, 0, model_view, projection, viewport)
            world_coordinates.append((x_world, y_world, z_world))
        
        # Calculate center
        x_screen, y_screen, _ = gluProject(0, 0, 0, model_view, projection, viewport)
        x_world, y_world, z_world = gluUnProject( x_screen, y_screen, 0, model_view, projection, viewport)
        world_coordinates.append((x_world, y_world, z_world))
        pixel_coordinates.append((int(x_screen), int(y_screen)))
        
        print(self.screen_size_factor)
        pixel_coordinates = [(x*self.screen_size_factor, y*self.screen_size_factor) for x,y in pixel_coordinates]
        
        print("pixel coordinates: ", pixel_coordinates)
        print("world coordinates: ", world_coordinates)
        
        return world_coordinates, pixel_coordinates
             

    def draw_axis(self):
        
        glPushMatrix()
        glTranslatef(0,0,-15)
        # X axis (red)
        glBegin(GL_LINES)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(5, 0, 0)
        glEnd()

        # Y axis (green)
        glBegin(GL_LINES)
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 5, 0)
        glEnd()

        # Z axis (blue)
        glBegin(GL_LINES)
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 5)
        glEnd()   
        glPopMatrix()  



    def mainLoop(self):
        
        draw = True
        load = True
        step = 5
        
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
                    
                    if (event.key == pg.K_i):
                        print("current PJM: \n", glGetDoublev(GL_PROJECTION_MATRIX))
                        print("current MVM: \n", self.rectangle.modelview)
                    
                    if (event.key == K_SPACE):
                        step = 10
                        
                    if (event.key == pg.K_e):
                        draw = not draw
                    
                    if (event.key == pg.K_a):
                        wc, pc = self.get_annotations(self.rectangle.modelview, glGetDoublev(GL_PROJECTION_MATRIX), glGetIntegerv(GL_VIEWPORT)) # world coordinates and pixel coordinates
                        write_json("annotations.json",self.image_name[self.count_background],wc, pc)
                    
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
                        if load:
                            print(self.image_name[self.count_background])
                            data = read_json("pnp_anno.json")
                            
                            for item in data:
                                if item["img_name"] == ("data\\" + self.image_name[self.count_background]):
                                    # print("annotations loaded!")
                                    print("world cord: ",item["orientation"])
                                    orientation = item["orientation"]    
                                    break
                            if (orientation is None):
                                print("not quick_annotated yet")
                            
                            # Create orientation matrix
                            self.orientation_matrix = self.rectangle.RotMult_matrix(orientation)
                            # Apply the orientation matrix
                            self.rectangle.draw_wired_rect(self.orientation_matrix)  
                                
                        else:
                            print("No annotations found.")
                    
                    if (event.key == pg.K_r):
                        if (event.mod & pg.KMOD_CAPS or event.mod & pg.KMOD_SHIFT):
                            self.rectangle.rotate('reset')
                        else:
                            self.rectangle.translate('reset')    
                    
                    if (event.key == pg.K_n):
                        self.new_background("next")
                        print("next background")
                    
                    if (event.key == pg.K_p):
                        self.new_background("previous")
                        print("previous background")
                     
                        
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
            
            self.draw_axis()
            
            if draw:    
                # draw wired rectangle
                self.rectangle.draw_wired_rect(self.orientation_matrix)
                # Render background
                self.background.render_background(self.window_width, self.window_height)
                
            # --- Text --- #
            self.drawText(self.window_width-100, self.window_height-100, f"Step: {round(step, 1) if step > 0.1 else step}")
            self.drawText(10, 50, f"Rotation x : {round(self.rectangle.eulers[0])}, y : {round(self.rectangle.eulers[1])}, z : {round(self.rectangle.eulers[2])}")
            self.drawText(10, 70, f"Translation x : {round(self.rectangle.position[0])}, y : {round(self.rectangle.position[1])}, z : {round(self.rectangle.position[2])}")
            self.drawText(10, 90, f"Dimension w : {self.rectangle.width*2}, h : {self.rectangle.height*2}, d : {self.rectangle.depth*2}")
            self.drawText(10, self.window_height-40, f"image loaded: {self.image_name[self.count_background]}")
            
            # --- Update the screen --- #    
            pg.display.flip()
            pg.time.wait(10)
        

if __name__ == "__main__":
    
    app = App(boxSize=[38, 27, 25.5])
    