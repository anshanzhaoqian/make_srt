import whisper

print("Loading model 'base'...")
model = whisper.load_model('base')

print("Transcribing input.mp4 with fp32...")
result = model.transcribe('input.mp4', fp16=False)

print(f"Transcription complete. {len(result['segments'])} segments found.")

srt_lines = []
for i, seg in enumerate(result['segments'], 1):
    start = seg['start']
    end = seg['end']
    text = seg['text'].strip()

    start_h = int(start // 3600)
    start_m = int((start % 3600) // 60)
    start_s = int(start % 60)
    start_ms = int((start - int(start)) * 1000)

    end_h = int(end // 3600)
    end_m = int((end % 3600) // 60)
    end_s = int(end % 60)
    end_ms = int((end - int(end)) * 1000)

    start_str = f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d}"
    end_str = f"{end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}"

    srt_lines.append(f"{i}\n{start_str} --> {end_str}\n{text}\n")

output = '\n'.join(srt_lines)
with open('input.srt', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"Saved {len(srt_lines)} subtitle entries to input.srt")
