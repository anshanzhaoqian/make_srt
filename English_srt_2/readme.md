# make_srt

调用faster-whisper实现给英语视频制造英语字幕文件

***

第三方库版本

faster-whisper是1.2.1

ffmpeg-python是0.2.0

***

input.mp4为视频名字

input.srt为字幕名字

***

我的电脑使用的是cuda13，但是faster-whisper使用的是cuda12，所以我激活了venv环境，使用了这么一条命令

`pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128`

这条命令会下载cu128版本的pytorch，在venv环境里可以运行cuda12环境，安装requirements.txt之前请先运行这条命令

我使用了faster-whisper库的small模型，它需要你的nvidia显卡至少有3gb显存才能运行，除了small模型，还有tiny，base，medium，large，等其它模型可以使用，第一次使用时需要联网下载模型

我的device用的cuda，compute_type用的float32，这些都可以修改

我的python版本是3.12

