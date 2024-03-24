import json

def write_json(filepath, data):
    # write data to json file
    # data written to csv
    
    with open(filepath, "r") as file:
        try:
            file_data = json.load(file) # file content to python list
        except json.decoder.JSONDecodeError:
                file_data = []
                print("file empty")
    
    file_data.append(data) 
    
    with open(filepath, 'w') as file:
        json.dump(file_data, file, indent=2) # dict to array (json)   
        
def read_json(filepath):
    
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

def clear_json(filepath):
    # clear the json file 
    with open(filepath, "w") as file:
        file.truncate()
        

