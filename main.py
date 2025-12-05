import os
import subprocess
import re
from pytubefix import YouTube, Playlist

# Configuration
DOWNLOAD_FOLDER = "music_downloads"


def convert_mp4_to_m4a(input_file, output_file, video_data):
    try:
        metadata_args = []
        for key, value in video_data.items():
            metadata_args.extend(["-metadata", f"{key}={value}"])

        subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_file,
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                *metadata_args,
                "-y",
                output_file,
            ],
            check=True,
            capture_output=True,
        )
        print("Conversion completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
    except Exception as e:
        print(f"Error converting file: {str(e)}")


def download_and_convert(video_url, folder_path):
    try:
        video = YouTube(video_url)
        stream = video.streams.filter(only_audio=True).order_by("abr").desc().first()

        if not stream:
            print(f"No audio stream available for: {video.title}")
            return

        title = re.sub(r"[^\w\-_\. ]", "_", video.title)
        f_name = f"{title}"

        if os.path.exists(os.path.join(folder_path, f_name + ".m4a")):
            print(f"File '{f_name}.m4a' already exists. Skipping.")
            return

        print(f"Downloading: {video.title}")
        video_stream = stream.download(
            output_path=folder_path, filename=f_name + ".mp4"
        )
        print(f"{video.title} - Download completed!")

        video_data = {
            "title": video.title,
            "artist": video.author,
        }

        m4a_output_path = os.path.join(folder_path, f_name + ".m4a")
        convert_mp4_to_m4a(video_stream, m4a_output_path, video_data)

        try:
            os.remove(video_stream)
            print("Temporary file deleted!")
        except Exception as e:
            print(f"Error deleting temporary file: {str(e)}")

    except Exception as e:
        print(f"Error processing video '{video_url}': {str(e)}")


if __name__ == "__main__":
    playlist_url = input("Enter playlist URL: ")

    try:
        playlist = Playlist(playlist_url)

        # Create main download folder if it doesn't exist
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)

        # Create playlist subfolder
        playlist_name = re.sub(r"[^\w\-_\. ]", "_", playlist.title)
        folder_path = os.path.join(DOWNLOAD_FOLDER, playlist_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        print(f"\nPlaylist: {playlist.title}")
        print(f"Total videos: {len(playlist.video_urls)}")
        print(f"Saving to: {folder_path}\n")

        for idx, video_url in enumerate(playlist.video_urls, 1):
            print(f"\n[{idx}/{len(playlist.video_urls)}]")
            download_and_convert(video_url, folder_path)

        print(f"\n✓ All downloads completed! Check folder: {folder_path}")

    except Exception as e:
        print(f"Error loading playlist: {str(e)}")
