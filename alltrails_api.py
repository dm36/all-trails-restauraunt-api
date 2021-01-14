import collections
import googlemaps
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
import base64

app = Flask(__name__)
api_key = os.getenv('ALLTRAILS_API_KEY')

# exit if an api_key is not provided
if not api_key:
    print ("You need to provide your Google Maps and Places ALLTRAILS_API_KEY!")
    quit()

auth = HTTPBasicAuth()
favorites = collections.defaultdict(list)

users = {
    "user1": generate_password_hash("password1"),
    "user2": generate_password_hash("password2")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


@app.route('/search', methods=['POST'])
@auth.login_required
def search():
    '''The search endpoint finds places and associated information'''
    client = googlemaps.Client(api_key)

    # retrieve parameters from post request and if not provided default keyword
    # to chinese restauraunt and latitude and longitude to alltrails hq
    if not request.json:
        keyword = 'chinese restauraunt'
        latitude =  '37.79097732803359'
        longitude = '-122.40599930374489'
    else:
        keyword = request.json.get('name', 'chinese restauraunt')

        if ('latitude' in request.json and 'longitude' not in request.json) or ('latitude' not in request.json and 'longitude' in request.json):
            return jsonify("Either both latitude and longitude must be provided or neither!"), 400

        latitude = request.json.get('latitude', 37.79097732803359)
        longitude = request.json.get('longitude', -122.40599930374489)
    
    results = client.places(keyword, (float(latitude), float(longitude)))
    search_results = []
    for result in results['results']:
        features = ['name', 'formatted_address', 'business_status', 'price_level', 'opening_hours', 'place_id', 'rating', 'photos', 'user_ratings_total']
    
        # Filter out non-operational businesses
        if 'business_status' in result and result['business_status'] != 'OPERATIONAL':
            continue

        # Represent output as an array of feature maps- each feature map contains the relevant features for that location
        feature_map = {}
        for feature in features:
            if feature in result:
                feature_map[feature] = result[feature]
        search_results.append(feature_map)

    return jsonify(search_results), 200


@app.route('/favorite', methods=['POST', 'DELETE'])
@auth.login_required
def favorite():
    '''The favorite endpoint can be used to flag your favorite places.'''
    if request.method == "DELETE":
        if not placeid:
            return jsonify('place_id must be provided as a parameter when deleting from the favorite endpoint!'), 400

        new_favorites = []
        for pid, name in favorites[user]:
            if pid == placeid:
                continue
            else:
                new_favorites.append((pid, name))
        if len(new_favorites) == len(favorites):
            return jsonify("This place has not been favorited."), 400
        favorites[user] = new_favorites
        return jsonify("The place corresponding to your placeid has been successfully deleted.")
        

    if request.method == "POST":
        user = auth.current_user()
        client = googlemaps.Client(api_key)
        
        # throw an error if the user does not provide place_id
        if not request.json or 'place_id' not in request.json:
            return jsonify('place_id must be provided as a parameter to the favorite endpoint!'), 400
        placeid = request.json['place_id']
        
        # use the google place api to retrieve information on the provided place
        # and throw an error if the placeid does not exist
        try:
            response = client.place(placeid)
        except:
            return jsonify('The place you tried to favorite does not exist!'), 400
        
        # retrieve the name of the place and save it away as a favorite as long 
        # as it has not been seen before
        name = response['result']['name']
        
        if (placeid, name) not in favorites[user]:
            favorites[user].append((placeid, name))
        else:
            return jsonify('You have already favorited this place before!'), 400

        # retrieve the names of the user's favorited places
        favorited_places = [name for placeid, name in favorites[user]]
        return jsonify("Your placeid " + placeid + " has been favorited!" + " Your favorite places are: " + str(favorited_places))

with app.test_client() as c:
    # testing search endpoint
    credentials = base64.b64encode(b"user1:password1").decode('utf-8')
    rv = c.post('/search', json={
        'name': 'indian restauraunt'
    }, headers={"Authorization": f"Basic {credentials}"})
    json_data = rv.get_json()
    assert (len(json_data) == 19)

    # testing favorite endpoint
    rv = c.post('/favorite', json={
        'place_id': 'ChIJA0cTb4-AhYAR75I-j6J-2DM'
    }, headers={"Authorization": f"Basic {credentials}"})
    json_data = rv.get_json()
    assert json_data == "Your placeid ChIJA0cTb4-AhYAR75I-j6J-2DM has been favorited! Your favorite places are: ['New Delhi Indian Restaurant']"

    # testing error cases for search endpoint
    rv = c.post('/search', json={
        'name': 'indian restauraunt',
        'longitude': '32'
    }, headers={"Authorization": f"Basic {credentials}"})
    json_data = rv.get_json()
    assert json_data == "Either both latitude and longitude must be provided or neither!"

    rv = c.post('/search', json={
        'name': 'indian restauraunt',
        'latitude': '32'
    }, headers={"Authorization": f"Basic {credentials}"})
    json_data = rv.get_json()
    assert json_data == "Either both latitude and longitude must be provided or neither!"

    # testing error cases for favorite endpoint
    rv = c.post('/favorite', json={
        'placesID': 'ChIJA0cTb4-AhYAR75I-j6J-2DM'
    }, headers={"Authorization": f"Basic {credentials}"})
    json_data = rv.get_json()
    assert json_data == "place_id must be provided as a parameter to the favorite endpoint!"

    rv = c.post('/favorite', json={
        'place_id': 'ChIJA0cTb4-AhYAR75I-j6J-2DL'
    }, headers={"Authorization": f"Basic {credentials}"})
    json_data = rv.get_json()
    assert json_data == "The place you tried to favorite does not exist!"

    rv = c.post('/favorite', json={
        'place_id': 'ChIJA0cTb4-AhYAR75I-j6J-2DM'
    }, headers={"Authorization": f"Basic {credentials}"})
    json_data = rv.get_json()
    assert json_data == 'You have already favorited this place before!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
