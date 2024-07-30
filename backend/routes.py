from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))

######################################################################
# RETURN HEALTH OF THE APP
######################################################################


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################


@app.route("/count")
def count():
    """return length of data"""
    if data:
        return jsonify(length=len(data)), 200

    return {"message": "Internal server error"}, 500


######################################################################
# GET ALL PICTURES
######################################################################
@app.route("/picture", methods=["GET"])
def get_pictures():
    return jsonify(data)

######################################################################
# GET A PICTURE BY ID
######################################################################

@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    picture = next((item for item in data if item.get('id') == id), None)
    if picture:
        return jsonify(picture)
    else:
        abort(404, description="Picture not found")

# Flask route to create a picture, respecting the provided ID
@app.route("/picture", methods=["POST"])
def create_pictures():
    if not request.json:
        abort(400, "Bad request. JSON data is required.")
    new_picture = request.json
    if 'id' in new_picture:
        if any(p['id'] == new_picture['id'] for p in data):
            # Ensure the message string matches exactly what's expected in the test
            return jsonify({"Message": f"picture with id {new_picture['id']} already present"}), 302
    else:
        new_picture['id'] = data[-1]['id'] + 1 if data else 1
    data.append(new_picture)
    return jsonify(new_picture), 201

# Flask route to delete a picture by ID
@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture_by_id(id):
    global data
    original_length = len(data)
    data = [item for item in data if item['id'] != id]
    if len(data) == original_length:
        return jsonify({"message": "No picture found with that ID"}), 404
    return jsonify({"message": "Picture deleted"}), 204

@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    if not request.json:
        abort(400, "Bad request. JSON data is required.")
    update_data = request.json
    picture = next((item for item in data if item['id'] == id), None)
    if not picture:
        return jsonify({"message": "Picture not found"}), 404
    # Apply updates to the picture
    picture.update(update_data)
    return jsonify(picture), 200


if __name__ == '__main__':
    app.run(debug=True)