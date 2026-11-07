import os
import json
import random
import urllib.parse
import requests
import asyncio
import edge_tts
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

# --- 100-DAY MULTILINGUAL STORY LIBRARY DATABASE ---
THEMES = [
    ("Magical Forest", "in a glowing enchanted forest with sparkling fireflies and vibrant magic trees"),
    ("Underwater Kingdom", "underwater in a colorful coral reef with bright glowing jellyfish and friendly sea turtles"),
    ("Space Adventure", "in outer space surrounded by twinkling stars, colorful nebulae, and friendly small planets"),
    ("Dinosaur Valley", "in a lush green prehistoric valley with friendly baby dinosaurs and giant waterfalls"),
    ("Toy Town", "in a whimsical toy city with cobblestone streets made of candy and flying toy airplanes"),
    ("Cloud Kingdom", "high above the clouds on fluffy cotton candy castles with rainbows spanning the sky"),
    ("Safari Mystery", "in the sunny African savannah with friendly lion cubs, zebras, and playful monkeys"),
    ("Snowy Wonderland", "in a cozy snowy mountain village with friendly snowmen and dancing aurora borealis"),
    ("Secret Garden", "in a hidden garden with giant whispering flowers, colorful butterflies, and gentle streams"),
    ("Pirate Island", "on a sunny treasure island with palm trees, friendly parrots, and a sparkling blue lagoon")
]

CHARACTERS = [
    ("Barnaby the Bear", "3D Pixar style cute fluffy baby bear"),
    ("Leo the Lion Cub", "3D Pixar style friendly little lion cub with a tiny mane"),
    ("Pip the Penguin", "3D Pixar style adorable small penguin wearing a cozy scarf"),
    ("Maya the Bunny", "3D Pixar style fluffy white rabbit with long floppy ears"),
    ("Kiki the Kangaroo", "3D Pixar style cute baby kangaroo with a tiny pouch"),
    ("Finn the Dolphin", "3D Pixar style cheerful blue baby dolphin jumping through waters"),
    ("Oliver the Owl", "3D Pixar style wise small owl with big round shiny eyes"),
    ("Sammy the Squirrel", "3D Pixar style energetic squirrel holding a golden acorn"),
    ("Toby the Turtle", "3D Pixar style small gentle sea turtle with a patterned shell"),
    ("Bella the Butterfly", "3D Pixar style colorful butterfly with glowing wings")
]

def generate_story_for_day(day_num, content_type="video", lang="en"):
    """
    Generates a unique story for any given day (Day 1 to 100),
    tailored specifically for full videos (7 scenes) or YouTube Shorts (3 scenes).
    """
    theme_name, theme_desc = THEMES[(day_num - 1) % len(THEMES)]
    char_name, char_style = CHARACTERS[(day_num - 1) % len(CHARACTERS)]
    
    scene_count = 3 if content_type == "short" else 7
    
    templates = {
        "en": [
            (f"Once upon a time on Day {day_num}, {char_name} explored the {theme_name}.", f"{char_style} {theme_desc}, bright sunny lighting, 3D Pixar render, storybook illustration"),
            (f"{char_name} noticed a glowing golden key hidden under a bright shimmering leaf.", f"{char_style} looking closely at a glowing golden key, magical sparkling aura, 3D animation"),
            (f"With curiosity in heart, {char_name} followed a trail of floating colorful bubbles.", f"{char_style} chasing floating rainbow bubbles along a scenic trail, 3D Pixar style"),
            (f"Along the path, a friendly companion joined the quest with a happy smile.", f"{char_style} meeting a cute small animal friend, heartwarming scene, vivid colors, 3D render"),
            (f"Together, they climbed a high hill to look at the magnificent vista ahead.", f"{char_style} standing on top of a hill looking at a majestic landscape, cinematic lighting"),
            (f"They unlocked a magical treasure box full of colorful twinkling stars.", f"{char_style} opening a glowing chest filled with magic stars, awe and wonder, 3D Pixar style"),
            (f"Satisfied and happy, {char_name} smiled under the silver moon, ready for the next adventure.", f"{char_style} sleeping cozy under a sparkling starry night sky, cute fairytale scene")
        ],
        "hi": [
            (f"एक समय की बात है, {char_name} ने {theme_name} की एक अद्भुत यात्रा शुरू की।", f"{char_style} {theme_desc}, bright sunny lighting, 3D Pixar render, storybook illustration"),
            (f"{char_name} को एक चमकते हुए पत्ते के नीचे एक जादुई सोने की चाबी मिली।", f"{char_style} looking closely at a glowing golden key, magical sparkling aura, 3D animation"),
            (f"उत्सुकता के साथ, वह रंग-बिरंगे बुलबुलों के पीछे चलने लगा।", f"{char_style} chasing floating rainbow bubbles along a scenic trail, 3D Pixar style"),
            (f"रास्ते में एक प्यारा दोस्त मिला और दोनों साथ मिलकर आगे बढ़े।", f"{char_style} meeting a cute small animal friend, heartwarming scene, vivid colors, 3D render"),
            (f"वे दोनों एक ऊंचे पहाड़ पर चढ़े और सामने का सुंदर नजारा देखा।", f"{char_style} standing on top of a hill looking at a majestic landscape, cinematic lighting"),
            (f"उन्होंने जादुई बक्सा खोला जिसमें से ढेरों चमकते तारे निकले।", f"{char_style} opening a glowing chest filled with magic stars, awe and wonder, 3D Pixar style"),
            (f"खुशी-खुशी {char_name} चाँद की रोशनी में सो गया और नया दिन याद किया।", f"{char_style} sleeping cozy under a sparkling starry night sky, cute fairytale scene")
        ],
        "ta": [
            (f"ஒரு அழகான நாளில், {char_name} {theme_name}-ற்குள் தனது புதிய பயணத்தைத் தொடங்கியது.", f"{char_style} {theme_desc}, bright sunny lighting, 3D Pixar render, storybook illustration"),
            (f"{char_name} ஒரு மின்னும் இலையின் அடியில் தங்கச் சாவியைக் கண்டது.", f"{char_style} looking closely at a glowing golden key, magical sparkling aura, 3D animation"),
            (f"ஆர்வதோடு, அது பறக்கும் வண்ணப் குமிழிகளைப் பின்தொடர்ந்து சென்றது.", f"{char_style} chasing floating rainbow bubbles along a scenic trail, 3D Pixar style"),
            (f"வழியில் ஒரு அழகான நண்பன் இணைந்து கொள்ள, பயணம் இனிமையாக மாறியது.", f"{char_style} meeting a cute small animal friend, heartwarming scene, vivid colors, 3D render"),
            (f"இருவரும் ஒரு உயர்ந்த மலை மீது ஏறி அழகான காட்சியைப் பார்த்தனர்.", f"{char_style} standing on top of a hill looking at a majestic landscape, cinematic lighting"),
            (f"அவர்கள் ஒரு மந்திர பெட்டியைத் திறந்தனர், அதில் நட்சத்திரங்கள் ஜொலித்தன.", f"{char_style} opening a glowing chest filled with magic stars, awe and wonder, 3D Pixar style"),
            (f"மகிழ்ச்சியுடன் {char_name} நிலவின் வெளிச்சத்தில் தூங்கி அமைதி அடைந்தது.", f"{char_style} sleeping cozy under a sparkling starry night sky, cute fairytale scene")
        ]
    }
    
    selected_scenes = templates.get(lang, templates["en"])[:scene_count]
    return {
        "title": f"Day {day_num} - {char_name} in {theme_name}",
        "scenes": [{"narration": n, "prompt": p} for n, p in selected_scenes]
    }

