# app.py
import os
import requests
import warnings
from openai import OpenAI
from elevenlabs import generate, set_api_key
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import streamlit as st

# Suppress MoviePy warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Initialize API clients
client = from openai import OpenAI

client = OpenAI(api_key="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")
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {str(e)}")
set_api_key(st.secrets["ELEVENLABS_API_KEY"])

def generate_script(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a video scriptwriter. Create a concise 30-second script with 4 scenes."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Script generation failed: {str(e)}")
        return None

def generate_image(prompt, filename):
    try:
        response = client.images.generate(
            prompt=prompt,
            n=1,
            size="256x256"
        )
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        with open(filename, 'wb') as f:
            f.write(img_data)
        return filename
    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")
        return None

def generate_voiceover(text, filename):
    try:
        audio = generate(
            text=text,
            voice="Rachel",
            model="eleven_monolingual_v1"
        )
        with open(filename, 'wb') as f:
            f.write(audio)
        return filename
    except Exception as e:
        st.error(f"Voiceover generation failed: {str(e)}")
        return None

def create_video(image_paths, audio_path, output_path):
    try:
        clips = [ImageClip(img).set_duration(5) for img in image_paths if img is not None]
        video_clip = concatenate_videoclips(clips)
        audio_clip = AudioFileClip(audio_path)
        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(output_path, fps=24)
        return output_path
    except Exception as e:
        st.error(f"Video creation failed: {str(e)}")
        return None

# Streamlit UI
st.title("AI Video Generator 🎥")
user_prompt = st.text_input("Enter your video idea (e.g., 'Robots exploring Mars')")

if user_prompt:
    with st.spinner("Creating your video..."):
        try:
            # Step 1: Generate script
            script = generate_script(user_prompt)
            if not script:
                st.stop()
            
            st.subheader("Generated Script")
            st.write(script)

            # Step 2: Create images
            scenes = [line for line in script.split('\n') if line.strip()]
            image_paths = []
            for i, scene in enumerate(scenes[:4]):  # Limit to 4 scenes
                img_path = generate_image(scene, f"scene_{i}.jpg")
                if img_path:
                    image_paths.append(img_path)
                    st.image(img_path, caption=f"Scene {i+1}")

            # Step 3: Generate voiceover
            audio_path = generate_voiceover(script, "narration.mp3")
            if audio_path:
                st.audio(audio_path)

            # Step 4: Create video
            if image_paths and audio_path:
                video_path = create_video(image_paths, audio_path, "output.mp4")
                if video_path:
                    st.video(video_path)
                    with open(video_path, "rb") as f:
                        st.download_button(
                            label="Download Video",
                            data=f,
                            file_name="ai_video.mp4",
                            mime="video/mp4"
                        )
                
                # Cleanup temporary files
                for img in image_paths:
                    os.remove(img)
                os.remove(audio_path)
                os.remove(video_path)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
