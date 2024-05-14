import os, json, traceback, io

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
    video_buffer = io.BytesIO()

    while True:
        try:
            print("Working till now1")

            data = await ws.receive_text()
            request_data = json.loads(data)
            language = request_data["lang"]
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

                print("Working till now3")

                # model = genai.GenerativeModel(
                #     model_name="gemini-1.5-pro-latest",
                #     generation_config=generation_config,
                #     safety_settings=SAFETY_SETTINGS,
                # )

                # path = "test_vid_audio_ws.mp3"
                # audiofile = genai.upload_file(path=path, display_name=path)

                # print("Working till now4")

                # prompt = f"""
                # Translate the provided audio file into {language} for subtitle creation (follow the json schema), ensuring clarity and accessibility for  {language}  speakers unfamiliar with different culture. Identify any culturally specific phrases or terms in the lyrics that might require additional explanation for an international audience.
                # For each culturally specific term, include an entry in the 'culturalLexicon' within the JSON output. This will help {language} users understand not just the language but also the cultural context of the lyrics.

                # Here's the JSON schema
                # {LLM_SUBTITLE_SCHEMA}
                # Please ensure the Subtitles are accurate and follwing json schema and the explanations are detailed enough to convey the deeper meanings and cultural significance of the terms.
                # """

                # # Configuration for generative AI model, specifying a longer timeout for processing audio and text.
                # model = genai.GenerativeModel(
                #     model_name="gemini-1.5-pro-latest",
                #     generation_config={"response_mime_type": "application/json"},
                # )
                # response = model.generate_content(
                #     [prompt, audiofile], request_options={"timeout": 180}
                # )
                # print(response.text)

                # print("Working till now5")

                # save this data to a file:
                # gemini_res = json.loads(response.text)
                gemini_res = [
                    {
                        "startTime": "00:00",
                        "endTime": "00:53",
                        "Subtitle": "",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "00:53",
                        "endTime": "01:03",
                        "Subtitle": "मजबूरी को आगे बुलाऊं, आने जाने की आदत को ज़हर बना, हाँ तेरी पी जाऊं मैं पूरी",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "01:03",
                        "endTime": "01:18",
                        "Subtitle": "आना था वो नहीं आया, दिल बाग बाग मेरा टकराया, कागा बोल के दस जावे,  पावें क्यों उसकी सूरी। रावां च बावां च उनको ढूंढू, कोई मुझे ना रोके",
                        "culturalLexicon": [
                            {
                                "term": "कागा बोल के दस जावे",
                                "explanation": "This phrase refers to seeking guidance or a message from a crow, often seen as a messenger in South Asian folklore. It reflects the protagonist's desperation in seeking answers about their beloved.",
                            },
                            {
                                "term": "पावें क्यों उसकी सूरी",
                                "explanation": " सूरी translates to 'clue'. The protagonist wonders why they are unable to find any clue of their beloved's whereabouts.",
                            },
                        ],
                    },
                    {
                        "startTime": "01:18",
                        "endTime": "01:28",
                        "Subtitle": "मेरे ढोल जुदाईयां दी, तेनू खबर किवें होवे, आ जावे दिल तेरा पूरा भी ना होवे",
                        "culturalLexicon": [
                            {
                                "term": "ढोल जुदाईयां दी",
                                "explanation": "This metaphor uses 'ढोल', a traditional drum, to represent the sound of separation. It signifies that the pain of separation is so profound that it resonates like the beating of a drum, a sound that is hard to ignore.",
                            }
                        ],
                    },
                    {
                        "startTime": "01:28",
                        "endTime": "01:38",
                        "Subtitle": "हां बड़ियां बनाइयां दी, गल बात किवें होवे, आ जावे दिल तेरा पूरा भी ना होवे",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "01:38",
                        "endTime": "01:47",
                        "Subtitle": "",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "01:47",
                        "endTime": "02:07",
                        "Subtitle": "भूल गई मजबूरी नु, दुनिया दी दस्तूरी नु, साथ तेरा है बथेरा, पूरा कर ज़रूरी नु। आना था वो नहीं आया, रास्ता ना दिखलाया, तुम्हारा ते सहारा,  ख्वाहिश अधूरी नु। सारी मैं जावां मैं तेनू बुलावां, गल सारी तां होवे",
                        "culturalLexicon": [
                            {
                                "term": "दुनिया दी दस्तूरी",
                                "explanation": "This phrase refers to societal norms and expectations. The protagonist is expressing their willingness to defy societal expectations for their love.",
                            }
                        ],
                    },
                    {
                        "startTime": "02:07",
                        "endTime": "02:18",
                        "Subtitle": "मेरे ढोल जुदाईयां दी, तेनू खबर किवें होवे, आ जावे दिल तेरा पूरा भी ना होवे",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "02:18",
                        "endTime": "02:28",
                        "Subtitle": "हां बड़ियां बनाइयां दी, गल बात किवें होवे, आ जावे दिल तेरा पूरा भी ना होवे",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "02:28",
                        "endTime": "02:40",
                        "Subtitle": "",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "02:40",
                        "endTime": "02:44",
                        "Subtitle": "मेरे ढोल जुदाईयां दी, सर्दारी ना होवे",
                        "culturalLexicon": [
                            {
                                "term": "सर्दारी ना होवे",
                                "explanation": "This phrase implies that the pain of separation does not discriminate. It affects everyone equally, regardless of their social status (represented by 'सर्दारी').",
                            }
                        ],
                    },
                    {
                        "startTime": "02:44",
                        "endTime": "02:50",
                        "Subtitle": "मेरे ढोल जुदाईयां दी",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "02:50",
                        "endTime": "03:00",
                        "Subtitle": "",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "03:00",
                        "endTime": "03:04",
                        "Subtitle": "मेरे ढोल जुदाईयां दी, सर्दारी ना होवे",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "03:04",
                        "endTime": "03:10",
                        "Subtitle": "दिलदारां दी सब यारां दी, आज़ादी ना होवे",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "03:10",
                        "endTime": "03:15",
                        "Subtitle": "दिलदारां दी सब यारां दी, आज़ादी ना होवे",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "03:15",
                        "endTime": "03:26",
                        "Subtitle": "आज ले ले के तुझे, है जहाँ से ले, तू है वही",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "03:26",
                        "endTime": "03:36",
                        "Subtitle": "तेरी कमी, बना दे सज़ा दे पन्ना के हमें",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "03:36",
                        "endTime": "03:41",
                        "Subtitle": "बना दे सज़ा दे पन्ना के हमें",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "03:41",
                        "endTime": "03:45",
                        "Subtitle": "",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "03:45",
                        "endTime": "03:55",
                        "Subtitle": "आगे लावां मजबूरी नु, आण जान ति बसुड़ी नु, ज़हर बने, हां तेरी पी जावां मैं पूरी नु। रावां च बावां च उनुं लुकावं",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "03:55",
                        "endTime": "04:10",
                        "Subtitle": "कोई मेनु ना रोके, मेरे ढोल जुदाईयां दी, तेनू खबर किवें होवे, आ जावे दिल तेरा पूरा भी ना होवे",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "04:10",
                        "endTime": "04:20",
                        "Subtitle": "हां बड़ियां बनाइयां दी, गल बात किवें होवे, आ जावे दिल तेरा पूरा भी ना होवे",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "04:20",
                        "endTime": "04:24",
                        "Subtitle": "पूरा भी ना होवे",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "04:24",
                        "endTime": "04:26",
                        "Subtitle": "पूरा भी ना होवे",
                        "culturalLexicon": [],
                    },
                    {
                        "startTime": "04:26",
                        "endTime": "04:36",
                        "Subtitle": "",
                        "culturalLexicon": [],
                    },
                ]

                await ws.send_json(gemini_res)
                webvtt_content = json_to_webvtt(gemini_res)
                print(webvtt_content)

                print("Working till now6")

                current_dir = os.path.dirname(os.path.realpath(__file__))
                file_path = os.path.join(current_dir, "../frontend/public/subtitle.vtt")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(webvtt_content)

                # send webvtt content to the ui
                # await ws.send_json({"webvtt": webvtt_content})

                # send this file back to the ui.

                # apply the agent here that will generate the images related to the specific music video
                video_buffer = io.BytesIO()

        except WebSocketDisconnect:
            break

        except Exception as e:
            traceback.print_exc()
            print(e)  # Log the exception traceback
            break
