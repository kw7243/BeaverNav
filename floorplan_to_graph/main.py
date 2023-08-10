from os import path
from flask import Flask, abort, request, send_file
# from partial_demo import main
from flask import Flask, jsonify, request
from interfloorplan_api import main as inter_main
from intrafloorplan_api import main as intra_main
from PIL import Image

from flask_cors import CORS

import os
import numpy as np
import uuid
import cv2
import base64
import pickle

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

@app.route('/interfloorplan', methods=['POST'])
def interfloorplan():
    data = request.get_json()
    try:
        start_floor_plan = data['floor_plan']
        start_location = data['start_location']
        end_location = data['end_location']

        # Call your interfloorplan API function here and get the path_list
        path_list = inter_main(start_location, end_location)

        return jsonify({'path_list': path_list}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/intrafloorplan', methods=['POST'])
def intrafloorplan():
    data = request.get_json()
    try:
        floor_plan = data['floor_plan']
        start_location = data['start_location']
        end_location = data['end_location']

        # Call your intrafloorplan API function here and get the image data as a NumPy array
        image_data = intra_main(start_location, end_location, floor_plan)
        print(image_data)
        # Convert NumPy array to bytes
        _, buffer = cv2.imencode('.png', image_data)

        # Convert bytes to base64 encoded string
        img_str = base64.b64encode(buffer).decode('utf-8')

        # Return the base64 string in the JSON response
        return jsonify({'image': img_str}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000)  # change port number if needed

# app = Flask(__name__)


# @app.route('/floorpaths', methods=['GET', 'POST'])
# def create_floorpath():
#     if request.method == 'GET':
#         # Get the floor path annotation from a previous request. If the image path is not found,
#         # an 400 response is sent back, indicating a bad request. We expect the path to the floor
#         # plan to be a key in the JSON body with the name `path` e.g. '{ "path": "results/test.jpg"'

#         file_path = request.json['path']
#         if path.exists(file_path) and path.isfile(file_path):
#             return send_file(file_path, max_age=5*60)
#         else:
#             return abort(400, 'the provided file path is invalid')
#     else:
#         # Create a floor path annotation on the floor plans and return the system path to each
#         # generated image.

#         start_location, end_location = request.json['origin'], request.json['destination']
#         print(start_location, end_location)

        
#         # Insert the call to the main function here
#         # Should be the response of calling the main function
#         floorplans = main(start_location,end_location)
#         # The structure of `floorplans` should be [
#         #   {
#         #     text: 'Then go to building ...',
#         #     image_file_location: [path to image file],
#         #   }
#         # ]

#         return floorplans


# if __name__ == '__main__':
#     app.run(debug=True)


