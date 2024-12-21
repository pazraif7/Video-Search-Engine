import os
import yt_dlp
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
import cv2
import json
import moondream as md 
from PIL import Image
import rapidfuzz
import matplotlib.pyplot as plt
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

def search_and_download():
    search = "super mario movie trailer"
    output_folder = os.getcwd()  
    ydl_opts = {
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'format': 'best',  
        'noplaylist': True  
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Searching for '{search}' and downloading the first result...")
            info = ydl.extract_info(f"ytsearch:{search}", download=True)  
            video_file = ydl.prepare_filename(info['entries'][0])  
        print(f"Video successfully downloaded: {video_file}")
        return video_file
    except Exception as e:
        print("Something went wrong while downloading the video.")
        print(f"Error: {e}")
        return None
    
def detect_scenes(video_file, output_folder="scenes", threshold=30.0):
    os.makedirs(output_folder, exist_ok=True)
    video_manager = VideoManager([video_file])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    try:
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list()
        print(f"Detected {len(scene_list)} scenes.")
        cap = cv2.VideoCapture(video_file)
        for i, (start, end) in enumerate(scene_list):
            frame_time = start.get_seconds()  
            cap.set(cv2.CAP_PROP_POS_MSEC, frame_time * 1000)  
            ret, frame = cap.read()
            if ret:
                output_image_path = os.path.join(output_folder, f"scene_{i+1}.jpg")
                cv2.imwrite(output_image_path, frame)  # Save the frame as an image
                print(f"Saved scene {i+1} image: {output_image_path}")
            else:
                print(f"Failed to capture frame for scene {i+1}.")
        cap.release()
        return len(scene_list)

    except Exception as e:
        print(f"An error occurred while detecting scenes: {e}")
        return 0

    finally:
        video_manager.release()

def caption_scenes(output_folder="scenes", json_file="scene_captions.json", model_path="moondream-2b-int8.mf"):
    if os.path.exists(json_file):
        print(f"Captions already exist in {json_file}. Skipping captioning.")
        return

    try:
        model = md.vl(model=model_path)
        print("Model initialized successfully.")
    except Exception as e:
        print(f"Error initializing model: {e}")
        return

    captions = {}

    for image_file in sorted(os.listdir(output_folder), key=lambda x: int(x.split('_')[1].split('.')[0])):
        if not image_file.endswith(('.jpg')): 
            continue

        try:
            scene_number = int(image_file.split('_')[1].split('.')[0])
        except ValueError:
            print(f"Skipping invalid file: {image_file}")
            continue

        image_path = os.path.join(output_folder, image_file)
        print(f"Generating caption for scene {scene_number}...")

        try:
            image = Image.open(image_path)
            encoded_image = model.encode_image(image)
            caption = model.caption(encoded_image)["caption"]
            captions[scene_number] = caption
            print(f"Scene {scene_number} caption: {caption}")
        except Exception as e:
            print(f"Error generating caption for scene {scene_number}: {e}")
            captions[scene_number] = "Error generating caption"
        with open(json_file, "w") as f:
            json.dump(captions, f, indent=4)

def search_captions_with_word(json_file, output_folder, threshold=80):
    with open(json_file, "r") as f:
        captions = json.load(f)    
    all_words = set()
    for caption in captions.values():
        all_words.update(caption.split()) 
    caption_completer = WordCompleter(list(all_words), ignore_case=True)
    session = PromptSession()
    query = session.prompt("Search the scene using a word: ", completer=caption_completer).strip().lower()
    results = rapidfuzz.process.extract(query, captions.values(), scorer=rapidfuzz.fuzz.partial_ratio, score_cutoff=threshold)
    found_scenes = [
        int(scene_number) for scene_number, caption in captions.items()
        if any(caption == result[0] and result[1] >= threshold for result in results)
    ]

    if found_scenes:
        print(f"Found scenes: {found_scenes}")
        scene_images = [
            os.path.join(output_folder, f"scene_{scene_number}.jpg") for scene_number in found_scenes
        ]
        create_collage(scene_images, output_file="collage.png")
        print("Collage created and saved as 'collage.png'.")    
    else:
        print("No scenes found matching the query.")


def create_collage(scene_images, output_file="collage.png"):
    images = [cv2.imread(image_path) for image_path in scene_images]
    num_images = len(images)
    if num_images == 0:
        print("No images to create a collage.")
        return

    grid_cols = min(num_images, 5)
    grid_rows = (num_images + grid_cols - 1) // grid_cols

    fig, axes = plt.subplots(grid_rows, grid_cols, figsize=(15, 5))
    axes = axes.flatten()

    for ax, image, scene_path in zip(axes, images, scene_images):
        ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        ax.axis("off")

    for ax in axes[num_images:]:
        ax.axis("off")

    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Collage saved to {output_file}.")
    plt.show()


def main():
    video_file = search_and_download()
    print("Starting scene detection...")
    detect_scenes(video_file)
    caption_scenes()
    search_captions_with_word(json_file="scene_captions.json", output_folder="scenes", threshold=80)
    
if __name__ == "__main__":
    main()

