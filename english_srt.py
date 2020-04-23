from pydub import AudioSegment
from pydub.utils import make_chunks
import speech_recognition as sr
from pytube import YouTube
import subprocess
import os,os.path
import time
import datetime

chunk_length_ms = 3000 
time2 = int(chunk_length_ms / 1000)
time3 = 2

def strt3(t3):
	b=[]
	l = len(t3)
	a=25
	for n in range(l):
		if n % a == 0:
			b.append(t3[n:n+a])

	return '\n'.join(b)

def timestr(t):
	t1=t*time2
	t2=(t+1)*time2
	str1=str(datetime.timedelta(seconds=t1))
	str2=str(datetime.timedelta(seconds=t2))
	str3='0'+str1+'.000 --> 0'+str2+'.000'
	return str3

#web为youtube地址
web='https://www.youtube.com/watch?v=eJCqdl8sNKo'

YouTube(web).streams.get_by_itag(22).download(filename='videoplayback')

command = "ffmpeg -i videoplayback.mp4 -ab 160k -ac 2 -ar 44100 -vn y2mate.wav"
subprocess.call(command, shell=True)

myaudio = AudioSegment.from_file("y2mate.wav" , "wav") 
chunks = make_chunks(myaudio, chunk_length_ms)

for i, chunk in enumerate(chunks):
    chunk_name = "chunk{0}.wav".format(i)
    print("exporting", chunk_name)
    chunk.export(chunk_name, format="wav")

r=sr.Recognizer()
t=[]
t3=[]
sum=i+1
a=int(sum/12)
b=sum%12
c=a*12
t.append('hello')
for i in range(0,sum):
	harvard=sr.AudioFile('chunk'+str(i)+'.wav')
	with harvard as source:
		audio=r.record(source)
		try:
			s=r.recognize_google(audio)
			t.append(s)
		except Exception:
			t.append('')
		print(i)
		time.sleep(time3)



txt=''

for i, val in enumerate(t):
	if i!=0:
		j=i-1
		txt=txt+str(i)+'\n'+timestr(j)+'\n'+val+'\n\n'
		print(i)

f=open('videoplayback.srt','w',encoding='utf-8')
f.write(txt)
f.close()

for i in range(0,sum):
	filename='chunk'+str(i)+'.wav'
	if(os.path.exists(filename)):
		os.remove(filename) 