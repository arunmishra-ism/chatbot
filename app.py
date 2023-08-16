from flask import Flask, request, jsonify, render_template
from chatbot_utils import get_bot_response, get_response, intents
import random
import wikipedia
import requests
import wolframalpha
import re  # Import the re module for regular expressions

app = Flask(__name__)

# Route to render the index.html template
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle chat interactions
# Route to handle chat interactions
# Set up your OpenWeatherMap API key
openweathermap_api_key = "dc4f950cf48cc8f8e16843aa39ac59d6"

# Set up your Wolfram Alpha API key
wolfram_alpha_api_key = "26HYYJ-8AX38VK586"
# Set up your Wikipedia API
wikipedia.set_lang("en")  # Set the desired language for Wikipedia queries

# Set up your Wolfram Alpha client
wolfram_client = wolframalpha.Client(wolfram_alpha_api_key)

# Your existing code for handling user input and interactions
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message'].lower()

    # Extract the city name from user input
    city_match = re.search(r'in (\w+)', user_message, re.IGNORECASE)
    user_provided_city = city_match.group(1) if city_match else None

    # Get the chatbot's response and tag probabilities
    response, tag_probabilities = get_bot_response(user_message)

    # Find the intent with the highest probability
    highest_probability_intent = max(tag_probabilities, key=lambda x: float(x['probability']))
    print(highest_probability_intent['probability'], highest_probability_intent)

    # Check if the user's query is related to temperature
    if "temperature" in user_message in user_message:
        city = user_provided_city or "mumbai"
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweathermap_api_key}&units=metric"
        response = requests.get(weather_url)
        weather_data = response.json()

        if weather_data.get("main") and weather_data.get("main").get("temp"):
            temperature = weather_data["main"]["temp"]
            answer = f"The current temperature in {city.capitalize()} is {temperature:.1f}°C."
        else:
            answer = f"Sorry, I couldn't retrieve the temperature information for {city.capitalize()}."

    # Check if the user's query is related to weather
    elif "weather" in user_message and user_provided_city:
        city = user_provided_city.capitalize()
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweathermap_api_key}&units=metric"
        response = requests.get(weather_url)
        weather_data = response.json()

        if weather_data.get("main") and weather_data.get("weather"):
            weather_condition = weather_data["weather"][0]["description"]
            feels_like = weather_data["main"]["feels_like"]
            answer = f"In {city}, the weather is {weather_condition}, and it feels like {feels_like:.1f}°C."
        else:
            answer = f"Sorry, I couldn't retrieve the weather information for {city}."


    # Check if the user's query can be answered using Wolfram Alpha
    elif any(word in user_message for word in ["solve", "calculate"]):
        wolfram_res = wolfram_client.query(user_message)
        if wolfram_res.success:
            answer = next(wolfram_res.results).text
        # else:
        #     answer = response  # Fallback to intents.json response

    # Check if the probability is less than 0.6 to use Wikipedia
    elif float(highest_probability_intent['probability']) < 0.65:
        try:
            wiki_summary = wikipedia.summary(user_message, sentences=2)
            answer = wiki_summary #if wiki_summary else response  # Use Wikipedia summary if available
        except wikipedia.exceptions.PageError:
            answer = get_response([highest_probability_intent], intents)  # Fetch the response using the intent

    else:
        answer = get_response([highest_probability_intent], intents)  # Fetch the response using the intent

    return jsonify({'response': answer})

if __name__ == '__main__':
    app.run()