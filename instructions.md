First take some pictures with chessboard background so you can determine the camera matrix.

Next, determine the dimensions of the box in the picture.
Call the quick_annotate.run() function and provide:
 - the path of the images of the boxes
 - dimension of box in the image

By clicking on the corners in the right order you create an approximation of the cuboid.
Next press "a" for annotating and writing it to the pnp_anno.json file, if you are not happy with the approximation press "r".

After quick annotating you will run the openGL program, here you can further optimize the position of the cubiod in the picture and finally write it to anno.json. 
