import argostranslate.translate 
import argostranslate.package 
import re
import sys
import os

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
