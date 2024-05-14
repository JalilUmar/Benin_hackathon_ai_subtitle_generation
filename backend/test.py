import os

current_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(current_dir, "../frontend/public/subtitle.vtt")

with open(file_path, "w", encoding="utf-8") as f:
    f.write("Hello babar")
