from Legobot.Lego import Lego
import configparser
import requests
import os


class WeatherListener(Lego):
    def listening_for(self, message):
        return '!weather' in message['text']

    def handle(self, message):
        # check_weather_by_zip
        # Uses the Weather Underground API to check current conditions and a forecast
        # Pulls its API key from api.cfg file in the same directory as your bot.

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
            self.reply(message, "No API keys found. Please initialize your api.cfg file.")

        try:
            wunderground_api_key = api_keys.get('API', 'wunderground')
        except Exception as e:
            return e

        zipcode = message.arg1
        current = requests.get(
            "http://api.wunderground.com/api/%s/conditions/q/%s.json" % (wunderground_api_key, zipcode))
        forecast = requests.get(
            "http://api.wunderground.com/api/%s/forecast/q/%s.json" % (wunderground_api_key, zipcode))
        current = current.json()
        forecast = forecast.json()
        try:
            location = current['current_observation']['display_location']['full']
            condition = current['current_observation']['weather']
            temp_f = current['current_observation']['temp_f']
            humidity = current['current_observation']['relative_humidity']
            feelslike_f = current['current_observation']['feelslike_f']
            wind_condition = current['current_observation']['wind_string']
            wind_dir = current['current_observation']['wind_dir']
            wind_speed = current['current_observation']['wind_mph']
            wind_gust = current['current_observation']['wind_gust_mph']

            short_forecast_period = forecast['forecast']['txt_forecast']['forecastday'][1]['title']
            short_forecast_data = forecast['forecast']['txt_forecast']['forecastday'][1]['fcttext']

            # forecast_url = current['current_observation']['forecast_url']

        except:
            self.reply(message, ("Unable to find information on that zip code right now." +
                                 "Please check again later or petition Congress to have it created."))
            return

        reply = ("The weather in %s is currently %s with a temperature of %s degrees, humidity of %s, " +
                 "and it feels like %s degress. Wind is %s, blowing %s at %s mph with %s mph gusts. " +
                 "Forecast for %s: %s") % (
            location,
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
        )
        self.reply(message, reply)

    def get_name(self):
        return 'weather'

    def get_help(self):
        return 'Get the weather for a US 5-digit zip code. Usage: !weather <zipcode>'
