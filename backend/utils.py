import moviepy.editor as mp
import os


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

        # Add cultural notes if available
        # if item.get("culturalLexicon", []):
        #     for note in item["culturalLexicon"]:
        #         webvtt += f"\n{start} --> {end} .cultural-note\n"
        #         webvtt += f"{note['term']}: {note['explanation']}\n"

        # Add subtitle
        subtitle = item["Subtitle"]
        webvtt += f"\n{start} --> {end} c\n{subtitle}\n"

    return webvtt
