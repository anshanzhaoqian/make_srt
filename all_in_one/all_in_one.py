import sys
import os
from faster_whisper import WhisperModel
import argostranslate.translate 
import argostranslate.package 
import re
import asyncio
import edge_tts
import pysrt
from pydub import AudioSegment
import shutil
import time

# 配置
VOICE = "zh-CN-XiaoxiaoNeural"  # 中文女声

def format_timestamp(seconds):
    """将秒数转换为 SRT 时间戳格式 HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def main_one():
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

def setup_en_to_zh():
    """下載並安裝『英文 -> 中文』的翻譯模型"""
    print("正在下載/更新翻譯模型索引...")
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    
    # 尋找從 en 到 zh 的模型
    package_to_install = next(
        (pkg for pkg in available_packages if pkg.from_code == "en" and pkg.to_code == "zh"),
        None
    )
    
    if package_to_install:
        print(f"發現可用模型: {package_to_install.name}，開始下載安裝...")
        download_path = package_to_install.download()
        argostranslate.package.install_from_path(download_path)
        print("模型安裝成功！\n")
    else:
        print("未找到 en 到 zh 的翻譯模型，請檢查網路連線。")

def translate_en_to_zh(text):
    """執行英文轉中文翻譯"""
    installed_languages = argostranslate.translate.get_installed_languages()
    
    # 提取本機已安裝的語言物件
    from_lang = next((lang for lang in installed_languages if lang.code == "en"), None)
    to_lang = next((lang for lang in installed_languages if lang.code == "zh"), None)
    
    # 如果本地找不到模型，自動觸發下載
    if not from_lang or not to_lang:
        setup_en_to_zh()
        installed_languages = argostranslate.translate.get_installed_languages()
        from_lang = next((lang for lang in installed_languages if lang.code == "en"), None)
        to_lang = next((lang for lang in installed_languages if lang.code == "zh"), None)
    
    # 執行翻譯
    translation = from_lang.get_translation(to_lang)
    return translation.translate(text)

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

def main_two():
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

def srt_time_to_ms(time_obj):
    """将 pysrt 时间对象转换为毫秒"""
    return (time_obj.hours * 3600 + time_obj.minutes * 60 +
            time_obj.seconds) * 1000 + time_obj.milliseconds


def parse_srt(filepath):
    """
    解析 SRT 文件。
    返回列表，每个元素为 (text, start_ms, end_ms)
    """
    subs = pysrt.open(filepath, encoding='utf-8')
    segments = []
    for sub in subs:
        text = sub.text.replace('\n', ' ').strip()
        start_ms = srt_time_to_ms(sub.start)
        end_ms = srt_time_to_ms(sub.end)
        if text:
            segments.append((text, start_ms, end_ms))
    return segments


def clean_text(text):
    """清理文本中的 HTML 标签"""
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


async def text_to_audio(text, output_path):
    """使用 edge-tts 将文本转为音频文件"""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)


async def main():
    
    main_one()
    
    main_two()
    
    # 配置
    SRT_FILE = "output.srt"
    OUTPUT_FILE = "output.mp3"
    TEMP_DIR = "temp_audio"
    
    # 创建临时目录
    os.makedirs(TEMP_DIR, exist_ok=True)

    # 1. 解析 SRT 文件
    print("正在解析 SRT 文件...")
    segments = parse_srt(SRT_FILE)
    print(f"共解析到 {len(segments)} 条字幕")

    # 2. 逐条生成语音片段
    print("正在生成语音片段...")
    audio_segments = []  # 每个元素: (audio_segment, start_ms, end_ms)
    total = len(segments)

    for i, (text, start_ms, end_ms) in enumerate(segments):
        cleaned_text = clean_text(text)
        if not cleaned_text:
            print(f"  [{i+1}/{total}] 跳过空文本")
            continue

        temp_file = os.path.join(TEMP_DIR, f"seg_{i:04d}.mp3")
        print(f"  [{i+1}/{total}] 合成: {cleaned_text[:40]}...")

        try:
            await text_to_audio(cleaned_text, temp_file)
            time.sleep(10)
            seg_audio = AudioSegment.from_mp3(temp_file)
            audio_segments.append((seg_audio, start_ms, end_ms))
            print(f"      语音时长: {len(seg_audio)}ms, 字幕时长: {end_ms - start_ms}ms")
        except Exception as e:
            print(f"  警告: 合成失败 '{cleaned_text[:20]}': {e}")
            continue

    if not audio_segments:
        print("错误: 没有成功生成任何语音片段")
        return

    # 3. 确定最终音频的总时长
    # 总时长取最后一个字幕的结束时间（毫秒）
    last_end_ms = max(seg[2] for seg in audio_segments)
    total_duration_ms = last_end_ms + 500  # 末尾留 500ms 缓冲
    print(f"总时长: {total_duration_ms}ms ({total_duration_ms/1000:.1f}秒)")

    # 创建静音画布
    final_audio = AudioSegment.silent(duration=total_duration_ms)

    # 4. 将每个语音片段放置在对应的时间位置
    print("正在拼接音频（按时间轴放置语音片段）...")
    for seg_audio, start_ms, end_ms in audio_segments:
        final_audio = final_audio.overlay(seg_audio, position=start_ms)

    # 5. 导出为 MP3
    print(f"正在导出 {OUTPUT_FILE}...")
    final_audio.export(OUTPUT_FILE, format="mp3", bitrate="192k")

    # 清理临时文件
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    # 输出统计信息
    duration_sec = len(final_audio) / 1000
    size = os.path.getsize(OUTPUT_FILE)
    print(f"\n完成! 已生成 {OUTPUT_FILE}")
    print(f"  音频时长: {duration_sec:.1f} 秒")
    print(f"  文件大小: {size / 1024 / 1024:.1f} MB")
    print(f"  语音片段数: {len(audio_segments)}")







if __name__ == "__main__":
    asyncio.run(main())
