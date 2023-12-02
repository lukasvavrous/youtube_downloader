import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from pytube import YouTube
from moviepy.editor import *
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os
import re
import threading

def is_valid_youtube_url(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    youtube_pattern = re.compile(youtube_regex)
    return re.match(youtube_pattern, url) is not None

def fetch_video_info():
    video_url = url_entry.get()

    if not is_valid_youtube_url(video_url):
        messagebox.showerror("Error", "Invalid YouTube URL")
        return

    try:
        yt = YouTube(video_url)

        # Display thumbnail
        response = requests.get(yt.thumbnail_url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((150, 90), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        thumbnail_label.config(image=photo)
        thumbnail_label.image = photo

        # Update format options
        stream_formats = {stream.mime_type.split('/')[1] for stream in yt.streams}
        format_combobox['values'] = list(stream_formats)
        format_combobox.current(0)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def fetch_video_info_async():
    threading.Thread(target=fetch_video_info, daemon=True).start()

def download_video():
    video_url = url_entry.get()
    start_time = int(start_entry.get())
    end_time = int(end_entry.get())
    output_format = format_combobox.get()

    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(file_extension='mp4').first()
        stream.download(filename='downloaded_video.mp4')

        with VideoFileClip('downloaded_video.mp4') as video:
            trimmed_video = video.subclip(start_time, end_time)
            
            if output_format == 'mp4':
                trimmed_video.write_videofile('trimmed_video.mp4')
            elif output_format == 'mp3':
                trimmed_video.audio.write_audiofile('trimmed_audio.mp3')

        messagebox.showinfo("Success", f"Video saved as trimmed_video.{output_format}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

    finally:
        try:
            os.remove('downloaded_video.mp4')
        except Exception as e:
            print("Error deleting original file: ", e)

def on_url_entry_change(event=None):
    video_url = url_entry.get()
    if is_valid_youtube_url(video_url):
        fetch_video_info_async()

root = tk.Tk()
root.title("YouTube Video Downloader and Trimmer")

tk.Label(root, text="Video URL:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.bind("<KeyRelease>", on_url_entry_change)
url_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Start Time (in seconds):").grid(row=1, column=0, padx=10, pady=10)
start_entry = tk.Entry(root, width=20)
start_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="End Time (in seconds):").grid(row=2, column=0, padx=10, pady=10)
end_entry = tk.Entry(root, width=20)
end_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text="Output Format:").grid(row=3, column=0, padx=10, pady=10)
format_combobox = ttk.Combobox(root, values=["mp4", "mp3"])
format_combobox.grid(row=3, column=1, padx=10, pady=10)
format_combobox.current(0)

download_button = tk.Button(root, text="Download and Trim", command=download_video)
download_button.grid(row=4, column=0, columnspan=2, pady=20)

thumbnail_label = tk.Label(root)
thumbnail_label.grid(row=1, column=2, rowspan=3, padx=10, pady=10)

root.mainloop()
