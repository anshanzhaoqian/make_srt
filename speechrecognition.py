from pydub import AudioSegment
from pydub.utils import make_chunks
import speech_recognition as sr
from pytube import YouTube
import subprocess
from googletrans import Translator
import os,os.path

#web为youtube地址
web='https://www.youtube.com/watch?v=9bldbQPBrFA'

translator = Translator()
YouTube(web).streams.get_by_itag(17).download(filename='videoplayback')

command = "ffmpeg -i videoplayback.3gpp -ab 160k -ac 2 -ar 44100 -vn y2mate.wav"
subprocess.call(command, shell=True)

myaudio = AudioSegment.from_file("y2mate.wav" , "wav") 
chunk_length_ms = 5000 
chunks = make_chunks(myaudio, chunk_length_ms)

for i, chunk in enumerate(chunks):
    chunk_name = "chunk{0}.wav".format(i)
    print("exporting", chunk_name)
    chunk.export(chunk_name, format="wav")

r=sr.Recognizer()
t=[]
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
			t.append(translator.translate(s, dest='zh-cn').text)
		except Exception:
			t.append('')
		print(i)

txt=''
k=1
for i in range(0,a):
	for j in range(0,11):
		txt=txt+str(k)+'\n'
		if j==0:
			txt=txt+'00:0'+str(i)+':00.000 --> 00:0'+str(i)+':05.000\n'+str(t[k])+'\n\n'
		elif j==1:
			txt=txt+'00:0'+str(i)+':05.000 --> 00:0'+str(i)+':10.000\n'+str(t[k])+'\n\n'
		else:
			txt=txt+'00:0'+str(i)+':'+str(j*5)+'.000 --> 00:0'+str(i)+':'+str(j*5+5)+'.000\n'+str(t[k])+'\n\n'
		k=k+1
	txt=txt+str(k)+'\n'
	txt=txt+'00:0'+str(i)+':'+str(j*5+5)+'.000 --> 00:0'+str(i+1)+':00.000\n'+str(t[k])+'\n\n'
	k=k+1

i=a
for j in range(0,b):
	txt=txt+str(k)+'\n'
	if j==0:
		txt=txt+'00:0'+str(i)+':00.000 --> 00:0'+str(i)+':05.000\n'+str(t[k])+'\n\n'
	elif j==1:
		txt=txt+'00:0'+str(i)+':05.000 --> 00:0'+str(i)+':10.000\n'+str(t[k])+'\n\n'
	else:
		txt=txt+'00:0'+str(i)+':'+str(j*5)+'.000 --> 00:0'+str(i)+':'+str(j*5+5)+'.000\n'+str(t[k])+'\n\n'
	k=k+1

f=open('videoplayback.srt','w',encoding='utf-8')
f.write(txt)
f.close()
 
for i in range(0,sum):
	filename='chunk'+str(i)+'.wav'
	if(os.path.exists(filename)):
		os.remove(filename) 