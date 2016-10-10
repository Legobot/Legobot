from Legobot.Lego import Lego
import configparser
import requests
import os


class WeatherListener(Lego):
    def listening_for(self, message):
        return '!weather' in message['text']

    def handle(self, message):
        # check_weather_by_zip
        # Uses the Weather Underground API to check current conditions
        # and a forecast
        # Pulls its API key from api.cfg file in the same directory
        # as your bot.

        try:
            zipcode = message['text'].split()[1]
        except IndexError:
            self.reply(message, "Please provide a zip code for me to check")
            return

        if not len(zipcode) == 5:
            self.reply(message, "I only support 5 digit, US zip codes.")

        api_keys = configparser.ConfigParser()
        if os.path.isfile('api.cfg'):
            api_keys.read('api.cfg')
        else:
            err = "No API keys found. Please initialize your api.cfg file."
            self.reply(message, err)

        try:
            wunderground_api_key = api_keys.get('API', 'wunderground')
        except Exception as e:
            return e

        zipcode = message.arg1
        cond_api = "http://api.wunderground.com/api/%s/conditions/q/%s.json"
        fore_api = "http://api.wunderground.com/api/%s/forecast/q/%s.json"
        current = requests.get(cond_api % (wunderground_api_key, zipcode))
        forecast = requests.get(fore_api % (wunderground_api_key, zipcode))
        current = current.json()
        forecast = forecast.json()
        try:
            observation = current['current_observation']
            location = observation['display_location']['full']
            condition = observation['weather']
            temp_f = observation['temp_f']
            humidity = observation['relative_humidity']
            feelslike_f = observation['feelslike_f']
            wind_condition = observation['wind_string']
            wind_dir = observation['wind_dir']
            wind_speed = observation['wind_mph']
            wind_gust = observation['wind_gust_mph']

            forecastday = forecast['forecast']['txt_forecast']['forecastday']
            short_forecast_period = forecastday[1]['title']
            short_forecast_data = forecastday[1]['fcttext']

            # forecast_url = current['current_observation']['forecast_url']

        except:
            err = "Unable to find information on that zip code right now." \
                  "Please check again later or petition Congress " \
                  "to have it created."
            self.reply(message, err)
            return

        reply = "The weather in %s is currently %s with a temperature of " \
                "%s degrees, humidity of %s and it feels like %s degress. " \
                "Wind is %s, blowing %s at %s mph with %s mph gusts. " \
                "Forecast for %s: %s"
        self.reply(message, reply % (location,
                                     condition,
                                     temp_f,
                                     humidity,
                                     feelslike_f,
                                     wind_condition,
                                     wind_dir,
                                     wind_speed,
                                     wind_gust,
                                     short_forecast_period,
                                     short_forecast_data,
                                     ))

    def get_name(self):
        return 'weather'

    def get_help(self):
        help_text = "Get the weather for a US 5-digit zip code. " \
                    "Usage: !weather <zipcode>"
        return help_text
