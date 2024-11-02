from flask import Flask, render_template, request, jsonify
import cv2
import pygame
import os
import speech_recognition as sr

app = Flask(__name__)

# Use the absolute path to your static folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLICK_SOUND_PATH = r"C:\Users\ASUS\Desktop\capture\VoiceCapture\temp_audio.wav"
IMAGE_PATH = os.path.join(BASE_DIR, "static", "captured_photo.jpg")  # Absolute path to static folder

def play_click_sound():
    if os.path.exists(CLICK_SOUND_PATH):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(CLICK_SOUND_PATH)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
        except pygame.error as e:
            print(f"Error playing sound: {e}")
    else:
        print("Click sound file not found!")

def listen_for_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for 'cheese'...")
        audio = r.listen(source)  # Listen for audio input
    try:
        command = r.recognize_google(audio).lower()
        print(f"Recognized command: {command}")
        return command
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

def capture_image():
    # Listen for the "cheese" command
    command = listen_for_command()
    if command == "capture":
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            print("Error: Could not open the camera.")
            return None
        ret, frame = cam.read()
        if ret:
            play_click_sound()  # Play click sound
            cv2.imwrite(IMAGE_PATH, frame)  # Save the captured image to the absolute path in the static folder
            print(f"Photo saved as '{IMAGE_PATH}'")  # Print the full path
        else:
            print("Error: Could not capture image.")
            return None
        cam.release()
        cv2.destroyAllWindows()
        return IMAGE_PATH
    else:
        print("No valid command recognized, no image captured.")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture():
    image_path = capture_image()
    if image_path:
        return jsonify({"status": "success", "image_url": "/" + os.path.relpath(image_path, BASE_DIR)})
    else:
        return jsonify({"status": "error", "message": "Could not capture image"}), 500

if __name__ == "__main__":
    app.run(debug=True)