def fetch_image(prompt_text, output_filename, is_short=False):
    width, height = (576, 1024) if is_short else (1024, 576)
    encoded_prompt = urllib.parse.quote(prompt_text)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={random.randint(1, 99999)}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            return output_filename
    except Exception as e:
        print(f"Image API warning: {e}. Using fallback image.")
        
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (width, height), color=(30, 100, 150))
    d = ImageDraw.Draw(img)
    d.text((40, height // 2), f"Scene: {output_filename}", fill=(255, 255, 255))
    img.save(output_filename)
    return output_filename

async def create_voiceover(text, audio_filename, lang="en"):
    voice_map = {
        "en": "en-US-AriaNeural",
        "hi": "hi-IN-SwaraNeural",
        "ta": "ta-IN-PallaviNeural"
    }
    voice = voice_map.get(lang, "en-US-AriaNeural")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(audio_filename)

def assemble_content(day_num, content_index, content_type="video", lang="en"):
    story = generate_story_for_day(day_num, content_type=content_type, lang=lang)
    is_short = (content_type == "short")
    output_video_path = f"day_{day_num}_{content_type}_{content_index}_{lang}.mp4"
    audio_filename = f"narration_day_{day_num}_{content_index}.mp3"
    
    print(f"--- Generating Day {day_num} | {content_type.upper()} #{content_index} [{lang.upper()}] ---")
    
    full_text = " ".join([s["narration"] for s in story["scenes"]])
    asyncio.run(create_voiceover(full_text, audio_filename, lang=lang))
    
    audio = AudioFileClip(audio_filename)
    duration_per_image = audio.duration / len(story["scenes"])
    
    image_files = []
    for idx, scene in enumerate(story["scenes"]):
        img_file = f"day{day_num}_{content_type}_{content_index}_scene{idx}.png"
        fetch_image(scene["prompt"], img_file, is_short=is_short)
        image_files.append(img_file)
        
    clips = [ImageClip(img).with_duration(duration_per_image) for img in image_files]
    video = concatenate_videoclips(clips, method="compose").with_audio(audio)
    video.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac")
    print(f"SUCCESS: Created {output_video_path}")

if __name__ == "__main__":
    day = int(os.environ.get("DAY_NUMBER", 1))
    c_type = os.environ.get("CONTENT_TYPE", "short")
    c_idx = int(os.environ.get("CONTENT_INDEX", 1))
    lang = os.environ.get("STORY_LANG", "en").lower()
    
    assemble_content(day_num=day, content_index=c_idx, content_type=c_type, lang=lang)
