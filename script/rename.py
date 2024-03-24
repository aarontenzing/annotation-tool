import os
import glob

def rename_files():
    dir = glob.glob('data\\*.jpg')
    i =  1
    for filename in dir:
        new_filename = os.path.join(os.path.dirname(filename), str(i) + '.jpg')
        os.rename(filename, new_filename)
        i += 1


if __name__ == '__main__':
    rename_files()