from pytube import YouTube

web="https://www.youtube.com/watch?v=pvoa6468XcQ&pp=0gcJCUELAYcqIYzv"

YouTube(web).streams.first().download()
