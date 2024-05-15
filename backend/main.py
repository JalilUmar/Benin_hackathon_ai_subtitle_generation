import os, json, traceback, io, time, operator

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
import google.generativeai as genai
from utils import (
    SAFETY_SETTINGS,
    LLM_SUBTITLE_SCHEMA,
    json_to_webvtt,
    extract_audio,
    get_agent_tools,
)
from typing import Annotated, Sequence, TypedDict


# agentic imports:
from langchain_openai import ChatOpenAI
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_community.utilities.serpapi import SerpAPIWrapper

from langgraph.prebuilt import ToolInvocation
from langgraph.prebuilt import ToolExecutor
from langgraph.graph import StateGraph, END
from langchain_core.messages import FunctionMessage

from dotenv import load_dotenv, find_dotenv


_: bool = load_dotenv(find_dotenv())

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

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
                await ws.send_json({"json_res": gemini_res})

                print("Gemini response send to client ... \n\n")

                # resetting video buffer.
                video_buffer = io.BytesIO()

                # apply the agent here that will generate the images related to the specific music video
                model = ChatOpenAI(
                    temperature=0.8,
                    model="gpt-4-1106-preview",
                    streaming=True,
                    max_retries=5,
                    api_key=OPENAI_API_KEY,
                )

                # Agent tools
                agent_tools = get_agent_tools(ws)

                # Converting tools to openai functions
                functions = [convert_to_openai_function(t) for t in agent_tools]
                model = model.bind_functions(functions)

                class AgentState(TypedDict):
                    messages: Annotated[Sequence[BaseMessage], operator.add]

                tool_executor = ToolExecutor(agent_tools)

                def should_continue(state):
                    messages = state["messages"]
                    last_message = messages[-1]
                    # If there is no function call, then we finish
                    if "function_call" not in last_message.additional_kwargs:
                        return "end"
                    # Otherwise if there is, we continue
                    else:
                        return "continue"

                def call_model(state):
                    messages = state["messages"]
                    response = model.invoke(messages)
                    # We return a list, because this will get added to the existing list
                    return {"messages": [response]}

                async def call_tool(state):
                    messages = state["messages"]
                    last_message = messages[-1]

                    action = ToolInvocation(
                        tool=last_message.additional_kwargs["function_call"]["name"],
                        tool_input=json.loads(
                            last_message.additional_kwargs["function_call"]["arguments"]
                        ),
                    )
                    # call the tool_executor and get back a response
                    response = await tool_executor.ainvoke(action)

                    function_message = FunctionMessage(
                        content=str(response), name=action.tool
                    )
                    # We return a list, because this will get added to the existing list
                    return {"messages": [function_message]}

                # Defining a new state graph
                workflow = StateGraph(AgentState)

                # Define the two nodes we will cycle between
                workflow.add_node("agent", call_model)
                workflow.add_node("action", call_tool)

                workflow.set_entry_point("agent")

                workflow.add_conditional_edges(
                    "agent", should_continue, {"continue": "action", "end": END}
                )

                # We now add a normal edge from `tools` to `agent`.
                # This means that after `tools` is called, `agent` node is called next.
                workflow.add_edge("action", "agent")

                app = workflow.compile()
                full_response = """"""

                system_prompt = f"""
                You are a multimodal AI AGENT specializing in music understanding and visual representation. Your task is to analyze song lyrics, generate evocative images, and provide a comprehensive summary of the song's message.
                                
                For every song transcript you receive, you must:
                Generate Images: 
                Craft three detailed prompts for a Stable Diffusion model to create images that capture the essence, emotions, and symbolism of the song. Send these prompts to the designated image generation tool and await confirmation of successful image creation.
                Summarize the Song: 
                Once the images are generated, provide a comprehensive summary of the song, analyzing its theme, emotions, imagery, and cultural context (if relevant).

                Important Considerations:
                1. Prompt Quality: 
                Invest time in crafting high-quality image prompts that are descriptive, evocative, and specific. The quality of the generated images depends heavily on your prompts.
                2. Style Diversity: 
                Try to create prompts that result in images with different styles, perspectives, or moods to offer a multifaceted visual representation of the song.
                3. Summary Depth: 
                Your song summary should be detailed and insightful, demonstrating a deep understanding of the lyrics and their nuances.
                
                Remember: Your primary function is to generate images that capture the essence of the song. The song summary is provided after successful image generation. This workflow ensures a complete and meaningful artistic interpretation of the provided song lyrics.
                """

                inputs = {
                    "messages": [
                        SystemMessage(content=system_prompt),
                        HumanMessage(
                            content=f"""
                            SONG TEXT TRANSCRIPT:
                            {gemini_res}
                            """
                        ),
                    ],
                }

                async for event in app.astream_events(inputs, version="v1"):
                    kind = event.get("event")

                    if kind == "on_chat_model_stream":
                        content = event["data"]["chunk"].content

                        if content:
                            if isinstance(content, bytes):
                                content_str = content.decode(
                                    "utf-8",
                                )
                            else:
                                content_str = content

                            full_response += content_str
                            # yield content.encode("utf-8")
                            # await ws.send_text(content_str)
                            print(content_str)

                    elif kind == "on_tool_start":
                        print(
                            f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}"
                        )
                        print("--")

                    elif kind == "on_tool_end":
                        print(f"Done tool: {event['name']}")
                        print(f"Tool output was: {event['data'].get('output')}")
                        print("--")

        except WebSocketDisconnect:
            break

        except Exception as e:
            traceback.print_exc()
            print(e)  # Log the exception traceback
            break
