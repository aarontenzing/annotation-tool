import numpy as np
import cv2
import glob
import pickle
import itertools


# Import math Library
import math 
from src.lib.utils.pnp.cuboid_pnp_shell import pnp_shell   
from src.tools.objectron_eval.objectron.dataset.box import Box as boxEstimatio
from src.lib.opts import opts

from handle_json import write_json, clear_json

class cuboid:
    def __init__(self, w, h, d):
        self.width = w
        self.height = h
        self.depth = d 
        self.dimension_order = list(itertools.permutations([self.width, self.height, self.depth]))

        self.translation_vector = None
        self.rotation_vector = None
        self.rotation_matrix = None
        
        self.image_points = None
    
    def set_dimensions(self, w, h, d):
        self.width = w
        self.height = h
        self.depth = d

    def get_world_coordinates(self):
        # X axis point to the right
        right = self.width / 2.0
        left = -self.width / 2.0
        # Y axis point upward
        top = self.height / 2.0
        bottom = -self.height / 2.0
        # Z axis point forward
        front = self.depth / 2.0
        rear = -self.depth / 2.0
        # List of 8 vertices of the box
        object_points =  np.array([
            [left, bottom, rear],  # Rear Bottom Left
            [left, bottom, front],  # Front Bottom Left
            [left, top, rear],  # Rear Top Left
            [left, top, front],  # Front Top Left
            [right, bottom, rear],  # Rear Bottom Right
            [right, bottom, front],  # Front Bottom Right
            [right, top, rear],  # Rear Top Right
            [right, top, front],  # Front Top Right

        ], dtype=np.float32)
        
        return object_points
    
    def set_rotation_vector(self, rotation_vector):
        self.rotation_vector = rotation_vector
    
    def set_translation_vector(self, translation_vector):
        self.translation_vector = translation_vector
        
    def set_image_points(self, image_points):
        self.image_points = image_points
        
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
    def get_depth(self):
        return self.depth
    
    def get_size(self):
        return [self.width, self.height, self.depth]
    
    def get_translation_vector(self):
        return self.translation_vector
    
    def get_rotation_vector(self):
        return self.rotation_vector

