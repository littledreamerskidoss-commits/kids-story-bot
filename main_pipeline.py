import os
import json
import random
import urllib.parse
import requests
import asyncio
import edge_tts
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.VideoClip import ImageClip

def generate_long_story():
    # Adapts based on automated self-updates if channel_memory exists
    theme_focus = "magical forest"
    if os.path.exists("channel_memory.json"):
        with open("channel_memory.json", "r") as f:
            memory = json.load(f)
            theme_focus = memory.get("preferred_theme", "magical forest")
    
    themes = [
        (f"The Little Bear's Journey in the {theme_focus.title()}", [
            ("Once upon a time, deep inside a cozy whispering forest, lived a little bear named Barnaby.", "3D Pixar style baby bear in a cozy green forest, golden hour lighting, storybook illustration"),
            ("Every single night, Barnaby would look up at the bright silver moon hanging high in the sky.", "3D Pixar style baby bear looking up at a glowing silver moon through tree branches"),
            ("He dreamed of climbing the tallest mountain to see if he could give the moon a friendly hug.", "3D Pixar style baby bear looking at a majestic tall mountain in the distance, adventurous"),
            ("With a small backpack filled with honey jars and berries, Barnaby began his big journey.", "3D Pixar style baby bear walking up a winding mountain trail with a tiny backpack"),
            ("Along the way, a wise old owl flew down and whispered words of encouragement into his furry ear.", "3D Pixar style baby bear talking to a friendly wise owl on a mossy branch, magical glow"),
            ("As they climbed higher, the stars glittered like tiny diamonds scattered across a velvet blanket.", "3D Pixar style baby bear standing on a high mountain peak looking at brilliant starry night sky"),
            ("Barnaby realized he didn't need to touch the moon to feel its magic; sharing the adventure was enough.", "3D Pixar style baby bear smiling happily under a giant glowing moon, heartwarming scene")
        ])
    ]
    title, scenes = random.choice(themes)
    return {"title": title, "scenes": [{"narration": n, "prompt": p} for n, p in scenes]}

def fetch_image(prompt_text, output_filename, is_short=False):
    width, height = (576, 1024) if is_short else (1024, 576)
    encoded_prompt = urllib.parse.quote(prompt_text)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={random.randint(1, 99999)}"
    response = requests.get(url, timeout=60)
    if response.status_code == 200:
        with open(output_filename, 'wb') as f:
            f.write(response.content)
        return output_filename
    else:
        raise Exception("Failed to fetch image")

async def create_voiceover(text, audio_filename):
    communicate = edge_tts.Communicate(text, "en-US-AnaNeural")
    await communicate.save(audio_filename)

def assemble_video(scenes, output_video_path, is_short=False):
    full_text = " ".join([s["narration"] for s in scenes])
    asyncio.run(create_voiceover(full_text, "narration.mp3"))
    audio = AudioFileClip("narration.mp3")
    duration_per_image = audio.duration / len(scenes)
    
    image_files = []
    for idx, scene in enumerate(scenes):
        img_file = f"scene_{idx}.png"
        fetch_image(scene["prompt"], img_file, is_short=is_short)
        image_files.append(img_file)
        
    clips = [ImageClip(img).set_duration(duration_per_image) for img in image_files]
    video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    video.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    is_short_run = os.environ.get("VIDEO_TYPE") == "short"
    story = generate_long_story()
    if is_short_run:
        assemble_video(story["scenes"][:3], "final_short.mp4", is_short=True)
    else:
        assemble_video(story["scenes"], "final_video.mp4", is_short=False)
