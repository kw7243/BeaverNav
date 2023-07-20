from os import path
from flask import Flask, abort, request, send_file

app = Flask(__name__)


@app.route('/route/image/', methods=['GET'])
def get_route_images():
    # Get the floor path annotation from a previous request. If the image path is not found,
    # an 400 response is sent back, indicating a bad request. We expect the path to the floor
    # plan to be a query parameter key in the URL e.g. '?path=results/test.jpg'
    file_path = request.args.get('path')
    if path.exists(file_path) and path.isfile(file_path):
        return send_file(file_path, max_age=5*60)
    else:
        return abort(400, 'the provided file path is invalid')


@app.route('/route', methods=['POST'])
def create_floorpath():
    # Create a floor path annotation on the floor plans and return the system path to each
    # generated image.

    start_location, end_location = request.json['origin'], request.json['destination']
    # Insert the call to the main function here
    # Should be the response of calling the main function
    floorplans = [{'text': 'REPLACE THIS',
                   'image_file_location': 'results/test.png'}]
    # The structure of `floorplans` should be [
    #   {
    #     text: 'Then go to building ...',
    #     image_file_location: [path to image file],
    #   }
    # ]

    return floorplans


if __name__ == '__main__':
    app.run(debug=True)
