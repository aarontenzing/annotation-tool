import cv2
import numpy as np
import glob
from pprint import pprint
import pickle 
from scipy.spatial.transform import Rotation as R
import itertools

from src.lib.opts import opts
from src.lib.utils.pnp.cuboid_pnp_shell import pnp_shell    
from src.tools.objectron_eval.objectron.dataset.box import Box as boxEstimation
from handle_json import write_json, clear_json
import os

class quick_annotate:
    def __init__(self, path = None, screen_size = (1920, 1080), boxSize=None):
        
        if path is None:
            BASE = os.path.dirname(os.path.abspath(__file__))
            dir = os.path.join(BASE, 'data', '*.jpg')
            print(dir)
            self.path = dir 
        else:
            self.path = path
        
        self.images = glob.glob(self.path) # get all images in the path
        self.image = cv2.imread(self.images[0])
        self.screen_size = screen_size
        self.scaling = 1
        self.idx = 0
        self.boxSize = boxSize
        self.vertices = []
        
        self.data = {}
        
        self.image_w = self.image.shape[1]
        self.image_h = self.image.shape[0]

        
        # Load the camera matrix
        cameraMatrix = self.load_camera_matrix()
        print("cameraMatrix:\n", cameraMatrix)

        print("Original image shape: ", (self.image.shape[1], self.image.shape[0]))
        
        # Resize the image  
        w, h = self.calculateWindow(self.image)
        self.image = cv2.resize(self.image, (w, h))
        
        print("scaling factor: ", self.scaling)
        print("Resized image shape: ", (w, h))
    
    
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
    
    def load_camera_matrix(self):
        # cameraMatrix = np.array([[3456, 0, 2304],[0,3456,1728], [0, 0, 1]], dtype=np.float32)
        cameraMatrix = pickle.load(open("cameraMatrix.pkl", "rb"))
        print("cameraMatrix:\n", cameraMatrix)
        distMatrix = pickle.load(open("dist.pkl", "rb"))
        return cameraMatrix, distMatrix

    def calculate_cuboid(self, size, image_points, camera_matrix, dist_coeffs):

        status = False
        dims = list(itertools.permutations(size))
        image_points = np.array(image_points, dtype=np.float32)
        print("Permutations: ", dims)

        error_distance = np.inf
        best_PNP_image_points = None
        best_rotation_vector = None
        best_translation_vector = None
        best_dimensions = None

        for i in dims:
            width, height, depth = i[0], i[1], i[2]
            # X axis point to the right
            right = width / 2.0
            left = -width / 2.0
            # Y axis point upward
            top = height / 2.0
            bottom = -height / 2.0
            # Z axis point forward
            front = depth / 2.0
            rear = -depth / 2.0

            # List of 8 vertices of the box
            object_points =  np.array([
                # self.center_location,   # Center
                [left, bottom, rear],  # Rear Bottom Left
                [left, bottom, front],  # Front Bottom Left
                [left, top, rear],  # Rear Top Left
                [left, top, front],  # Front Top Left

                [right, bottom, rear],  # Rear Bottom Right
                [right, bottom, front],  # Front Bottom Right
                [right, top, rear],  # Rear Top Right
                [right, top, front  ],  # Front Top Right

            ], dtype=np.float32)
                
            flag = cv2.SOLVEPNP_ITERATIVE

            
            ret, rotation_vector, translation_vector, reprojectionError = cv2.solvePnPGeneric(
                        object_points,
                        image_points,
                        camera_matrix,
                        dist_coeffs,
                        flags=flag
                ) 
            
            if not ret:
                continue
            
            rotation_vector = rotation_vector[0]
            translation_vector = translation_vector[0]
                
            # Project the transformed 3D points to 2D using OpenCV's projectPoints
            PNP_image_points, _ = cv2.projectPoints(object_points, rotation_vector, translation_vector, camera_matrix, dist_coeffs)
            
            # Transformation object points and rot and trans matrix
            
            
            error = 0
            # calculate the error distance
            for i in range(len(image_points)):
                error += np.linalg.norm(image_points[i] - PNP_image_points[i])
            
            print("Dims: ", width, height, depth)
            print("current error distance: ", error_distance)
            
            if error < error_distance:
                error_distance = error
                best_rotation_vector = rotation_vector
                best_translation_vector = translation_vector
                best_dimensions = [width, height, depth]
                best_object_points = object_points
                best_PNP_image_points = PNP_image_points
                status = True
                
        return best_PNP_image_points, best_rotation_vector, best_translation_vector, best_dimensions, status

        
    def draw_cuboid(self, points):
        # Draw the points on the image
        for coordinate in points:
            x, y = int(coordinate[0]), int(coordinate[1])
            cv2.circle(self.image, (x, y), 15, (0, 255, 0), -1)  # Draw a filled circle at each point      

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.vertices.append([x, y])
            cv2.circle(self.image, (x, y), 5, (0, 0, 255), -1)

    def reset_image(self, image_path):
        self.image = cv2.imread(image_path)
        w, h = self.calculateWindow(self.image)
        self.image = cv2.resize(self.image, (w, h))
        self.vertices = []    
       

    def run(self):
        
        # Create a window and bind the mouse callback function
        cv2.namedWindow('QUICK ANNOTATE')
        cv2.setMouseCallback('QUICK ANNOTATE', self.mouse_callback)
        
        while True:
            # Display the image
            cv2.imshow('QUICK ANNOTATE', self.image)
            
            # Wait for a key press
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('a'):
                print("annotate")
                if len(self.vertices) > 3 and len(self.vertices) <= 8:                       
                        
                    self.vertices = np.array(self.vertices, dtype=np.float64)
                    self.vertices *= self.scaling
                    self.vertices = self.vertices.astype(int)
                    image_points = np.array(self.vertices, dtype=np.float32)
                   
                    # pnp 
                    if self.boxSize is None:
                        self.boxSize = input("Enter the size of the object [width, height, depth]: ")
            
                    camera, dist = self.load_camera_matrix()
                    PNP_imagepoints, rotation_vector, translation_vector, dimensions, status = self.calculate_cuboid(self.boxSize, self.vertices, camera, dist)
                    PNP_imagepoints =  PNP_imagepoints.reshape(-1, 2)
                    
                    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
                    r = R.from_matrix(rotation_matrix)
                    euler_angles = r.as_euler('xyz', degrees=True)  # 'xyz' for roll, pitch, yaw
                    print("Euler angles: ", euler_angles)
                    
                    # draw the cuboid
                    if status == True:
                        print("draw estimation!")
                        self.image = cv2.imread(self.images[self.idx])
                        if PNP_imagepoints is not None:
                            self.draw_cuboid(PNP_imagepoints)
                            print("Ready to save annotation!")
                            self.data = {"img_name" : self.images[self.idx].split("\\")[-1], "orientation": euler_angles.tolist(), "translation": translation_vector.flatten().tolist(), "dimensions": dimensions}
                        else:
                            print("Error: cant draw the cuboid. Please click the vertices. In the right order")
                            self.reset_image(self.images[self.idx])
                        self.image = cv2.resize(self.image, (int(self.image_w/self.scaling), int(self.image_h/self.scaling))) # resize the image
                    else:
                        # reset the image
                        self.reset_image(self.images[self.idx])      
      
                else:
                    print("Please select 8 vertices: ", self.vertices)
                    # reset the image
                    self.reset_image(self.images[self.idx])
            
            elif key == ord("s"):
                    print("saved annotation!")
                    
                    write_json("pnp_anno.json", self.data)
                    
                    self.reset_image(self.images[self.idx])
                    projected_points, point_3d_cam, scale, points_ori, bbox, status = [], [], [], [], [], False
                
            elif key == ord('c'): 
                clear_json("pnp_anno.json")
                print("cleared annotation!")           
                        
            elif key == ord('r'):
                self.reset_image(self.images[self.idx])  
                    
            elif key == ord('n'):
                
                self.idx += 1
                if self.idx >= len(self.images):
                    self.idx = 0
                
                self.reset_image(self.images[self.idx])
                print("image: ", self.images[self.idx])
                
            elif key == ord('q'):
                break
        
        # Close all OpenCV windows
        cv2.destroyAllWindows()
      
        
if __name__ == "__main__":
    
    # Always use appropriate boxSize for the object
    # click 'a' to annotate the object and 'n' to move to the next image
    # click 's' to save the annotation
    # click 'r' to reset the image
    # click 'q' to quit the program

    qa = quick_annotate(boxSize=[13.5, 15.5, 18])
    qa.run()

        
                
        