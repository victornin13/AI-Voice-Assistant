import os
from typing import Any
import openai
from dotenv import load_dotenv
import time
import speech_recognition as sr
import numpy as np
import pyttsx3
import pywhatkit 
import datetime
import re



load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEYS')
model = 'gpt-3.5-turbo'

r= sr.Recognizer()
engine = pyttsx3.init()
voice = engine.getProperty('voices')[0]
engine.setProperty('voice', voice.id)
name= ['Vic','Victor']


greetings = ["Hello {}".format(np.random.choice(name)),
           "Yes?",
           "How are you today good sir?",
           "Mister {}".format(np.random.choice(name)),
           "Doctor {}".format(np.random.choice(name)),
           "Professor {}".format(np.random.choice(name)),
           "To how may I be of service sir",
           "I am at your service",
           "Que quieres",
           "Que lo Que",
           "Master {}".format(np.random.choice(name)),
           "My guy",
           "What's good?"]



#Checks the status of weather from OpenWeatherMap 
def current_weather(day=None):
    weather_API = "WEATHER_KEY"
    city = "Washington"
    weather_data = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&units=imperial&appid={weather_API}")
    if weather_data.json()['cod'] == '404':
        print("No City Found")
    else:
        forecast_list = weather_data.json()['list']
        current_date = datetime.datetime.now().date()
        target_date = None
        
        if day:
            # Handle 'today' and 'tomorrow' cases
            if day.lower() == 'today' or day.lower() == 'right now' or day.lower() == 'currently':
                target_date = current_date
            elif day.lower() == 'tomorrow':
                target_date = current_date + datetime.timedelta(days=1)
            else:
                # Find the target date based on the specific day mentioned
                weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                target_weekday = weekdays.index(day.lower())
                target_date = current_date + datetime.timedelta(days=(target_weekday - current_date.weekday()) % 7)

        # Find the weather information for the target date
        target_forecast = next((forecast for forecast in forecast_list if forecast['dt_txt'].startswith(str(target_date))), None) if target_date else None

        if target_forecast:
            weather = target_forecast['weather'][0]['main']
            temp = round(target_forecast['main']['temp'])
            print(f"The weather in Washington, DC on {target_date.strftime('%A')} is {weather}, and it is {temp}°F")
            engine.say((f"The weather in Washington, DC on {target_date.strftime('%A')} is {weather}, and it is {temp}°F"))
            engine.runAndWait()
        else:
            print("No weather information available for the specified day")
            #engine.say("No weather information available for the specified day")

        #engine.runAndWait()

# Variable to track whether "tomorrow" case is handled
handled_tomorrow = False

#Wake Word
def listen_for_wake_word(source):
   print("Listening for 'Hey Jarvis'")


   while True:
       audio = r.listen(source)
       try:
           text = r.recognize_google(audio, language='en')
           if "hey jarvis" in text.lower():
               print("Wake word detected.")
               engine.say(np.random.choice(greetings))
               engine.runAndWait()
               listen_and_respond(source)
               break
       except sr.UnknownValueError:
           pass
       


#Using ChatGPT responses
def listen_and_respond(source):
   print("Listening...")


   while True:
       audio = r.listen(source)
       try:
           text = r.recognize_google(audio, language='en')
           print("you said: {}".format(text))
           if not text:
               continue
           
           #Allows the user to play songs on Youtube
           if "play" in text.lower():
               song = text.lower().replace("play", "")
               engine.say("Playing "+ song)
               engine.runAndWait()
               pywhatkit.playonyt(song)
               continue
           
           
           
           #Allows user to ask about the weather
           if "weather" in text.lower():
                if "tomorrow" in text.lower():
                    current_weather("tomorrow")
               #Extract the day of the week mentioned in the query
                day_match = re.search(r"\b([A-Za-z]+day)\b", text)
                if day_match:
                    target_day = day_match.group(1).lower()
                    current_weather(target_day)
                else:
                    # If no specific day mentioned, assume today's weather
                    current_weather("today")
                continue
           
  

           #Sending text to ChatGPT
           response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "{}".format(text)}])
           response_text = response.choices[0].message.content
           print("OpenAI response: {}".format(response_text))

           #Say answer
           engine.say(response_text)
           engine.runAndWait()



           #Check Scheduled Reminders
           check_reminders()
           time.sleep(1)


           #if not audio:
               #listen_for_wake_word(source)
       except sr.UnknownValueError:
           time.sleep(2)
           print("silence, listening...")
           listen_for_wake_word(source)
           continue


       except sr.RequestError as e:
           print("could not request results; {}".format(e))
           engine.say("could not request results; {}".format(e))
           engine.runAndWait()
           listen_for_wake_word(source)
           continue
       


# Main Function
def main():


    #Start listening for wake word and responding
    with sr.Microphone() as source:
        while True:
            try:
                listen_for_wake_word(source)
            except RuntimeError as e:
                print("Error:", e)
                listen_for_wake_word(source)


if __name__ == "__main__":
    main()
