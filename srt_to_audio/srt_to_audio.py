import asyncio
import edge_tts
import pysrt
from pydub import AudioSegment
import os
import re
import shutil

# 配置
SRT_FILE = "output.srt"
OUTPUT_FILE = "output.mp3"
TEMP_DIR = "temp_audio"
VOICE = "zh-CN-XiaoxiaoNeural"  # 中文女声


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
