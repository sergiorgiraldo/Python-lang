from threading import Thread  # Encoder is a thread
import subprocess
from datetime import datetime
import os
import glob
import fnmatch
import shutil
from notify import notify  # Shows notifications/alerts
from typing import List

not_found_msg = """
The ffmpeg command was not found;
ffmpeg is used by this script to make a video file from a set of pngs.
It is typically not installed by default distros , but it is widely available.
On macOS, try running `brew install ffmpeg`.
"""


class Encoder(Thread):
    """Create a video file from images"""

    def __init__(self, input_dir: str, output_dir: str) -> None:
        # Initialize the thread
        Thread.__init__(self)

        # Set config options
        self.input: str = f"{input_dir}/%d.png"
        timestamp: str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.output: str = f"{output_dir}/timelapse-{timestamp}.mp4"

        notify("Encode", "Encoder started")

    def join(self, timeout=None) -> None:
        """ Hard shutdown """
        try:
            Thread.join(self)
        except Exception as e:
            notify("Timelapse error", "thread join:An unexpected error occurred:" + str(e)) # handle the error

    def run(self) -> None:
        """
        Now that we have screenshots of the user's desktop, we will stitch them
        together using `ffmpeg` to create a movie.  Each image will become
        a single frame in the movie.
        """
        command: List[str] = ["ffmpeg", "-y",
                              "-framerate", "2",
                              "-i", self.input,
                              "-c:v", "libx264",
                              "-preset", "slow",
                              "-profile:v", "high",
                              "-level:v", "4.0",
                              "-pix_fmt", "yuv420p",
                              "-crf", "18",
                              self.output]
        try:
            notify("Timelapse", f"Creating timelapse. This might take a while")
            try:
                completed = subprocess.run(
                    command, capture_output=True, check=True)
            except subprocess.CalledProcessError as e:
                notify("Timelapse: ffmpeg not found.", e.stderr.decode('utf-8'))
            else:
                notify("Timelapse", f"Movie saved to `{self.output}`")
        except Exception as e:
            notify("Timelapse Error", "encoderRun:Error:" + str(e))