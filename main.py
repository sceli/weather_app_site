from flask import Flask, render_template, request
from jinja2 import Environment, select_autoescape, FileSystemLoader
import requests
import urllib.parse
import datetime
import os


app = Flask(__name__)
env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape(['html', 'xml']))

def format_epoch_to_time(epoch_time):
    """Converts epoch datetime format to hour:minute format"""
    dt_object = datetime.datetime.fromtimestamp(epoch_time)
    return dt_object.strftime('%H:%M')

def format_epoch_to_date(epoch_time):
    """Converts epoch datetime format to day-month-year format"""
    dt_object = datetime.datetime.fromtimestamp(epoch_time)
    return dt_object.strftime('%d-%m-%Y')

def get_day_name(epoch_time):
    """Converts epoch datetime format to weekday name"""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dt_object = datetime.datetime.fromtimestamp(epoch_time)
    day_index = dt_object.weekday()
    return days[day_index]

# Add functions to template
app.add_template_filter(format_epoch_to_time)
app.add_template_filter(format_epoch_to_date)
app.add_template_filter(get_day_name)

# Api endpoint
OWM_Endpoint = "https://api.openweathermap.org/data/2.5/onecall"
api_key = OWM_API_KEY   # Paste your api key here from https://openweathermap.org

is_response_200 = True

@app.route('/', methods=['GET', 'POST'])
def weather():
    if request.method == 'GET':
        return render_template('index.html', env=env, selected_day=None)

    elif request.method == 'POST':
        city = request.form.get('cityInput')
        view = request.form.get('view', 'daily')
        if city:
            weather_data = get_weather_data(city)
            if weather_data is None:
                # Show error message if city name is incorrect
                return render_template('index.html', error_message=f"Please enter correct city name")
            elif is_response_200 == False:
                # Show error message and response code if response is not 200
                render_template('index.html', error_message=f"{weather_data}")
            else:
                return render_template('weather.html', cityInput=city.title(), weather_data=weather_data,
                                       view=view, env=env)
        else:
            return render_template('index.html', env=env)

def get_weather_data(address):
    global is_response_200
    url = 'https://nominatim.openstreetmap.org/search?q=' + urllib.parse.quote(address) + '&format=json'

    response = requests.get(url)
    if response.status_code == 200:
        try:
            my_latitude = response.json()[0]["lat"]
            my_longitude = response.json()[0]["lon"]

            weather_params = {
                "lat": my_latitude,
                "lon": my_longitude,
                "units": "metric",
                "exclude": "minutely",
                "appid": api_key
            }
            response = requests.get(OWM_Endpoint, params=weather_params)
            if response.status_code == 200:
                response.raise_for_status()
                weather_data = response.json()
                return weather_data
            else:
                is_response_200 = False
                return response
        except IndexError:
            return None
    else:
        is_response_200 = False
        return response

@app.route('/toggle_view', methods=['POST'])
def toggle_view():
    city = request.form.get('cityInput')
    view = request.form.get('view')

    weather_data = get_weather_data(city)
    return render_template('weather.html', cityInput=city, weather_data=weather_data, view=view, env=env)

if __name__ == '__main__':
    app.run(debug=True)
