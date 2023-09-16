#!/usr/bin/env python3

import cgi
import json
import sys

# Step 1: Get the query parameters
arguments = cgi.FieldStorage()

# Step 2: Read the JSON data from file
with open('fact.json') as f:
    data = json.load(f)

# Step 3: Function to apply filters
def apply_filters(data, filters):
    filtered_data = data.copy()
    for key, value in filters.items():
        filtered_data = {k: v for k, v in filtered_data.items() if key in v and value in v[key]}
    return filtered_data

# Step 4: Get and apply filters
filters = {}
if 'filter' in arguments:
    filter_str = arguments['filter'].value
    for f in filter_str.split(','):
        key, value = f.split(':')
        filters[key] = value

filtered_data = apply_filters(data, filters)

# Step 5: Get the result based on 'key' argument
result = []
if 'key' in arguments:
    key = arguments['key'].value
    for v in filtered_data.values():
        result.extend(v.get(key, []))
else:
    result = []

# Step 6: Return the result in JSON format
print("Content-Type: application/json")
print()
print(json.dumps(result))
