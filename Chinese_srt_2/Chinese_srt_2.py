import re
from googletrans import Translator
import time
import asyncio

def parse_srt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    blocks = re.split(r'\n\n+', content)
    subtitles = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 2:
            continue
        
        idx = lines[0].strip()
        timecode = lines[1].strip()
        text = '\n'.join(lines[2:]).strip()
        
        subtitles.append({
            'index': idx,
            'timecode': timecode,
            'text': text
        })
    
    return subtitles

async def translate_text(apple2):
    async with Translator() as translator:
        result = await translator.translate(apple2, dest='zh-CN', src='en')
    return result

async def main():
    subtitles = parse_srt('input.srt')
    print(f"共找到 {len(subtitles)} 条字幕")
    
    output_lines = []
    
    for i, sub in enumerate(subtitles):
        print(f"[{i+1}/{len(subtitles)}] 翻译中: {sub['text'][:60]}...")
        time.sleep(10)
        translated = await translate_text(sub['text'])
        
        output_lines.append(str(sub['index']))
        output_lines.append(sub['timecode'])
        output_lines.append(translated.text)
        output_lines.append('')
    
    with open('output.srt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"翻译完成！结果已保存到 output.srt")

if __name__ == '__main__':
    asyncio.run(main())
