import subprocess

# 1. 设置本地 FFmpeg 的绝对路径
ffmpeg_path = r"C:\translate\ffmpeg.exe"  # Windows 示例
# ffmpeg_path = "/usr/local/bin/ffmpeg" # Mac/Linux 示例

# 2. 构造命令参数列表（例如将 input.mp4 转为 output.mp4）
input_file = "input.mp4"
output_file = "output.mp4"

cmd = [
    ffmpeg_path,
    "-i", input_file,
    "-i", "output.mp3",
    "-c:v", "copy",
    "-c:a", "aac",
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-y",  # 覆盖已存在的文件
    output_file
]

# 3. 使用 subprocess 执行
try:
    # 运行命令并捕获输出
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
        encoding="utf-8"
    )
    print("转换成功！")
except subprocess.CalledProcessError as e:
    print("转换失败，错误信息：", e.stderr)
