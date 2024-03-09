import cv2
import numpy as np
import glob
from pprint import pprint

from src.lib.opts import opts
from src.lib.utils.pnp.cuboid_pnp_shell import pnp_shell    

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
        _, _, w, h = self.calculateWindow(self.image)
        self.image = cv2.resize(self.image, (w, h))
        
        print("scaling factor: ", self.scaling)
        print("Resized image shape: ", (w, h))
    
    
    def calculateWindow(self, image):
        # downscale the image to a size that is manageable
        image_w, image_h = image.shape[1], image.shape[0]
        scale = 1
        while (image_w/scale) > self.screen_size[1] or (image_h/scale) > self.screen_size[0]:
            scale += 1
        self.scaling = scale
        image_w = self.image.shape[1]
        image_h = self.image.shape[0]
        w = int(image_w / scale)
        h = int(image_h / scale)
        
        return image_w, image_h, w, h
    
    def load_camera_matrix(self):
        cameraMatrix = np.array([[3456, 0, 2304],[0,3456,1728], [0, 0, 1]], dtype=np.float32)
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
        image_w, image_h, w, h = self.calculateWindow(self.image)
        self.image_w = image_w
        self.image_h = image_h
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
                    projected_points, _, _, _, bbox = self.calculate_cuboid(meta, bbox, self.vertices, self.boxSize)
                    pprint(bbox)
                    if len(projected_points) != 0:
                        print("draw estimation!")
                        # self.draw_cuboid(bbox["projected_cuboid"])
                        _,_,w,h = self.calculateWindow(self.image)
                        self.image = cv2.imread(self.images[self.idx])
                        for coordinate in bbox["projected_cuboid"]:
                            x, y = int(coordinate[0]), int(coordinate[1])
                            cv2.circle(self.image, (x, y), 15, (0, 255, 0), -1)  # Draw a filled circle at each point
                        self.image = cv2.resize(self.image, (w, h))
                        
                    else:
                        print("Wrong order of points selected.")    
                    
                else:
                    print("Please select 8 vertices: ", self.vertices)
                    self.reset_image(self.images[self.idx])
            
            elif key == ord('r'):
                self.reset_image(self.images[self.idx])

            elif key == ord('w'):
                print("write to file")
                
            
            elif key == ord('n'):
                
                self.idx += 1
                if self.idx >= len(self.images):
                    self.idx = 0
                
                self.image = cv2.imread(self.images[self.idx])
                _, _, w, h = self.calculateWindow(self.image)
                self.image = cv2.resize(self.image, (w, h))
                self.points = []
                
            elif key == ord('q'):
                break
        
        # Close all OpenCV windows
        cv2.destroyAllWindows()
        
        
        
if __name__ == "__main__":
    qa = quick_annotate(boxSize=[38, 27, 25.5])
    qa.run()
    cv2.destroyAllWindows()

        
                
        