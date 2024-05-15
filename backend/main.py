import os, json, traceback, io, time

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
import google.generativeai as genai
from utils import SAFETY_SETTINGS, LLM_SUBTITLE_SCHEMA, json_to_webvtt, extract_audio

app = FastAPI()

genai.configure(api_key="AIzaSyBbZqL2pKUK9k8j-oYSLgnNMFS--wzFqek")

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "response_mime_type": "application/json",
}


@app.websocket("/subtitle/ws")
async def video_subtitle_generator(ws: WebSocket):
    await ws.accept()
    print("Websocket started ...\n\n")
    video_buffer = io.BytesIO()

    while True:
        try:
            data = await ws.receive_text()
            request_data = json.loads(data)
            language = request_data["lang"]
            print("language", language)

            chunk = bytearray(request_data["videoChunk"])
            video_buffer.write(chunk)
            print(
                "Received chunk. Total bytes in buffer:", len(video_buffer.getvalue())
            )
            if request_data["isLastChunk"]:
                video_buffer.seek(0)
                with open("test_vid_audio_ws.mp4", "wb") as f:
                    bytes_written = f.write(video_buffer.read())
                    print(f"Wrote {bytes_written} bytes to video file")

                extract_audio("test_vid_audio_ws.mp4")

                print("Last chunk reieved and video file written ...\n\n")

                max_retries = 3
                for attempt in range(max_retries):
                    try:

                        model = genai.GenerativeModel(
                            model_name="gemini-1.5-pro-latest",
                            generation_config=generation_config,
                            safety_settings=SAFETY_SETTINGS,
                        )

                        path = "test_vid_audio_ws.mp3"
                        audiofile = genai.upload_file(path=path, display_name=path)

                        print("Audio uploaded to gemini ...\n\n")

                        # prompt = f"""
                        # ##TASK##
                        # You are a skilled audio translator and transcriber.  You will receive an audio song and a target language. Your job is to translate the song into the target language, ensuring clarity and accessibility for speakers unfamiliar with the song's cultural context.

                        # ##INSTRUCTIONS##

                        # 1. **Analyze the language of the audio.**
                        # 2. **If the audio language and target language are the same, transcribe the song accurately.**
                        # 3. **If the languages are different, translate the lyrics into the target language.**
                        # 4. **Identify culturally specific phrases or terms in the lyrics.**
                        # 5. **Provide a 'culturalLexicon' for each culturally specific term to help non-native listeners understand the context.**
                        # 6. **Strictly adhere to the provided JSON schema for output.**

                        # ##INPUT##
                        # Target Language: "{language}"

                        # ##OUTPUT JSON SCHEMA##
                        # {LLM_SUBTITLE_SCHEMA}
                        # """

                        print("language", language)
                        prompt = f"""
                        ##TASK##
                        Translate the provided audio song file into **{language}** for subtitle creation (follow the json schema), ensuring clarity and accessibility for **{language}** speakers unfamiliar with different cultures. 

                        **IMPORTANT**: Please ensure that the translation is in the target language (**{language}**) and not in the source language (the language of the audio file). 

                        Identify any culturally specific phrases or terms in the lyrics that might require additional explanation for an international audience. For each culturally specific term, include an entry in the 'culturalLexicon' within the JSON output. This will help **{language}** users understand not just the language but also the cultural context of the lyrics.

                        ##output json Schema##
                        {LLM_SUBTITLE_SCHEMA}
                        
                        
                        ##instruction##

                        1. Please provide a translation of the song in the target language (**{language}**).
                        2. 'culturalLexicon' should be provided to better explain subtitles.
                        3. The response should always follow the provided schema.
                        4. **Double-check** that the translation is in the target language (**{language}**) and not in the source language (the language of the audio file).
                        """

                        # Configuration for generative AI model, specifying a longer timeout for processing audio and text.
                        model = genai.GenerativeModel(
                            model_name="gemini-1.5-pro-latest",
                            generation_config={
                                "response_mime_type": "application/json"
                            },
                        )
                        response = model.generate_content(
                            [prompt, audiofile], request_options={"timeout": 180}
                        )
                        print(response.text)
                        print("Gemini responsded successfully ... \n\n")

                        print("Converting gemini response to json... \n\n")
                        # save this data to a file:
                        gemini_res = json.loads(response.text)

                        break
                    except Exception as e:
                        print(f"Attempt {attempt + 1} failed with exception: {e}")
                        if attempt < max_retries - 1:
                            print("Retrying...")
                            time.sleep(1)
                        else:
                            print("Maximum retries exceeded. Exiting...")

                webvtt_content = json_to_webvtt(gemini_res)
                print(webvtt_content)

                print("WebVtt created successfully ....\n\n")

                current_dir = os.path.dirname(os.path.realpath(__file__))
                file_path = os.path.join(current_dir, "../frontend/public/subtitle.vtt")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(webvtt_content)

                print("Subtitles file written successfully ... \n\n")

                # sending complete json data back to client
                await ws.send_json(gemini_res)

                print("Gemini response send to client ... \n\n")

                # send this file back to the ui.

                # apply the agent here that will generate the images related to the specific music video
                video_buffer = io.BytesIO()

        except WebSocketDisconnect:
            break

        except Exception as e:
            traceback.print_exc()
            print(e)  # Log the exception traceback
            break
