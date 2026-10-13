import json

import requests
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

class WeatherClient:
    
    def __init__(self):
        self.location_api = "http://ip-api.com/json/"
        self.weather_api = "https://api.open-meteo.com/v1/forecast"

    def get_location(self):
        response = requests.get(self.location_api, timeout=5)
        response.raise_for_status()

        data = response.json()

        return {
            "city": data.get("city"),
            "region": data.get("regionName"),
            "country": data.get("country"),
            "latitude": data.get("lat"),
            "longitude": data.get("lon")
        }

    def get_weather(self, latitude, longitude):
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true",
            "temperature_unit": "fahrenheit",
            "windspeed_unit": "mph"
        }

        response = requests.get(
            self.weather_api,
            params=params,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        return data.get("current_weather", {})


class WeatherService:
    def __init__(self):
        self.client = WeatherClient()

    def build_report(self):
        location = self.client.get_location()

        weather = self.client.get_weather(
            location["latitude"],
            location["longitude"]
        )

        return {
            "location": {
                "city": location["city"],
                "region": location["region"],
                "country": location["country"]
            },
            "weather": {
                "temperature_fahrenheit": weather.get("temperature"),
                "wind_speed_mph": weather.get("windspeed"),
                "wind_direction": weather.get("winddirection"),
                "weather_code": weather.get("weathercode"),
                "time": weather.get("time")
            }
        }


app = Flask(__name__)
CORS(app)

weather_service = WeatherService()

def api_response(data):
    pretty = request.args.get("pretty")

    if pretty is not None:
        return Response(
            json.dumps(data, indent=4),
            mimetype="application/json"
        )

    return jsonify(data)


@app.route("/", methods=["GET"])
def home():
    return api_response({
        "message": "Dynamic Weather API is running",
        "try": [
            "/weather",
            "/weather?pretty"
        ]
    })


@app.route("/weather", methods=["GET"])
def weather():
    try:
        report = weather_service.build_report()
        return api_response(report)

    except Exception as error:
        return api_response({
            "error": str(error),
            "message": "Weather lookup failed"
        }), 500


def main():
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
