import json

def from_json_file(config_file_path):
    with open(config_file_path, 'r') as f:
        config = json.load(f)
    return config