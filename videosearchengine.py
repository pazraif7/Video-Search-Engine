import os
import yt_dlp

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
    
    
def main():
    search_and_download()
    

if __name__ == "__main__":
    main()

