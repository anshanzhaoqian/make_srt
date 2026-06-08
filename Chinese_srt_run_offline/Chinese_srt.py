import re
import ollama

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

def translate_text(text):
    prompt = f"将以下英语翻译为简体中文，只输出翻译结果，不要额外解释：\n\n{text}"
    
    response = ollama.chat(
        model='gemma3:1b',
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )
    
    translated = response['message']['content'].strip()
    return translated

def main():
    subtitles = parse_srt('input.srt')
    print(f"共找到 {len(subtitles)} 条字幕")
    
    output_lines = []
    
    for i, sub in enumerate(subtitles):
        print(f"[{i+1}/{len(subtitles)}] 翻译中: {sub['text'][:60]}...")
        translated = translate_text(sub['text'])
        
        output_lines.append(str(sub['index']))
        output_lines.append(sub['timecode'])
        output_lines.append(translated)
        output_lines.append('')
    
    with open('output.srt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"翻译完成！结果已保存到 output.srt")

if __name__ == '__main__':
    main()
