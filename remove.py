import os,os.path

if(os.path.exists('videoplayback.mp4')):
	os.remove('videoplayback.mp4')
if(os.path.exists('videoplayback.srt')):
	os.remove('videoplayback.srt')
if(os.path.exists('y2mate.wav')):
	os.remove('y2mate.wav')