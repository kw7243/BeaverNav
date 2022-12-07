from os import path
from flask import Flask, abort, request, send_file
from partial_demo import main

app = Flask(__name__)


@app.route('/floorpaths', methods=['GET', 'POST'])
def create_floorpath():
    if request.method == 'GET':
        # Get the floor path annotation from a previous request. If the image path is not found,
        # an 400 response is sent back, indicating a bad request. We expect the path to the floor
        # plan to be a key in the JSON body with the name `path` e.g. '{ "path": "results/test.jpg"'

        file_path = request.json['path']
        if path.exists(file_path) and path.isfile(file_path):
            return send_file(file_path, max_age=5*60)
        else:
            return abort(400, 'the provided file path is invalid')
    else:
        # Create a floor path annotation on the floor plans and return the system path to each
        # generated image.

        start_location, end_location = request.json['origin'], request.json['destination']
        print(start_location, end_location)

        
        # Insert the call to the main function here
        # Should be the response of calling the main function
        floorplans = main(start_location,end_location)
        # The structure of `floorplans` should be [
        #   {
        #     text: 'Then go to building ...',
        #     image_file_location: [path to image file],
        #   }
        # ]

        return floorplans


if __name__ == '__main__':
    app.run(debug=True)
