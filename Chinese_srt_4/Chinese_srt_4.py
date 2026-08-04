import re
import sys
import os
from openai import OpenAI

# Initialize the client with DeepSeek's official Base URL and your API Key
client = OpenAI(
    api_key="deepseek-api-key",
    base_url="https://api.deepseek.com",
)

def translate_en_to_zh(text_to_translate):
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一位精通英语和简体中文、深谙东西方文化差异的专业高级翻译"
                        "请帮我将接下来的英文内容翻译成中文。"                       
                        "保持原文的段落结构、列表和标点符号层级。"
                        "直接输出翻译后的中文内容，不需要包含多余的客套话或解释。"
                    )
                },
                {
                    "role": "user",
                    "content": text_to_translate
                }
            ],
            # If you want to disable reasoning tokens to save costs/latency, change type to "disabled"
            extra_body={"thinking": {"type": "enabled"}}, 
            stream=False
        )
        
        # Extract and return the translated string
        return response.choices[0].message.content
        
    except Exception as e:
        return f"An error occurred: {str(e)}"


def split_srt_text(text):
    """将SRT内容拆分为块，每个块包含序号、时间轴和文本"""
    blocks = []
    lines = text.strip().split('\n')
    i = 0
    while i < len(lines):
        if lines[i].strip().isdigit():
            # 找到序号
            idx = lines[i].strip()
            i += 1
            if i < len(lines):
                # 时间轴
                time_line = lines[i].strip()
                i += 1
                # 文本行（可能有多行）
                text_lines = []
                while i < len(lines) and lines[i].strip() != '':
                    text_lines.append(lines[i].strip())
                    i += 1
                # 跳过空行
                blocks.append((idx, time_line, text_lines))
        else:
            i += 1
    return blocks

def format_srt_blocks(blocks):
    """将块格式化为SRT内容"""
    lines = []
    for idx, time_line, text_lines in blocks:
        lines.append(idx)
        lines.append(time_line)
        lines.extend(text_lines)
        lines.append('')
    return '\n'.join(lines)

def main():
    input_file = 'input.srt'
    output_file = 'output.srt'

    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析SRT
    blocks = split_srt_text(content)
    print(f"共发现 {len(blocks)} 条字幕")
          
    # 逐条翻译
    for i, (idx, time_line, text_lines) in enumerate(blocks):
        original_text = ' '.join(text_lines)
        if original_text.strip():
            try:
                translated = translate_en_to_zh(original_text)
                blocks[i] = (idx, time_line, [translated])
                print(f"[{idx}] {original_text[:50]}... -> {translated[:50]}...")
            except Exception as e:
                print(f"翻译失败 [{idx}]: {e}")
                blocks[i] = (idx, time_line, text_lines)
        else:
            blocks[i] = (idx, time_line, text_lines)

    # 写入输出文件
    output_content = format_srt_blocks(blocks)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f"\n翻译完成！输出文件: {output_file}")

if __name__ == '__main__':
    main()
