import cv2
import numpy as np
import glob
from pprint import pprint
import pickle 
import json

from src.lib.opts import opts
from src.lib.utils.pnp.cuboid_pnp_shell import pnp_shell    
from src.tools.objectron_eval.objectron.dataset.box import Box as boxEstimation


def write_json(filepath, img, world_coordinates, projection_coordinates):
    # data written to csv
    data = {
                "img_name" : img,
                "orientation" : world_coordinates,
                "translation" : projection_coordinates,
            }
    
    with open(filepath, "r") as file:
        try:
            file_data = json.load(file) # file content to python list
        except json.decoder.JSONDecodeError:
                file_data = []
                print("file empty")
    
    file_data.append(data) 
    
    with open(filepath, 'w') as file:
        json.dump(file_data, file, indent=2) # dict to array (json)   

class quick_annotate:
    def __init__(self, path = None, screen_size = (1920, 1080), boxSize=None):
        
        if path is None:
            self.path = ("data\\*.jpg")
        else:
            self.path = path
        
        self.images = glob.glob(self.path) # get all images in the path
        self.image = cv2.imread(self.images[0])
        self.screen_size = screen_size
        self.scaling = 1
        self.idx = 0
        self.boxSize = boxSize
        self.vertices = []
        
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
        return cameraMatrix

    def calculate_cuboid(self, meta, bbox, points, size): 
        opt = opts()
        opt.nms = True
        opt.obj_scale = True   
        opt.c = "cereal_box" 
        return pnp_shell(opt, meta, bbox, points, size, OPENCV_RETURN=False)

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
                                        
                    # pnp 
                    if self.boxSize is None:
                        self.boxSize = input("Enter the size of the object [width, height, depth]: ")
            
                    camera = self.load_camera_matrix()
                    meta = {"width": self.image_w,"height": self.image_h, "camera_matrix":camera}
                    bbox = {'kps': self.vertices, "obj_scale": self.boxSize}
                    projected_points, point_3d_cam, scale, _, bbox = self.calculate_cuboid(meta, bbox, self.vertices, self.boxSize)
                    
                    pprint(bbox)
    
                    # draw the cuboid
                    print("draw estimation!")
                    self.image = cv2.imread(self.images[self.idx])
                    self.draw_cuboid(bbox["projected_cuboid"])
                    self.image = cv2.resize(self.image, (int(self.image_w/self.scaling), int(self.image_h/self.scaling))) # resize the image      
      
                else:
                    print("Please select 8 vertices: ", self.vertices)
                    self.reset_image(self.images[self.idx])
            
            elif key == ord("s"):
                if (len(projected_points) > 0):
                    print("saved annotation!")
                    # calculate the rotation and translation matrix
                    box = boxEstimation(bbox["kps_3d_cam"])
                    orientation, translation, scale = box.fit(bbox["kps_3d_cam"])
                    orientation = orientation.tolist()
                    translation = translation.tolist()
                    
                    # print("orientation: ", orientation)
                    # print("translation: ", translation)
                    # print("scale (normalised): ", scale)

                    # projected_points = bbox["projected_cuboid"].tolist()
                    # point_3d_cam = point_3d_cam.tolist()
                    write_json("pnp_anno.json", self.images[self.idx], orientation, translation)
                    self.reset_image(self.images[self.idx])
                projected_points = [] 
                
            
            elif key == ord('r'):
                self.reset_image(self.images[self.idx])  
                    
            elif key == ord('n'):
                
                self.idx += 1
                if self.idx >= len(self.images):
                    self.idx = 0
                
                self.reset_image(self.images[self.idx])
                
            elif key == ord('q'):
                break
        
        # Close all OpenCV windows
        cv2.destroyAllWindows()
        
        
        
if __name__ == "__main__":
    # Always use appropriate boxSize for the object
    
    # click 'a' to annotate the object and 'n' to move to the next image
    # click 'r' to reset the image
    # click 'q' to quit the program

    qa = quick_annotate(boxSize=[38, 27, 25.5])
    qa.run()

        
                
        