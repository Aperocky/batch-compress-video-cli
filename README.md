## Batch Video Compress cli

This is a cli tool that batch compress all videos in a folder and process in/move to a separate folder if needed.

After racking up 100s of GBs of videos in a couple hours of GoPro and DJI videos, I realized that:

1. I don't have enough space to store all of them.
2. The videos are very poorly compressed, if at all. Compressing at a level without reducing quality will yield significantly smaller video
3. I don't want to individually use FFMPEG cli commands to compress all of those videos, I want a simple command that can compress all of them.
4. ffmpeg often break down on HDDs due to disk constraints.

So I wrote a tool to solve all of those problems.
