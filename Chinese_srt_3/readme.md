# make_srt

使用argostranslate实现把英语字幕文件srt翻译成中文字幕文件srt

***

第三方库版本

argostranslate是1.11.0

***

input.srt为英语字幕文件

output.srt为中文字幕文件

***

我的电脑使用的是cuda13，但是argostranslate使用的是cuda12，所以我激活了venv环境，使用了这么一条命令

`pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128`

这条命令会下载cu128版本的pytorch，在venv环境里可以运行cuda12环境，安装requirements.txt之前请先运行这条命令

我的python版本是3.12

本脚本使用的时候需要联网


