import cv2
from matplotlib import pyplot as plt
from handle_json import read_json 
import numpy as np
import pickle, glob
from pprint import pprint
from src.lib.opts import opts
from src.lib.utils.pnp.cuboid_pnp_shell import pnp_shell    


# Load the camera matrix
def load_camera_matrix():
    # with open('cameraMatrix.pkl', 'rb') as f:
        # cameraMatrix = pickle.load(f)
    # print(cameraMatrix)
    cameraMatrix = np.array([[3456, 0, 2304],[0,3456,1728], [0, 0, 1]], dtype=np.float32)

    return cameraMatrix

# downscale the image to a size that is manageable
def calculateWindowRatio(img_width : int, img_height : int) -> int:
    scale = 1
    print("orginal image shape: ",img_width, img_height)
    while (img_width/scale) > 1920 or (img_height/scale) > 1080:
        scale += 1
    print("Scaling factor: ", scale)
    return scale

# Mouse callback function
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
        points.append([x, y])
        print("Point added at ({}, {})".format(x, y))


# Calculate other vertices of the cuboid
def calculate_cuboid(meta, bbox, points, size): 
    opt = opts()
    opt.nms = True
    opt.obj_scale = True   
    opt.c = "cereal_box" 
    return pnp_shell(opt, meta, bbox, points, size, OPENCV_RETURN=False)


if __name__== "__main__":
    
    # Global variable to store points
    points = []
    image_vertices = []

    # Load the camera matrix
    cameraMatrix = load_camera_matrix()
    print("cameraMatrix:\n", cameraMatrix)

    # Read an image
    images = glob.glob('data\\*.jpg')
    
    image = cv2.imread(images[0])
    
    image_w, image_h = image.shape[1], image.shape[0]
    print("Image shape: ", image.shape)
    
    scaling = calculateWindowRatio(image_w, image_h)
    
    w = int(image_w / scaling)
    h = int(image_h / scaling)
    image = cv2.resize(image, (w, h))


    # Create a window and bind the mouse callback function
    cv2.namedWindow('annotate images')
    cv2.setMouseCallback('annotate images', mouse_callback)
    i = 0
    while True:
        # Display the image
        cv2.imshow('annotate images', image)
        
        # Wait for a key press
        key = cv2.waitKey(1) & 0xFF
        
        # Exit loop if 'q' key is pressed
        if key == ord('q'):
            image_vertices.append(points)
            image_vertices = np.array(image_vertices)
            image_vertices *= scaling
            break
        
        # next image
        if key == ord('n'):
            image_vertices.append(points)
            points = [] # reset points
            i += 1
            image = cv2.imread(images[i % len(images)])
            image = cv2.resize(image, (w, h))

    # Close all OpenCV windows
    cv2.destroyAllWindows()
    print("Scaled Points selected:\n", len(image_vertices[0]))

    if (len(image_vertices) >= 1):
        
        # pnp of first image
        size = [38, 27, 25.5]
        camera = np.array(cameraMatrix, dtype=np.float32)
        meta = {"width": image_w,"height": image_h, "camera_matrix":camera}
        print("image_w and image_h: ", image_w, image_h)
        bbox = {'kps': image_vertices[0], "obj_scale": size}
        projected_points, point_3d_cam, scale, points_ori, bbox = calculate_cuboid(meta, bbox, image_vertices[0], size)
    
        # Read the image
        image = cv2.imread(images[0])
    
        # Draw the points on the image
        for coordinate in bbox["projected_cuboid"]:
            x, y = int(coordinate[0]), int(coordinate[1])
            cv2.circle(image, (x, y), 15, (0, 255, 0), -1)  # Draw a filled circle at each point
        pprint(bbox)
        # Display the image with points
        image = cv2.resize(image, (w, h))
        cv2.imshow("image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

