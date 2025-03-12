# Podcast2Summary - Podcast Transcription and Summarization Tool

This tool automatically extracts audio content from Xiaoyuzhou (小宇宙) podcast URLs, converts it to text, and generates content summaries.

## Features

- Automatically extracts audio links from Xiaoyuzhou URLs
- Downloads audio files
- Supports multiple speech recognition methods:
  - Volcengine speech recognition (high quality, supports long audio, includes timestamps and speaker information)
  - Google speech recognition (suitable for short audio)
- Automatic fallback mechanism: when one transcription method fails, it automatically tries others
- Automatically saves transcribed text with filenames based on podcast titles
- Supports summarizing transcribed content using Volcengine LLM API, generating content overviews in Q&A format

## Installation

**Note:** This project comes with a pre-configured virtual environment. If you just downloaded the project, you can skip to the [Usage](#usage) section.

If you need to set up the project from scratch:

1. Clone or download this project

2. Create a `.env` file (copy from `.env.example`) and set your API keys and endpoints:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API keys and configuration:

```
# Volcengine speech recognition service configuration
VOLCENGINE_APPID=your_volcengine_appid_here
VOLCENGINE_TOKEN=your_volcengine_token_here
VOLCENGINE_CLUSTER=your_volcengine_cluster_here

# Volcengine LLM API key (for content summarization)
ARK_API_KEY=your_ark_api_key_here
```

## Usage

### Quick Start (For New Users)

This project comes with a pre-configured virtual environment. You can start the application in just two simple steps:

1. **Make the script executable** (only needed once):
   ```bash
   chmod +x run.sh
   ```

2. **Run the application** using one of these two methods:

   **Method 1:** Using the run.sh script (recommended)
   ```bash
   # Interactive mode
   ./run.sh
   
   # Or with a podcast URL
   ./run.sh "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"
   ```

   **Method 2:** Using the virtual environment's Python directly
   ```bash
   # Interactive mode
   ./venv/bin/python main.py
   
   # Or with a podcast URL
   ./venv/bin/python main.py "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"
   ```

### Command Options

Specify output file:

```bash
./run.sh -o output.txt "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"
```

Select different transcription methods:

```bash
# Use Volcengine for transcription (default, recommended for long audio)
./run.sh --method volcengine "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"

# Use Google speech recognition (suitable for short audio)
./run.sh --method sr "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"

# Transcribe without content summarization
./run.sh --no-summary "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"
```

## Notes

### Important Notes

- **No Virtual Environment Activation Needed**: The project is designed to work without manually activating the virtual environment. The `run.sh` script and the direct method both use the absolute path to the Python interpreter.
- **Long Processing Time**: The transcription process for long podcasts may take a significant amount of time (up to 30 minutes). The application will show progress information including the task ID and elapsed time.

### Transcription Service Notes

- For long audio (podcasts are typically long), Volcengine speech recognition is recommended for better results
- Volcengine speech recognition service features:
  - Supports long audio transcription
  - Provides detailed sentence information and timestamps
  - Can distinguish between different speakers
  - Requires Volcengine API credentials (paid service)
- Content summarization uses Volcengine LLM API, requiring the corresponding API key
- Google speech recognition API has duration limitations, typically only suitable for short audio
- The script has a built-in fallback mechanism, automatically trying other methods when the preferred transcription method fails

### Troubleshooting

- If you encounter a timeout error during transcription, the task ID will be displayed. You can use this ID to check the task status later.
- If the virtual environment's Python interpreter is not found, ensure that the `venv` directory exists in the project root and contains the appropriate files.

## License

MIT

---

# Podcast2Summary - 播客转录与总结工具

这个工具可以根据小宇宙播客的URL，自动提取音频内容，将其转换为文字，并生成内容总结。

## 功能特点

- 从小宇宙URL中自动提取音频链接
- 下载音频文件
- 支持多种语音识别方式：
  - 火山引擎语音识别（高质量，支持长音频，带时间戳和说话人信息）
  - Google语音识别（适用于短音频）
- 自动备选机制：当一种转录方式失败时，自动尝试其他方式
- 自动保存转录文本，文件名使用播客标题
- 支持使用火山引擎LLM API对转录内容进行总结，生成问答格式的内容概要

## 安装

**注意：**本项目已包含预配置的虚拟环境。如果你刚下载了项目，可以直接跳到[使用方法](#使用方法)部分。

如果你需要从头开始设置项目：

1. 克隆或下载本项目

2. 创建`.env`文件（从`.env.example`复制）并设置你的API密钥和端点：

```bash
cp .env.example .env
```

编辑`.env`文件，添加你的API密钥和配置：

```
# 火山引擎语音识别服务配置
VOLCENGINE_APPID=your_volcengine_appid_here
VOLCENGINE_TOKEN=your_volcengine_token_here
VOLCENGINE_CLUSTER=your_volcengine_cluster_here

# 火山引擎LLM API密钥（用于内容总结）
ARK_API_KEY=your_ark_api_key_here
```

## 使用方法

### 快速开始（新用户）

本项目已包含预配置的虚拟环境。你可以通过两个简单的步骤启动应用：

1. **设置脚本为可执行文件**（只需要执行一次）：
   ```bash
   chmod +x run.sh
   ```

2. **运行应用**使用以下两种方法之一：

   **方法1：**使用run.sh脚本（推荐）
   ```bash
   # 交互模式
   ./run.sh
   
   # 或者指定播客URL
   ./run.sh "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"
   ```

   **方法2：**直接使用虚拟环境的Python
   ```bash
   # 交互模式
   ./venv/bin/python main.py
   
   # 或者指定播客URL
   ./venv/bin/python main.py "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"
   ```

### 命令选项

指定输出文件：

```bash
./run.sh -o output.txt "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"
```

选择不同的转录方法：

```bash
# 使用火山引擎进行转录（默认，推荐用于长音频）
./run.sh --method volcengine "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"

# 使用Google语音识别（适用于短音频）
./run.sh --method sr "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"

# 转录但不进行内容总结
./run.sh --no-summary "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"
```

## 注意事项

### 重要说明

- **无需手动激活虚拟环境**：本项目设计为无需手动激活虚拟环境即可工作。run.sh脚本和直接方法都使用Python解释器的绝对路径。
- **处理时间较长**：长播客的转录过程可能需要相当长的时间（最多30分钟）。应用程序会显示进度信息，包括任务ID和已经过的时间。

### 转录服务说明

- 对于长音频（播客通常为长音频），推荐使用火山引擎语音识别，识别效果更好
- 火山引擎语音识别服务特点：
  - 支持长音频转录
  - 提供详细的分句信息和时间戳
  - 可以区分不同说话人
  - 需要火山引擎API凭证（付费服务）
- 内容总结功能使用火山引擎LLM API，需要相应的API密钥
- Google语音识别API有时长限制，通常只适用于短音频
- 脚本内置了备选机制，当首选转录方式失败时，会自动尝试其他方式

### 问题排查

- 如果在转录过程中遇到超时错误，系统会显示任务ID。您可以使用这个ID稍后检查任务状态。
- 如果找不到虚拟环境的Python解释器，请确保项目根目录中存在`venv`目录并包含适当的文件。

## 许可

MIT
