#!/usr/bin/python3

# Import necessary libraries
import cgi
import cgitb
import json
from itertools import chain

# Example usage:
# Command: curl 'http://127.0.0.1:8888/cgi-bin/option.py?filter=type:datacenter,name:Datacenter1&key=name'
# Output: ["Datacenter1"]
#
# Command: curl 'http://127.0.0.1:8888/cgi-bin/option.py?filter=type:datacenter,name:Datacenter1&filter=type:cluster,name:Cluster1&&filter=type:datastore&key=name'
# Output: ["LUN_01_VM_Replica", "LUN_02_VM_Replicas"]
#
# Command: curl -s 'http://127.0.0.1:8888/cgi-bin/option.py?filter=type:datacenter,name:Datacenter1&filter=type:cluster,name:Cluster1&&filter=type:datastore&key=name'
# Output: ["LUN_01_VM_Replica", "LUN_02_VM_Replicas"]

# Enable traceback for debugging
cgitb.enable()

# Define the JSON file path
json_file = "fact.json"

# Load the JSON data from the file
with open(json_file, 'r') as file:
    data = json.load(file)

# Parse URL parameters using cgi.FieldStorage
form = cgi.FieldStorage()
filters = form.getlist('filter')  # Get list of filters from URL parameters
key = form.getvalue('key')  # Get key from URL parameters

# Function to apply filters recursively
def apply_filters(data, filters):
    # If no filters left, return the data
    if not filters:
        return data

    # Split the first filter into key-value pairs
    filter_params = {param.split(':')[0]: param.split(':')[1] for param in filters[0].split(',')}
    
    results = []
    # If data is a dictionary, apply filters
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                # If all filter parameters match, apply next filter
                if all(v.get(fk) == fv for fk, fv in filter_params.items()):
                    results.append(apply_filters(v, filters[1:]))
                else:
                    # If not all parameters match, apply current filter
                    result = apply_filters(v, filters)
                    if result:
                        results.append(result)
            elif isinstance(v, list):
                # If value is a list, apply filter to each item
                for item in v:
                    result = apply_filters(item, filters)
                    if result:
                        results.append(result)
    # Flatten the list before returning
    return [item for sublist in results for item in (sublist if isinstance(sublist, list) else [sublist])]

# Apply filters to the data
filtered_data = apply_filters(data, filters)

# Extract data based on the key and convert to string
if key:
    key_param = key.split(':')[-1]
    # If filtered data is a dictionary, extract values based on the key
    if isinstance(filtered_data, dict):
        filtered_data = [v for v in filtered_data.values() if isinstance(v, dict)]
        filtered_data = [str(item.get(key_param)) for item in filtered_data if item.get(key_param) is not None]
    # If filtered data is a list, extract values based on the key
    elif isinstance(filtered_data, list):
        filtered_data = [str(item.get(key_param)) for item in filtered_data if item.get(key_param) is not None]

# Generate output in JSON format
print("Content-Type: application/json")
print()
print(json.dumps(filtered_data, indent=4))

