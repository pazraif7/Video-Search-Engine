import os
import yt_dlp
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
import cv2

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


def main():
    video_file = search_and_download()
    print("Starting scene detection...")
    detect_scenes(video_file)

    
if __name__ == "__main__":
    main()

