### AllTrails Lunchtime Discovery API

The AllTrails Lunchtime Discovery API is built on top of the Google Places API and can help you with finding good places for lunch!

The API has a search endpoint which returns locations near a provided latitude and longitude and a favorite endpoint which saves favorited places.

### Building and running the AllTrails Lunchtime Discovery API

To build the AllTrails Lunchtime Restaurant Discovery API as a Docker image run the following docker build command. This will build a Docker image using the instructions in the provided Dockerfile and tag the image with the name all-trails-lunch-api.
 
```docker build -t alltrails-lunch-api:latest .```

Then run the following command and provide your Google Map and Places API key to start a container with the alltrails-lunch-api image and run the Discovery API. This will run the container in detached mode and bind port 5000 of the container to port 5000 on the host machine.

```docker run -d -p 5000:5000 -e ALLTRAILS_API_KEY="Your Google Map and Places API Key goes here." alltrails-lunch-api```

### Using the Discovery API's search endpoint

In the Discovery API's search endpoint-  the name, latitude and longitude arguments correspond to the search string and the coordinates around which to receive place information.

In the example below, the curl commmand will send a post request to the API running on port 5000 and look for In N Out restauraunts near the provided latitude and longitude (the specified latitude and longitude correspond to a Chase Bank in Mountain View). Because of authentication, the user must provide a user and password (which can be done with the -u flag in curl). Current supported users are user1/password1 and user2/password2.

```
curl -u user1:password1 -i -H "Content-Type: application/json" -X POST -d '{"name":"in n out", "latitude": "37.385299050858265", "longitude": "-122.08367208842164"}' http://localhost:5000/search
```

Sample result after running the above curl command. The result is an array of locations and each locations contains relevant fields such as the business_status, address, name, opening hours, photos, price level, place_id, average rating and total number of ratings:

```
[
  {
    "business_status": "OPERATIONAL",
    "formatted_address": "53 W El Camino Real, Mountain View, CA 94040, United States",
    "name": "In-N-Out Burger",
    "opening_hours": {
      "open_now": true
    },
    "photos": [
      {
        "height": 1000,
        "html_attributions": [
          "<a href=\"https://maps.google.com/maps/contrib/114532279004574758964\">In-N-Out Burger</a>"
        ],
        "photo_reference": "ATtYBwI5NId52WV5zvMip-ro6P0zUpJpvyEbp1TKgzTb0WkxpRaOWTehQMZXqFEpZq_3IIOrXpNEB2_45UXQt1D4E1ftJ0mJTkllxQ5OxkHG8iDv89cYfYuEtReiXN_BTc3MA_di9zO20HPM9m8amI0fKUiXiGsJUpj6Dw09X3z0wOcxfmsS",
        "width": 1000
      }
    ],
    "place_id": "ChIJnd9jPSi3j4AR5m7u0VrveB8",
    "price_level": 1,
    "rating": 4.4,
    "user_ratings_total": 3365
  },
  ...
]
```

If a name is not provided- the API will default to searching for Chinese restauraunts and if latitude and longitude are not provided the location defaults to AllTrails HQ.

```
curl -u user1:password1 -X POST localhost:5000/search
```

```
[
  {
    "business_status": "OPERATIONAL",
    "formatted_address": "826 Washington St, San Francisco, CA 94108, United States",
    "name": "Hunan House",
    "opening_hours": {
      "open_now": true
    },
    "photos": [
      {
        "height": 3024,
        "html_attributions": [
          "<a href=\"https://maps.google.com/maps/contrib/114706907077735163137\">A Google User</a>"
        ],
        "photo_reference": "ATtYBwIfpyI-jzMe5U9wbzOerNZd3sNGiOQMQhtybpXVdZroH2yBWzj8JPtQ3V5x7qmsJ8DmHXXNdVJrrNAcfjWTvDbZR5vaYejbfOMbcPeTxtvbbWCnWsWoLyQ60AlGgdGx68tq6i6v8RT0juFnlwEkNfOSOnAYn-0SzE0URxivUZnz1wqN",
        "width": 4032
      }
    ],
    "place_id": "ChIJ0QaAqvSAhYAR3ID2OTZi71g",
    "price_level": 2,
    "rating": 3.9,
    "user_ratings_total": 262
  },
  ...
]
```