class quick_annotate:
    def __init__(self, screen_size = (1920, 1080), boxSize=None):
        
        self.path = "data/*.jpg"
        self.images = glob.glob(self.path) # get all images in the path
        self.image = cv2.imread(self.images[0])
        
        self.screen_size = screen_size
        self.scaling = 1
        
        self.idx = 0
        self.boxSize = boxSize
        self.vertices = []
        
        self.data = {} # dictionary to store the data that will be annotated
        
        self.image_w = self.image.shape[1]
        self.image_h = self.image.shape[0]
        
        # Load the camera matrix
        self.cameraMatrix, self.distMatrix = self.load_camera_matrix()
        print("cameraMatrix:\n", self.cameraMatrix)
        print("Distortion Coefficients:\n", self.distMatrix)

        print("Original image shape: ", (self.image.shape[1], self.image.shape[0]))
        
        # Resize the image  
        w, h = self.calculateWindow(self.image)
        self.image = cv2.resize(self.image, (w, h))
        
        print("scaling factor: ", self.scaling)
        print("Resized image shape: ", (w, h))
        
        self.cuboid = cuboid(boxSize[0], boxSize[1], boxSize[2])  # Set the dimensions of the cuboid
    
    def calculateWindow(self, image):
            
        # downscale the image to a size that is manageable
        self.image_h = image.shape[0]
        self.image_w = image.shape[1]
        scale = 1
        
        while (self.image_w/scale) > self.screen_size[1] or (self.image_h/scale) > self.screen_size[0]:
            scale += 1
            
        self.scaling = scale
        w = int(self.image_w / scale)
        h = int(self.image_h / scale)
        
        return w, h

    def reset_image(self, image_path):
        self.image = cv2.imread(image_path)
        w, h = self.calculateWindow(self.image) # scaled imager size
        self.image = cv2.resize(self.image, (w, h))
        self.vertices = []          

    def load_camera_matrix(self):
        # Load the camera matrix
        cameraMatrix = pickle.load(open("cameraMatrix.pkl", "rb"))
        distMatrix = pickle.load(open("dist.pkl", "rb"))
        return cameraMatrix, distMatrix

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.vertices.append([x, y])
            cv2.circle(self.image, (x, y), 5, (0, 0, 255), -1)

    def draw_cuboid(self, points):
        # Draw the points on the image
        for coordinate in points:
            x, y = int(coordinate[0]), int(coordinate[1])
            # print(x, y)
            cv2.circle(self.image, (x, y), 15, (0, 255, 0), -1)  # Draw a filled circle at each point     
        return self.image

    def calculate_best_cuboid(self, boxSize, vertices, cameraMatrix, distMatrix):
        # vars to store the best values
        error_distance = np.inf
        best_PNP_image_points = None
        best_rotation_vector = None
        best_translation_vector = None
        best_dimensions = None
        
        # go through all the possible permutations of the dimensions
        for x in self.cuboid.dimension_order:
            
            self.cuboid.set_dimensions(x[0], x[1], x[2])
            object_points = self.cuboid.get_world_coordinates()
            image_points = np.array(vertices, dtype=np.float32)
        
            status, rotation_vector, translation_vector, _ = cv2.solvePnPGeneric(object_points, image_points, cameraMatrix, distMatrix)
            if not status:
                continue
            
            rotation_vector = rotation_vector[0]
            translation_vector = translation_vector[0]
        
            PNP_image_points, _ = cv2.projectPoints(object_points, rotation_vector, translation_vector, cameraMatrix, distMatrix)
            
            rotation_matrix = cv2.Rodrigues(rotation_vector)
            rotation_matrix = rotation_matrix[0]
            transformed_points = []
            for point in object_points:
                # Apply rotation and translation
                point_col = point.reshape((3, 1))
                transformed_point = np.dot(rotation_matrix, point_col) + translation_vector
                transformed_points.append(transformed_point.flatten())
                
            transformed_points = np.array(transformed_points)      
            
            error = 0
            # calculate the error distance
            for i in range(len(image_points)):
                error += np.linalg.norm(image_points[i] - PNP_image_points[i])
            
            print("Dimensions: ", self.cuboid.get_width(), self.cuboid.get_height(), self.cuboid.get_depth())
            print("Current error distance: ", error)
            
            if error < error_distance:
                error_distance = error
                best_rotation_vector = rotation_vector
                best_translation_vector = translation_vector
                best_dimensions = self.cuboid.get_size()
                best_object_points = transformed_points
                best_PNP_image_points = PNP_image_points
                status = True
                
            
        self.cuboid.set_rotation_vector(best_rotation_vector)
        self.cuboid.set_translation_vector(best_translation_vector)
        self.cuboid.set_image_points(best_PNP_image_points)
        self.cuboid.set_dimensions(best_dimensions[0], best_dimensions[1], best_dimensions[2])
        
        print("Best dimensions: ", best_dimensions, "Error distance: ", error_distance)
                        
        return best_PNP_image_points, best_object_points, best_rotation_vector, best_translation_vector, best_dimensions, status 
            
    def run(self):
        
        # Create a window and bind the mouse callback function
        cv2.namedWindow('QUICK ANNOTATE')
        cv2.setMouseCallback('QUICK ANNOTATE', self.mouse_callback)
        step = 1
        
        while True:
            # Display the image
            cv2.imshow('QUICK ANNOTATE', self.image)
            
            # Wait for a key press
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('n'): # move to the next image
                print("Next image")
                self.idx += 1
                if self.idx >= len(self.images):
                    self.idx = 0
                print("Current image: ", self.images[self.idx])
                self.reset_image(self.images[self.idx])           
                        
            elif key == ord('r'):
                print("Reset the image")
                self.reset_image(self.images[self.idx]) # reset the image to original
            
            elif key == ord('a'): # annotate the image
                
                if len(self.vertices) == 8:
                    self.vertices = np.array(self.vertices, dtype=np.float64)
                    self.vertices *= self.scaling
                    self.vertices = self.vertices.astype(int)
                    image_points = np.array(self.vertices, dtype=np.float32)
                    
                    PNP_imagepoints, object_points, rotation_vector, translation_vector, dimensions, status = self.calculate_best_cuboid(self.boxSize, self.vertices, self.cameraMatrix, self.distMatrix)
                    PNP_imagepoints =  PNP_imagepoints.reshape(-1, 2)
              
                    # Draw PNP estimated cuboid
                    if PNP_imagepoints is not None:
                        self.image = cv2.imread(self.images[self.idx])
                        self.draw_cuboid(PNP_imagepoints)
                    else:
                        print("Error: cant draw the cuboid. Please click the vertices. In the right order")
                        self.reset_image(self.images[self.idx])

                    self.image = cv2.resize(self.image, (int(self.image_w/self.scaling), int(self.image_h/self.scaling))) # resize the image
  
                else:
                    print("Not enough points!")
                    self.reset_image(self.images[self.idx]) # reset the image
   
            elif key == ord('f'):
                cv2.destroyAllWindows()
                print("finetune")
                while True:
                    
                    # reset the image
                    self.image = cv2.imread(self.images[self.idx])
                     
                    image_points, _ = cv2.projectPoints(self.cuboid.get_world_coordinates(), self.cuboid.get_rotation_vector(), self.cuboid.get_translation_vector(), self.cameraMatrix, self.distMatrix)
                    image_points = image_points.reshape(-1, 2) 
                     
                    self.draw_cuboid(image_points)
                    
                    w, h = self.calculateWindow(self.image)
                    self.image = cv2.resize(self.image, (w, h))
                    
                    cv2.imshow('finetune', self.image)
                    
                    # Rotation keys (W, S, A, D, Q, E)
                    if key == ord('x'):  # Rotate up (around X-axis)
                        self.cuboid.rotation_vector[0] += math.radians(step)
                        print("W: Rotate Up")
                    elif key == ord('X'):  # Rotate down (around X-axis)
                        self.cuboid.rotation_vector[0] -= math.radians(step)
                        print("S: Rotate Down")
                    elif key == ord('y'):  # Rotate left (around Y-axis)
                        self.cuboid.rotation_vector[1] += math.radians(step)
                        print("A: Rotate Left")
                    elif key == ord('Y'):  # Rotate right (around Y-axis)
                        self.cuboid.rotation_vector[1] -= math.radians(step)
                        print("D: Rotate Right")
                    elif key == ord('z'):  # Rotate counterclockwise (around Z-axis)
                        self.cuboid.rotation_vector[2] += math.radians(step)
                        print("Q: Rotate Counterclockwise")
                    elif key == ord('Z'):  # Rotate clockwise (around Z-axis)
                        self.cuboid.rotation_vector[2] -= math.radians(step)
                        print("E: Rotate Clockwise")
                        
                    elif key == ord("a"):  # Left arrow (translate left along X-axis)
                        self.cuboid.translation_vector[0] -= step
                        print("Left Arrow: Move Left")
                    elif key == ord("d"):  # Right arrow (translate right along X-axis)
                        self.cuboid.translation_vector[0] += step
                        print("Right Arrow: Move Right")
                    elif key == ord("w"):  # Up arrow (translate up along Y-axis)
                        self.cuboid.translation_vector[1] -= step
                        print("Up Arrow: Move Up")
                    elif key == ord("s"):  # Down arrow (translate down along Y-axis)
                        self.cuboid.translation_vector[1] += step
                        print("Down Arrow: Move Down")
                    elif key == ord('q'):  # Page up (translate forward along Z-axis)
                        self.cuboid.translation_vector[2] -= step
                        print("Z: Move Forward")
                    elif key == ord('e'):  # Page down (translate backward along Z-axis)
                        self.cuboid.translation_vector[2] += step
                        print("X: Move Backward")
                        
                    elif key == 43:  # Plus key (increase step size)
                        step += 0.1
                        print("Plus: Increase step size")
                        print("Current step size: ", step)
                    
                    elif key == 45:  # Minus key (decrease step size)
                        if step > 0.1:
                            step -= 0.1
                        print("Minus: Decrease step size")
                        print("Current step size: ", step)
                    
                    elif key == 13:  # Enter key (save the annotation)
                        # Save the annotation
                        print("Saved the annotation")
                        image_points_int = [[int(round(point[0])), int(round(point[1]))] for point in image_points]
                        self.data = {"img_name" : self.images[self.idx].split("\\")[-1], "projection": image_points_int, "world": object_points.tolist(), "dimensions": self.cuboid.get_size()}   
                        write_json("pnp_anno.json", self.data)
                        
                        # Reset the cuboid to annotate a new object
                        del self.cuboid
                        self.cuboid = cuboid(self.boxSize[0], self.boxSize[1], self.boxSize[2])
                        
                        # Move to the next image
                        self.idx += 1
                        if self.idx >= len(self.images):
                            self.idx = 0
                        self.reset_image(self.images[self.idx]) 
                        
                        # Close the window
                        cv2.destroyWindow('finetune')
                        self.run()   
                           
                    elif key == 27:
                        cv2.destroyWindow('finetune')
                        break
                    
                    key = cv2.waitKey(5) & 0xFF  # Adjust the delay (5 ms) as needed
        
            elif key == 27: # quit the program
                    break
                
        cv2.destroyAllWindows()                    
        
if __name__ == "__main__":
    
    # Always use appropriate boxSize for the object
    # click 'a' to annotate the object and 'n' to move to the next image
    # click 's' to save the annotation
    # click 'r' to reset the image
    # click 'q' to quit the program
    
    qa = quick_annotate(boxSize=[25.5, 27, 38])
    qa.run()
