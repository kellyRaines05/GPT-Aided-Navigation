# imports
from playsound import playsound
import openai as OpenAI
import speech_recognition as sr
import numpy as np
from word2number import w2n
import base64
import time
import os

# constants
TEMP_FILE_NAME = "placeholder.mp3"
TEMP_IMAGE_NAME = "placeholder.jpg"
device = 1 # mic

# chatGPT functions
class GPT:
    def __init__(self):
        self.speed = 1.0 # default voice speed                                                     
        # create client for API calls to chatGPT
        self.client = OpenAI.OpenAI()
        # provide system prompt
        self.system_prompt = '''
            You are a personal navigation assistant for the visually impaired and blind. You will be given an image of their current surroundings which they cannot fully see.
            Your job is to help the user by using the contents of the image to inform them of their surroundings or help them safely navigate to a certain location by 
            carefully instructing actions they should take such as turning towards a certain direction and moving towards their desired target. There may be several obstacles
            they must be made aware of to ensure their safety. Also, you must inform them of safety warnings by reading signs or telling them about other visual cues like whether
            a stoplight is red or if the pedestrian symbol is on. If the user ever needs to cross the road to get to a certain location as instructed ensure that they are told how
            to get to a crosswalk before telling them to follow a certain sidewalk. Please provide important details in your responses such as cardinal directions, spatial
            relationships, estimates/measurements of distance, size, number, or color of important objects. Keep responses brief, around 2-3 sentences. Avoid unnecessary details
            unrelated to the environment, navigation, or resources for the user. Avoid offensive language in which instructions tell users "you should see" or use visual references
            as indications or instructions for their navigation, rather only used as additional information to describe their surroundings. Do NOT make a numbered list of steps in
            your instructions, but speak to the user only in a conversational format.
         '''
        self.user_prompt = None
        # speech input
        self.recognize = sr.Recognizer()
    
    def speak(self, phrase, speed):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="fable",
            input=phrase,
            speed=speed
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
        with sr.Microphone(device_index=device) as source:
            print("Listening...")
            audio = self.recognize.listen(source)
            try:
                # get user query
                self.user_prompt = self.recognize.recognize_google(audio)
                print("You: " + self.user_prompt)
                return self.user_prompt
            except sr.UnknownValueError:
                # error
                error = "Sorry, I could not understand that."
                self.speak(error, self.speed)
            except sr.RequestError as e:
                error = "Could not request results; {0}".format(e)
                self.speak(error, self.speed)
                return None
    
    def get_user_prompt(self):
        if self.user_prompt is not None:
            # play last prompt
            self.speak(self.user_prompt, self.speed)
        else:
            self.speak("No chat history. Please ask a query.", self.speed)

    def query_gpt(self):
        # get query from user
        query = self.listen_audio()
        # # screenshot environment
        # image_succ = self.screenshot()
        # error and exit
        if query == None:
            return
        else:
            try:
                # convert carla.libcarla.Image (jpg) to base64
                with open(TEMP_IMAGE_NAME, 'rb') as img_file:
                    b64image = base64.b64encode(img_file.read()).decode('utf-8')
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
                    max_tokens=500,
                )
                response = result.choices[0].message.content

                # get response
                self.speak(response, self.speed)
            # error and exit
            except Exception as e:
                print(f"Error: {e}")
                self.speak("Sorry, there was an error getting the image.", self.speed)
        os.remove(TEMP_IMAGE_NAME)

    def change_speed(self):
        with sr.Microphone(device_index=device) as source:
            print("Listening...")
            audio = self.recognize.recognize_google(self.recognize.listen(source))
            try:
                new_speed = w2n.word_to_num(audio)
                self.speak(f"Current speed at {self.speed}, changing it to {new_speed}", self.speed)
                self.speed = new_speed
                print(new_speed)
            except:
                self.speak("No new speed detected.", self.speed)