# imports
from cv2 import VideoCapture
from pynput import keyboard
from playsound import playsound
import openai as OpenAI
import speech_recognition as sr
import base64
import time
import cv2
import os

# constants
TEMP_FILE_NAME = "placeholder.mp3"
TEMP_IMAGE_NAME = "placeholder.jpg"

# key press check
record = False
replay_prompt = False
end = False

# button press detection
class Keyboard:
    def on_press(key):
        try:
            global record, replay_prompt, end
            if key.char == ('r'):
                record = True
            if key.char == ('p'):
                replay_prompt = True
            if key.char == ('q'):
                end = True
        except AttributeError:
            print('special key {0} pressed'.format(
                key))
    def on_release(key):
        return
    
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
        os.remove(TEMP_FILE_NAME)

    def listen_audio(self):
        # listen and transcript recorded voice
        with sr.Microphone(device_index=3) as source:
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
                error = "Sorry, I could not understand that. Could you say that again?"
                self.speak(error)
                # retry query
                self.query_gpt()
            except sr.RequestError as e:
                error = "Could not request results; {0}".format(e)
                self.speak(error)
                return None
    
    def get_user_prompt(self):
        if self.user_prompt is not None:
            # play last prompt 
            self.speak(self.user_prompt)

    def screenshot(self):
        # get image data from camera
        cam = VideoCapture(0, cv2.CAP_DSHOW)

        # error
        if not cam.isOpened():
            self.speak("Sorry, there was an error opening the video device.")
            return False
        
        # get one frame from the camera
        result, image = cam.read()

        if result:
            cv2.imwrite(TEMP_IMAGE_NAME, image)
            cam.release()
            return True
        # error
        else:
            self.speak("Sorry, there was an error reading the frame from the video device.")
            cam.release()
            return False

    def query_gpt(self):
        # get query from user
        query = self.listen_audio()
        # screenshot environment
        image_succ = self.screenshot()

        if query == None or image_succ == False:
            # error and exit
            return
        else:
            image = cv2.imread(TEMP_IMAGE_NAME)
            # error and exit
            if image is None:
                self.speak("Sorry, there was an error loading the image.")
                return
            
            # convert image to base64
            buffer = cv2.imencode('.jpg', image)[1]
            b64image = base64.b64encode(buffer).decode('utf-8')
            
            # time length
            start = time.time()

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
            
            end = time.time()
            print("time: ", (end-start), "s")

            # get response
            self.speak(response)

            # remove image
            os.remove(TEMP_IMAGE_NAME)
            
# start vision analysis
def main():
    global record, replay_prompt, end
    client = GPT()
    # press button to start request
    listener = keyboard.Listener(on_press=Keyboard.on_press, on_release=Keyboard.on_release)
    listener.start()
    # continue service until ended by user
    while not end:
        if record:
            client.query_gpt()
            record = False
        if replay_prompt:
            client.get_user_prompt()
            replay_prompt = False
    # end service
    client.speak("See you next time, goodbye!")
    
if __name__ == "__main__":
    main()