### Using the Discovery API's favorite endpoint

The favorite endpoint can be used to flag your favorite places.

To use the favorite endpoint provide the place_id that you would like to favorite as so- remembering to use authentication. Place ids can be extracted from the search endpoint's response:

```
...
],
  "place_id": "ChIJcxzUA2UvjoARkSs2sq5OU2Q",
  "price_level": 1,
  "rating": 4.6,
  "user_ratings_total": 967
}
...


curl -u user1:password1 -i -H "Content-Type: application/json" -X POST -d '{"place_id": "ChIJcxzUA2UvjoARkSs2sq5OU2Q"}' http://localhost:5000/favorite
```

```
"Your placeid ChIJcxzUA2UvjoARkSs2sq5OU2Q has been favorited! Your favorite places are: ['San Sun Restaurant', 'In-N-Out Burger']"
```

The endpoint will indicate the place's favorite status in the API response and return all places favorited by the authenticated user.

### Running the test suite and the Postman library

The block of code starting with app.test_client() contains tests for the favorite and search endpoints. The tests will run upon starting the web server.

```
with app.test_client() as c:
    # testing search endpoint
    credentials = base64.b64encode(b"user1:password1").decode('utf-8')
    rv = c.post('/search', json={
        'name': 'indian restauraunt'
    }, headers={"Authorization": f"Basic {credentials}"})
    json_data = rv.get_json()
    assert (len(json_data) == 19)
```

To import the Postman library/collection visit this link [here](https://www.getpostman.com/collections/f88eae8f80e7373fca73).

### Deploying with Kubernetes

To deploy the AllTrails Lunchtime Discovery API with Kubernetes (rather than Docker)- first replace the value of the ALLTRAILS_API_KEY with the Google Map and Places API key in alltrails-deployent.yaml. Then run the following commands:

```
kubectl apply -f alltrails-deployment.yaml
kubectl apply -f alltrails-service.yaml
```

These commands will create a deployment of 3 pods which will run the alltrails-lunch-api Docker image as well as a service that will expose this deployment.

Port-forward to this service with the following command (replace 8888 with your desired port): 

```
kubectl port-forward svc/alltrails-service 8888:5000
```

You will now be able to use the search and favorite api endpoints. An example of using curl with your desired port to find Indian restauraunts near AllTrails HQ:

```
curl -u user1:password1 -i -H "Content-Type: application/json" -X POST -d '{"name":"indian"}' http://localhost:8888/search
```

```
[
  {
    "business_status": "OPERATIONAL",
    "formatted_address": "123 2nd St, San Francisco, CA 94105, United States",
    "name": "North India",
    "opening_hours": {
      "open_now": true
    },
    "photos": [
      {
        "height": 4032,
        "html_attributions": [
          "<a href=\"https://maps.google.com/maps/contrib/100200347972736580221\">Samarth km</a>"
        ],
        "photo_reference": "ATtYBwJzSQnOiT-B3qVXZyPirp4ov-sMRMIyMGwt8Gntjx6tehUm481y9jt0q_TQfmZw0DnWca8Dndo7L3QNQ5rYUw0S3UWiSh6EgSPOhA_k3QYM2hbwSWyMOea2kWokF0I82halBO5YaHt7fCRLnTuavy5JLe9SGrR2WNy6QdN2Rv-xOCRn",
        "width": 3024
      }
    ],
    "place_id": "ChIJrQ9dLX2AhYARiolh2hTx1Ig",
    "price_level": 2,
    "rating": 4.1,
    "user_ratings_total": 1545
  },
  ...
]
```