This project allows users to search for specific moments in a video by analyzing scenes and generating captions. 
It downloads a video from YouTube, detects scene changes, extracts key frames, and generates descriptions using an AI-powered captioning model. 
Users can then search for specific words in the captions to find relevant scenes, and the system creates a collage of matching frames.
The system works by first downloading a video using yt-dlp, then detecting scenes with the SceneDetect library. 
It generates captions using Moondream AI and stores them in a JSON file. 
Users can search captions using rapidfuzz, and if matches are found, a collage of the relevant scenes is created. 
The project is built with Python and uses OpenCV, SceneDetect, yt-dlp, Moondream, RapidFuzz, Matplotlib, and Prompt Toolkit.
