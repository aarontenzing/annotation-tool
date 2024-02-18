import cv2
import numpy as np

# Global variables to store clicked points
image_points = np.array([])

num_points_clicked = 0

# Mouse callback function
def click_event(event, x, y, flags, param):
    global clicked_points, num_points_clicked

    # If left mouse button clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        # Draw a circle at the clicked point
        cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow('image', img)

        # Store the clicked point
        image_points.append((x, y))
        num_points_clicked += 1

        # If all corners are clicked, display coordinates
        if num_points_clicked == 4:
            print("Clicked points:", clicked_points)

def calibrate_camera():
    # Your camera calibration code here
    # This function should return the camera matrix and distortion coefficients
    return camera_matrix, dist_coeffs


# Function to estimate 3D coordinates
def estimate_3d_coordinates(image_points, camera_matrix, dist_coeffs):
    # Define object coordinates (assuming object is at z=0)
    object_coordinates = np.array([[0, 0, 0],
                                   [object_width, 0, 0],
                                   [object_width, object_height, 0],
                                   [0, object_height, 0]], dtype=np.float32)

    # Estimate 3D coordinates using solvePnP
    retval, rvec, tvec = cv2.solvePnP(object_coordinates, image_points, camera_matrix, dist_coeffs)

    # Convert rotation vector to rotation matrix
    R, _ = cv2.Rodrigues(rvec)

    # Object coordinates in camera coordinate system
    object_coordinates_camera = np.dot(R.T, (object_coordinates - tvec.T)).T

    return object_coordinates_camera


# Define object dimensions (e.g., width, height, depth)
object_width = 30.5  # in cm
object_height = 13  # in cm

while(True):
    if (image_points.size() == 4):
        break

# Calibrate camera
camera_matrix, dist_coeffs = calibrate_camera()

# Estimate 3D coordinates
object_coordinates_camera = estimate_3d_coordinates(image_points, camera_matrix, dist_coeffs)

# Load image
img = cv2.imread('data/IMG_0595.JPG')

# Resize image for easier viewing (optional)
scale_percent = 10  # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

# Display image
cv2.imshow('image', img)

# Set mouse callback function
cv2.setMouseCallback('image', click_event)

# Wait for user to click on points
cv2.waitKey(0)
cv2.destroyAllWindows()
