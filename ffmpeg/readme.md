# make_srt

用python调用ffmpeg实现英语视频和中文配音的拼接

***

input.mp4为英语视频

output.mp3为中文配音

output.mp4为输出文件

***

运行环境为win11

本脚本的功能相当于下面的命令

`ffmpeg -i input.mp4 -i output.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4`

***

ffmpeg的文件位于C:\translate\ffmpeg.exe


