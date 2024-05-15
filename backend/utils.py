import moviepy.editor as mp
import os

from fastapi import WebSocket
from langchain.tools import tool
import requests


from dotenv import load_dotenv, find_dotenv


_: bool = load_dotenv(find_dotenv())

STABILITY_AI_API_KEY = os.getenv("STABILITY_AI_API_KEY")


def extract_audio(video_path):
    # Load the video file
    video = mp.VideoFileClip(video_path)

    # Extract the audio from the video
    audio = video.audio

    # Get the video filename without extension
    video_filename = os.path.splitext(os.path.basename(video_path))[0]

    # Generate the output audio filename
    audio_filename = f"{video_filename}.mp3"

    # Write the audio to a file in the current directory
    audio.write_audiofile(audio_filename)

    print(f"Audio extracted and saved as: {audio_filename}")


SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

LLM_SUBTITLE_SCHEMA = [
    {
        "startTime": "00:00",
        "endTime": "00:03",
        "Subtitle": "Translated subtitle...",
        "culturalLexicon": [],
    },
    {
        "startTime": "00:03",
        "endTime": "00:07",
        "Subtitle": "Translated subtitle...",
        "culturalLexicon": [
            {
                "term": "specific term",
                "explanation": "Explanation providing cultural and contextual insight",
            }
        ],
    },
]


def convert_time(simple_time):
    """Converts MM:SS format to HH:MM:SS.sss format."""
    min_sec = simple_time.split(":")
    minutes = int(min_sec[0])
    seconds = int(min_sec[1])
    # Ensure it returns the time in HH:MM:SS.sss format
    return f"00:{minutes:02}:{seconds:02}.000"


def json_to_webvtt(json_data):
    """Converts JSON subtitles with cultural lexicon to WebVTT format with distinct styling for cultural notes."""

    webvtt = "WEBVTT\n\n"

    # Add cultural lexicon notes and subtitles
    for item in json_data:
        start = convert_time(item["startTime"])
        end = convert_time(item["endTime"])

        # Add subtitle
        subtitle = item["Subtitle"]
        webvtt += f"\n{start} --> {end} c\n{subtitle}\n"

    return webvtt


def get_agent_tools(websocket: WebSocket):

    @tool("stable_diffusion_image_generator", return_direct=True)
    async def image_generator(prompts: list[str]):
        """
        This tool will be used to generate high quality images for songs that will represent the theme of the songs
        """
        i = 0
        for prompt in prompts:
            response = requests.post(
                "https://api.stability.ai/v2beta/stable-image/generate/sd3",
                headers={
                    "authorization": f"Bearer {STABILITY_AI_API_KEY}",
                    "accept": "image/*",
                },
                files={"none": ""},
                data={
                    "prompt": prompt,
                    "output_format": "jpeg",
                },
            )
            i += 1
            if response.status_code == 200:
                current_dir = os.path.dirname(os.path.realpath(__file__))
                file_path = os.path.join(current_dir, f"../frontend/public/{i}.jpeg")
                # file_name = f"{i}.jpeg"
                with open(file_path, "wb") as file:
                    file.write(response.content)
                print(f"Image saved as {file_path}")
            else:
                "Image generation failed"

        await websocket.send_json({"message": "Image generation successfull"})

        return "Image generation successfull"

    return [image_generator]
