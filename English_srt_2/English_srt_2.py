import sys
import os
from faster_whisper import WhisperModel

def format_timestamp(seconds):
    """将秒数转换为 SRT 时间戳格式 HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def main():
    model = WhisperModel("small", device="cuda", compute_type="float32")
    
    segments, info = model.transcribe("input.mp4", language="en", beam_size=5)
    
    with open("input.srt", "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            start_ts = format_timestamp(segment.start)
            end_ts = format_timestamp(segment.end)
            f.write(f"{i}\n")
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{segment.text.strip()}\n\n")
    
    print(f"转录完成，共 {i} 条字幕，已保存到 input.srt")

if __name__ == "__main__":
    main()
