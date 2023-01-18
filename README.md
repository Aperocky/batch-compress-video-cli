## Batch Video Compress cli

`pip install batch-compress-video-cli`

This is a cli tool that batch compress all videos in a folder and process in/move to a separate folder if needed. Save the need to craft `ffmpeg` commands, perfect for compressing and storing unused action camera/drone videos.

## Usage

--- 

```
batch_compress_video
```

this will compress all `.mp4` file in the current directory that does not have `compressed` in its name. It does that with default values of `crf=23, preset=slower`.

```
batch_compress_video -d -f $SOURCE_DIR -t $DEST_DIR -p $PROC_DIR
```

this will find all `.mp4` file in `$SOURCE_DIR`, individually move them to `$PROC_DIR`, compress it there using the default values, and then move them to `$DEST_DIR`. This is really helpful when the source and destination directories are HDD storage and conflict with read/write operation of `ffmpeg`. The `-d` flag signifies the original videos are to be deleted.

```
batch_compress_video --crf 25 --scale 0.5 --preset fast
```

This will compress video with a quality of `crf=25`, reduce the width and height to 50%, and use `fast` preset.

A full example (output when it is running):

```
~/bellard/processing$ batch_compress_video --source "/Volumes/SSDS1/footage/gopro/PADDLE_2022_12" --process-dir "." --destination "/Volumes/SSDS1/footage/gopro/PADDLE_2022_12" --crf 25 --preset "medium" --scale 0.4
will compress 18 videos, they are ['GX010142.MP4', 'GX010156.MP4', 'GX010157.MP4', 'GX010155.MP4', 'GX010141.MP4', 'GX010140.MP4', 'GX010154.MP4', 'GX010150.MP4', 'GX010144.MP4', 'GX010145.MP4', 'GX010147.MP4', 'GX010153.MP4', 'GX010152.MP4', 'GX010146.MP4', 'GX010148.MP4', 'GX010149.MP4', 'GX010159.MP4', 'GX010158.MP4']
======== PROCESSING VIDEO: GX010142.MP4 ========
SIZE: 267 MB; DURATION: 48.0; FRAME_RATE: 30000/1001; RESOLUTION: 1920x1080
copying /Volumes/SSDS1/footage/gopro/PADDLE_2022_12/GX010142.MP4 to ./GX010142.MP4 for processing
compressing video ...
frame= 1438 fps=105 q=-1.0 Lsize=    4974kB time=00:00:47.95 bitrate= 849.6kbits/s speed=3.49x
copying ./GX010142_compressed.mp4 to destination /Volumes/SSDS1/footage/gopro/PADDLE_2022_12/GX010142_compressed.mp4
Video compressed to /Volumes/SSDS1/footage/gopro/PADDLE_2022_12/GX010142_compressed.mp4
SIZE: 5093 KB; DURATION: 48.0; FRAME_RATE: 30000/1001; RESOLUTION: 768x432

======== PROCESSING VIDEO: GX010156.MP4 ========
SIZE: 351 MB; DURATION: 62.9; FRAME_RATE: 30000/1001; RESOLUTION: 1920x1080
copying /Volumes/SSDS1/footage/gopro/PADDLE_2022_12/GX010156.MP4 to ./GX010156.MP4 for processing
compressing video ...
frame= 1728 fps=101 q=31.0 size=    4096kB time=00:00:57.87 bitrate= 579.8kbits/s speed=3.37x
```

The progress bar is displayed for each video as it is converting so you'd know where the conversion is. After it is converted, the newly compressed video stats will be displayed. In this case, extreme compression (lossy, scaled down) resulted in video that are less than 2% the size of the original.

Perfect for keeping cruft videos! Maybe in 2040 GANs, powerful graphic cards and TB sized storage are cheap and plentiful, and we restore our videos to its full (and even some extra) glory.

### Rationale

---

After racking up 100s of GBs of videos in a couple hours of GoPro and DJI videos, I realized that:

1. I don't have enough space to store all of them.
2. The videos are very poorly compressed, if at all. Compressing at a level without reducing quality will yield significantly smaller video. Compressing at higher level will yield very small video compared to original..
3. I don't want to individually use FFMPEG cli commands to compress all of those videos, I want a simple command that can compress all of them.
4. ffmpeg often break down on HDDs due to disk constraints.

This is a tool written to solve all of these problems.


### Developing

---

`pytest` and `coverage` are used for testing. After cloning, you can invoke them with `make test`.

CLI can be updated with `make install`
