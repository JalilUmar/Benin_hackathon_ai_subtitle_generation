import streamlit as st
import subprocess


def video_file_player():
    # Create a placeholder for the file uploader
    uploader_placeholder = st.empty()
    subtitle_file = "./eng.vtt"  # Path to the subtitle file

    # Check if a video has been uploaded
    if "video_file" not in st.session_state:
        # Display the file uploader in the placeholder
        video_file = uploader_placeholder.file_uploader(
            "Upload a video...", type=["mp4", "mov", "avi", "mkv"]
        )
        if video_file is not None:
            # Save the video in the session state
            st.session_state["video_file"] = video_file
            # Clear the placeholder to remove the uploader widget
            uploader_placeholder.empty()
            # Display the video with or without subtitles
            st.video(
                st.session_state["video_file"],
                subtitles=subtitle_file if subtitle_file else None,
            )
    else:
        # Display the video that's saved in the session state with or without subtitles
        st.video(
            st.session_state["video_file"],
            subtitles=subtitle_file if subtitle_file else None,
        )


# Placeholder function for subtitle generation
def generate_subtitles(language, video_file):
    st.write(f"Generating subtitles in {language} for video: {video_file.name}")
    # # ... your subtitle generation logic here ...
    st.success("Subtitles generated successfully! (This is a dummy message)")


def main():
    st.title("AI Subtitle Generator")

    # Video file player
    video_file_player()

    # If a video has been uploaded, display the subtitle options
    if "video_file" in st.session_state:
        # Language selection for subtitles
        language = st.selectbox(
            "Select a language for subtitles",
            ("English", "French", "Spanish", "German", "Chinese"),
        )

        # Button to start subtitle generation
        if st.button("Generate Subtitles"):
            generate_subtitles(language, st.session_state["video_file"])


if __name__ == "__main__":
    main()


# import streamlit as st
# import base64

# # Define the cultural lexicons
# cultural_lexicons = [
#     {
#         "start": 0,
#         "end": 3,
#         "term": "Basant",
#         "explanation": "A spring festival in India and Pakistan celebrated by flying kites.",
#     },
#     {
#         "start": 10,
#         "end": 15,
#         "term": "Diwali",
#         "explanation": "A festival of lights celebrated by millions across the world.",
#     },
# ]


# def video_file_player():
#     # Placeholder for file uploader
#     uploader_placeholder = st.empty()
#     subtitle_file = "subtitles cokestudio eng.vtt"  # Path to the subtitle file

#     # Check if a video has been uploaded
#     if "video_file" not in st.session_state:
#         video_file = uploader_placeholder.file_uploader(
#             "Upload a video...", type=["mp4", "mov", "avi", "mkv"]
#         )
#         if video_file is not None:
#             # Save the uploaded video file in session state
#             st.session_state["video_file"] = video_file
#             uploader_placeholder.empty()  # Clear the uploader placeholder
#             display_video_with_lexicons(video_file)
#     elif "video_file" in st.session_state:
#         display_video_with_lexicons(st.session_state["video_file"])


# def display_video_with_lexicons(video_file):
#     # Convert the video file to base64
#     video_bytes = video_file.read()
#     video_base64 = base64.b64encode(video_bytes).decode("utf-8")

#     # Assume the subtitle file path is correct and encode it in base64 for embedding
#     try:
#         with open("eng.vtt", "rb") as sub_file:
#             subtitle_bytes = sub_file.read()
#             subtitle_base64 = base64.b64encode(subtitle_bytes).decode("utf-8")
#             subtitle_src = f"data:text/vtt;base64,{subtitle_base64}"
#     except FileNotFoundError:
#         st.error("Subtitle file not found.")
#         subtitle_src = ""

#     # Embed video and attach JavaScript for updating the lexicon based on time
#     video_html = f"""
#     <video id='videoElement' width='720' height='405' controls>
#       <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
#       <track label="English" kind="subtitles" srclang="en" src="{subtitle_src}" default>
#       Your browser does not support the video tag.
#     </video>
#     <script>
#     const videoElement = document.getElementById('videoElement');
#     videoElement.addEventListener('timeupdate', () => {{
#         const currentTime = videoElement.currentTime;
#         window.parent.postMessage({{{{type: 'streamlit:setComponentValue', value: currentTime}}}}, '*');
#     }});
#     </script>
#     """
#     st.markdown(video_html, unsafe_allow_html=True)
#     # st.markdown(st.session_state)

#     # Container for cultural lexicon
#     lexicon_container = st.empty()
#     update_lexicon_display(lexicon_container)


# def update_lexicon_display(lexicon_container):
#     # Function to update lexicon display
#     if "video_time" in st.session_state:
#         current_time = st.session_state["video_time"]
#         st.markdown(current_time)
#         displayed_lexicon = None
#         for lexicon in cultural_lexicons:
#             if lexicon["start"] <= current_time <= lexicon["end"]:
#                 displayed_lexicon = lexicon
#                 break
#         if displayed_lexicon:
#             lexicon_container.markdown(
#                 f"**{displayed_lexicon['term']}**: {displayed_lexicon['explanation']}"
#             )
#         else:
#             lexicon_container.empty()


# def main():
#     st.title("AI Subtitle Generator")
#     video_file_player()  # Include video player functionality


# main()
