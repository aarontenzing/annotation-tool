import cv2

# Create a simple OpenCV window
cv2.namedWindow("Key Press Detection")

while True:
    # Wait for a key press, 1 ms delay between loops
    key = cv2.waitKey(1)
    
    if key != -1:  # Check if a key is pressed
        print(f"Key pressed: {key} | ASCII code: {chr(key) if key < 128 else 'Non-ASCII'}")
        
    # Press 'ESC' (ASCII code 27) to exit the loop
    if key == 27:  # ESC key
        print("ESC key pressed, exiting...")
        break

cv2.destroyAllWindows()
