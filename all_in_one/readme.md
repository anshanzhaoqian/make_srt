# make_srt

三合一脚本，整合English_srt_2,Chinese_srt_3和srt_to_audio,实现从英语视频文件mp4到中文音频文件mp3的转换

***

第三方库版本

edge-tts是7.2.8

pydub是0.25.1

pysrt是1.1.2

faster-whisper是1.2.1

ffmpeg-python是0.2.0

argostranslate是1.11.0

***

input.mp4为英语视频文件

input.srt为英语字幕文件

output.srt为中文字幕文件

output.mp3为中文音频文件

***

我的电脑使用的是cuda13，但是faster-whisper和argostranslate使用的是cuda12，所以我激活了venv环境，使用了这么一条命令

`pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128`

这条命令会下载cu128版本的pytorch，在venv环境里可以运行cuda12环境，安装requirements.txt之前请先运行这条命令

我的python版本是3.12

本脚本运行时需联网访问github.com

运行环境为win11

可以下载ffmpeg，当英语视频文件为input.mp4时，执行下列命令

`ffmpeg -i input.mp4 -i output.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4`

可以用output.mp3替代input.mp4里的原英语音轨，实现把input.mp4变成中文视频文件output.mp4
