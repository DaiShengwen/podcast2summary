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

1. 克隆或下载本项目
2. 安装依赖项：

```bash
pip install -r requirements.txt
```

3. 创建`.env`文件（从`.env.example`复制）并设置你的API密钥和端点：

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

基本用法：

```bash
# 交互模式（推荐）
./run.sh
# 或
python main.py

# 直接指定URL
./run.sh "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"
# 或
python main.py "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"
```

指定输出文件：

```bash
./run.sh -o output.txt "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"
# 或
python main.py -o output.txt "https://www.xiaoyuzhoufm.com/episode/your-podcast-url"
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

- 对于长音频（播客通常为长音频），推荐使用火山引擎语音识别，识别效果更好
- 火山引擎语音识别服务特点：
  - 支持长音频转录
  - 提供详细的分句信息和时间戳
  - 可以区分不同说话人
  - 需要火山引擎API凭证（付费服务）
- 内容总结功能使用火山引擎LLM API，需要相应的API密钥
- Google语音识别API有时长限制，通常只适用于短音频
- 脚本内置了备选机制，当首选转录方式失败时，会自动尝试其他方式

## 许可

MIT
