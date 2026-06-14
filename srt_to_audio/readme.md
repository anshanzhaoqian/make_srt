# make_srt

离线运行脚本实现把中文字幕文件转换成中文音频文件mp3

***

第三方库版本

anyio==4.13.0

edge-tts==7.2.8

pydub==0.25.1

pysrt==1.1.2

***

output.srt为中文字幕文件

output.mp3为中文音频文件mp3

***

运行环境为win11

可以下载ffmpeg，当英语视频文件为input.mp4时，执行下列命令

ffmpeg -i input.mp4 -i output.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4

可以用output.mp3替代input.mp4里的原英语音轨，实现把input.mp4变成中文视频文件output.mp4


