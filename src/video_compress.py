import argparse
import os
import re
import shutil
import ffmpeg

class VideoCompressor:

    @staticmethod
    def ffprobe(target):
        result = ffmpeg.probe(target)
        streams = result["streams"]
        file_data = result["format"]
        video_streams = [s for s in streams if s["codec_type"] == "video"]
        audio_streams = [s for s in streams if s["codec_type"] == "audio"]
        video_stream = video_streams[0] # assume one stream for this purpose.
        width = video_stream["width"]
        height = video_stream["height"]
        frame_rate = video_stream["r_frame_rate"]
        file_size = int(file_data["size"])
        duration = float(file_data["duration"])
        units = ["B", "KB", "MB", "GB", "TB"]
        curr_unit = 0
        size_str = "{} {}".format(file_size, units[curr_unit])
        while file_size > 10000:
            curr_unit += 1
            file_size = file_size // 1000
            size_str = "{} {}".format(file_size, units[curr_unit])
            if curr_unit == 4:
                break
        ffprobe_string = "SIZE: {}; DURATION: {:.1f}; FRAME_RATE: {}; RESOLUTION: {}x{}".format(size_str, duration, frame_rate, width, height)
        return ffprobe_string

    @staticmethod
    def get_dimension(target):
        result = ffmpeg.probe(target)
        streams = result["streams"]
        video_streams = [s for s in streams if s["codec_type"] == "video"]
        video_stream = video_streams[0]
        return int(video_stream["width"]), int(video_stream["height"])

    def __init__(self, source=None, destination=None, process_dir=None, crf=23, preset="slower", scale=1):
        self.crf = crf
        self.preset = preset
        self.get_directories(source, destination, process_dir)
        self.targets = []
        self.scale = scale

    def get_directories(self, source, destination, process_dir):
        current_directory = os.getcwd()
        if source is None:
            self.source = current_directory
        else:
            self.source = source
        if destination is None:
            self.destination = self.source
        else:
            self.destination = destination
        if process_dir is None:
            self.process_dir = self.source
        else:
            self.process_dir = process_dir

    def get_targets(self):
        target_regex = re.compile(".mp4$", flags=re.I)
        all_files = os.listdir(self.source)
        video_files = [f for f in all_files if target_regex.search(f)]
        self.targets = [f for f in video_files if "compressed" not in f]
        print("will compress {} videos, they are {}".format(len(self.targets), self.targets))

    def run(self):
        self.get_targets()
        for target in self.targets:
            self.process_target(target)

    def process_target(self, target):
        # Step 1. move video to processing directory if needed.
        print("======== PROCESSING VIDEO: {} ========".format(target))
        target_path = os.path.join(self.source, target)
        print(VideoCompressor.ffprobe(target_path))
        process_path = os.path.join(self.process_dir, target)
        if target_path != process_path:
            print("copying {} to {} for processing".format(target_path, process_path))
            shutil.copy(target_path, process_path)
        # Step 2. compress the video in process directory.
        print("compressing video ...")
        try:
            tmp_processed_path = self.compress_video(process_path)
        except Exception as e:
            print("PROCESSING FAILED for {}".format(process_path))
            raise e
        if self.source != self.process_dir:
            os.remove(process_path) # Remove copied and processed material.
        # Step 3. move compressed video to destination directory
        if self.process_dir != self.destination:
            compressed_target_name = re.sub(".mp4$", "", target, flags=re.I) + "_compressed.mp4"
            end_path = os.path.join(self.destination, compressed_target_name)
            print("copying {} to destination {}".format(process_path, end_path))
            shutil.move(tmp_processed_path, end_path)

    def compress_video(self, video_path, **kwargs):
        arg_dict = {
            "crf": self.crf,
            "preset": self.preset,
            "loglevel": "quiet",
            "stats": None,
        }
        arg_dict.update(kwargs)
        if self.scale != 1:
            original_width, original_height = VideoCompressor.get_dimension(video_path)
            new_width = int(original_width * self.scale)
            new_height = int(original_height * self.scale)
            if new_width % 2 != 0:
                new_width += 1
            if new_height % 2 != 0:
                new_height += 1
            arg_dict["vf"] = "scale={}:{}".format(new_width, new_height)
        output_path = re.sub(".mp4$", "", video_path, flags=re.I) + "_compressed.mp4"
        work = ffmpeg.input(video_path)
        work = ffmpeg.output(work, output_path, **arg_dict)
        work.run()
        return output_path


SOURCE_HELP = """
[string] Source directory path, default to current directory, videos found in the directory will be compressed.
"""

DEST_HELP = """
[string] Destination directory path, default to source directory, compressed videos are stored here.
"""

PROC_HELP = """
[string] Process directory path, default to source directory, if it is specified and is not the source directory, video will be moved to this directory to be processed.
This is used when videos are stored in HDDs and ffmpeg would run into buffer issues, moving it to local SSD drive will speed up processing. All videos processed will be removed from the directory.
"""

CRF_HELP = """
[int] CRF Value, higher is more compression and less quality, saner values range between 17-28, with 17 being nearly lossless.
"""

PRESET_HELP = """
[string] The speed of which to generate the output video, slower makes video smaller without compromising on quality.
Options are [veryfast, faster, fast, medium, slow, slower, veryslow]
Default to slower
"""

SCALE_HELP = """
[float] Scale factor, 0.5 means the video will be scaled down to 50%% of the original width and height.
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--source', action='store', dest='source', default=None, help=SOURCE_HELP)
    parser.add_argument('-t', '--destination', action='store', dest='destination', default=None, help=DEST_HELP)
    parser.add_argument('-p', '--process-dir', action='store', dest='process', default=None, help=PROC_HELP)
    parser.add_argument('--crf', action='store', dest='crf', default=23, type=int, help=CRF_HELP)
    parser.add_argument('--preset', action='store', dest='preset', default="slower", help=PRESET_HELP)
    parser.add_argument('--scale', action='store', dest='scale', default=1.0, type=float, help=SCALE_HELP)
    args = parser.parse_args()
    compressor = VideoCompressor(args.source, args.destination, args.process, args.crf, args.preset, args.scale)
    compressor.run()


if __name__ == "__main__":
    main()
