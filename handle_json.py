import json

filepath = "annotations.json"

def write_json(img, world_coordinates, projection_coordinates):
    print("write!")
    # data written to csv
    data = {
                "img_name" : img,
                "world" : world_coordinates,
                "projection" : projection_coordinates,
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
        
def read_json():
    
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Unable to decode JSON data from file '{filepath}'.")
        return {}

def clear_json():
    # clear the json file 
    with open(filepath, "w") as file:
        file.truncate()
        

