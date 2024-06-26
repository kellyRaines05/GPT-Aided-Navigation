# imports
from playsound import playsound
import openai as OpenAI
import speech_recognition as sr
import numpy as np
import base64
import time
import os

# constants
TEMP_FILE_NAME = "C:/Users/18155/Programming/research/placeholder.mp3"

# chatGPT functions
class GPT:
    def __init__(self):                                                         
        # create client for API calls to chatGPT
        self.client = OpenAI.OpenAI()
        # provide system prompt
        self.system_prompt = "You are an assistant for the visually impaired and blind. You respond to queries about the surrounding \
            envrionment to help them navigate based on the images provided to you. It is very important to be detailed by providing \
            cardinal directions and/or rough estimates of size, number, or color of objects. Please try to keep responses brief. Avoid \
            unnecessary details that are not related to the environment, navigation, or resources for the visually impaired/blind user."
        self.user_prompt = None
    
    def speak(self, phrase):
        response = self.client.audio.speech.create(
                model="tts-1",
                voice="fable",
                input=phrase
                )
        # stream response to file
        response.stream_to_file(TEMP_FILE_NAME)
        # play and write audio
        playsound(TEMP_FILE_NAME)
        print("ChatGPT: " + phrase)
        # remove the file
        time.sleep(1)
        os.remove(TEMP_FILE_NAME)

    def listen_audio(self):
        # listen and transcript recorded voice
        with sr.Microphone(device_index=1) as source:
            print("Listening...")
            recognize = sr.Recognizer()
            audio = recognize.listen(source)
            try:
                # get user query
                self.user_prompt = recognize.recognize_google(audio)
                print("You: " + self.user_prompt)
                return self.user_prompt
            except sr.UnknownValueError:
                # error
                error = "Sorry, I could not understand that. Press r to try again."
                self.speak(error)
            except sr.RequestError as e:
                error = "Could not request results; {0} Press r to try again.".format(e)
                self.speak(error)
                return None
    
    def get_user_prompt(self):
        if self.user_prompt is not None:
            # play last prompt
            self.speak(self.user_prompt)
        else:
            self.speak("No chat history. Please ask a query.")

    def query_gpt(self, image):
        # get query from user
        query = self.listen_audio()
        # # screenshot environment
        # image_succ = self.screenshot()
        # error and exit
        if query == None:
            return
        else:
            try:
                # convert carla.libcarla.Image to base64
                array = np.frombuffer(image.raw_data, dtype=np.uint8)
                b64image = base64.b64encode(array).decode('utf-8')
                
                # send request parameters
                result = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        { "role": "system", "content": self.system_prompt},
                        { "role": "user", "content": [
                                {"type": "text", "text": query,}, 
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64image}"}}
                            ]
                        }
                    ],
                    max_tokens=800,
                )
                
                response = result.choices[0].message.content

                # get response
                self.speak(response)
            # error and exit
            except:
                self.speak("Sorry, there was an error getting the image.")