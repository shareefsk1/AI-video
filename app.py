import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)
import os
from openai import OpenAI
from elevenlabs import generate, set_api_key
import requests
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import streamlit as st

# Load API keys
openai.api_key = st.secrets["OPENAI_API_KEY"]
set_api_key(st.secrets["ELEVENLABS_API_KEY"])

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_script(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Write a 30-second video script about: {prompt}"}]
    )
    return response.choices[0].message.content

def generate_image(prompt, filename):
    response = openai.Image.create(prompt=prompt, n=1, size="256x256")
    image_url = response['data'][0]['url']
    img_data = requests.get(image_url).content
    with open(filename, 'wb') as f:
        f.write(img_data)
    return filename

def generate_voiceover(text, filename):
    audio = generate(text=text, voice="Rachel", model="eleven_monolingual_v1")
    with open(filename, 'wb') as f:
        f.write(audio)
    return filename

def create_video(image_paths, audio_path, output_path):
    clips = [ImageClip(img).set_duration(5) for img in image_paths]
    video = concatenate_videoclips(clips)
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)
    video.write_videofile(output_path, fps=24)

# Streamlit UI
st.title("Free AI Video Generator 🎬")
user_prompt = st.text_input("Enter your video idea (e.g., 'A cat learning Python')")

if user_prompt:
    st.write("Generating script...")
    script = generate_script(user_prompt)
    
    st.write("Generating images...")
    image_paths = [generate_image(scene, f"scene_{i}.jpg") for i, scene in enumerate(script.split("\n"))]
    for img in image_paths:
        st.image(img)
    
    st.write("Generating voiceover...")
    audio_path = generate_voiceover(script, "voiceover.mp3")
    st.audio(audio_path)
    
    st.write("Creating video...")
    create_video(image_paths, audio_path, "output.mp4")
    st.video("output.mp4")
    st.download_button("Download Video", "output.mp4")
