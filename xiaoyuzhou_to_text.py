#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小宇宙播客音频转文字工具
此工具可以从小宇宙播客URL中提取音频内容，并将其转换为文字
"""

import os
import re
import sys
import json
import time
import argparse
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import speech_recognition as sr
from pydub import AudioSegment
from dotenv import load_dotenv

# 导入火山引擎转录模块
from transcribe_with_volcengine import transcribe_with_volcengine

# 加载环境变量
load_dotenv()

# 用户代理头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
}


def extract_audio_url(xiaoyuzhou_url):
    """从小宇宙URL中提取音频URL"""
    try:
        # 获取页面内容
        print(f"正在从{xiaoyuzhou_url}提取音频...")
        response = requests.get(xiaoyuzhou_url, headers=HEADERS)
        response.raise_for_status()
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找标题
        title_tag = soup.find('title')
        episode_title = title_tag.text.strip() if title_tag else "未知标题"
        
        # 方法1: 从脚本标签中查找音频URL
        scripts = soup.find_all('script')
        audio_url = None
        
        for script in scripts:
            if script.string and 'window.__INITIAL_STATE__' in script.string:
                # 提取JSON数据
                match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*});', script.string)
                if match:
                    data = json.loads(match.group(1))
                    # 查找音频URL的可能路径
                    try:
                        if 'podcast' in data and 'episodes' in data['podcast']:
                            for episode in data['podcast']['episodes']:
                                if 'enclosure' in episode and 'url' in episode['enclosure']:
                                    audio_url = episode['enclosure']['url']
                                    if 'title' in episode:
                                        episode_title = episode['title']
                                    break
                    except (KeyError, TypeError):
                        continue
        
        # 方法2: 查找audio标签
        if not audio_url:
            print("尝试从音频标签提取...")
            audio_tags = soup.find_all('audio')
            for audio in audio_tags:
                if audio.get('src'):
                    audio_url = audio.get('src')
                    break
                for source in audio.find_all('source'):
                    if source.get('src'):
                        audio_url = source.get('src')
                        break
        
        # 方法3: 查找可能的音频链接
        if not audio_url:
            print("尝试查找可能的音频链接...")
            audio_extensions = ['.mp3', '.m4a', '.wav', '.ogg', '.aac']
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                if any(href.endswith(ext) for ext in audio_extensions):
                    audio_url = href
                    break
        
        # 方法4: 在页面源代码中直接搜索音频URL模式
        if not audio_url:
            print("尝试在源代码中搜索音频URL...")
            url_patterns = [
                r'https?://[^"\']+\.mp3',
                r'https?://[^"\']+\.m4a',
                r'https?://[^"\']+\.wav',
                r'https?://[^"\']+\.ogg',
                r'https?://[^"\']+\.aac',
                r'https?://media\.xyzcdn\.net/[^"\']+' 
            ]
            
            for pattern in url_patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    audio_url = matches[0]
                    break
        
        if not audio_url:
            raise ValueError("无法从页面中提取音频URL")
        
        print(f"成功提取音频URL: {audio_url}")
        return audio_url, episode_title
    
    except Exception as e:
        print(f"提取音频URL时出错: {e}")
        raise


def download_audio(audio_url, output_path=None):
    """下载音频文件到临时目录或指定路径"""
    try:
        print(f"正在下载音频: {audio_url}")
        
        response = requests.get(audio_url, headers=HEADERS, stream=True)
        response.raise_for_status()
        
        # 确定文件类型
        content_type = response.headers.get('Content-Type', '')
        ext = '.mp3'  # 默认扩展名
        if 'audio/mpeg' in content_type:
            ext = '.mp3'
        elif 'audio/mp4' in content_type:
            ext = '.m4a'
        elif 'audio/x-wav' in content_type or 'audio/wav' in content_type:
            ext = '.wav'
        
        # 如果未指定输出路径，则使用临时文件
        if not output_path:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            output_path = temp_file.name
            temp_file.close()
        
        # 下载文件
        with open(output_path, 'wb') as f:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192
            
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # 显示下载进度
                    if total_size > 0:
                        done = int(50 * downloaded / total_size)
                        sys.stdout.write('\r[%s%s] %d%%' % ('█' * done, ' ' * (50 - done), done * 2))
                        sys.stdout.flush()
            
            if total_size > 0:
                sys.stdout.write('\n')
        
        print(f"音频下载完成: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"下载音频时出错: {e}")
        if not output_path and 'temp_file' in locals():
            os.unlink(temp_file.name)
        raise



def transcribe_with_sr(audio_path, language="zh-CN"):
    """使用SpeechRecognition库转录音频（较短音频适用）"""
    try:
        print("正在使用Speech Recognition进行音频转录...")
        
        # 如果是mp3或m4a，转换为wav
        if not audio_path.endswith('.wav'):
            print("转换音频格式为WAV...")
            sound = AudioSegment.from_file(audio_path)
            wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
            sound.export(wav_path, format="wav")
            audio_path = wav_path
        
        # 初始化识别器
        recognizer = sr.Recognizer()
        
        # 加载音频文件
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        
        # 使用Google Speech Recognition API
        text = recognizer.recognize_google(audio_data, language=language)
        return text
    
    except Exception as e:
        print(f"使用Speech Recognition转录时出错: {e}")
        print("注意: 此方法仅适用于短音频。对于长播客，请使用Whisper API。")
        raise


def save_text(text, output_file=None, title=None):
    """保存转录文本到文件"""
    if not output_file:
        # 如果没有指定输出文件，使用标题或时间戳作为文件名
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{title if title else 'transcription'}-{timestamp}.txt"
        output_file = filename
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            if title:
                f.write(f"标题: {title}\n\n")
            f.write(text)
        
        print(f"转录文本已保存到: {output_file}")
        return output_file
    
    except Exception as e:
        print(f"保存文本时出错: {e}")
        raise


def process_url(url, output_file=None, transcription_method="volcengine"):
    """处理小宇宙URL，将音频转为文字
    
    参数:
        url: 小宇宙播客URL
        output_file: 输出文件路径
        transcription_method: 转录方法，可选值: "whisper", "sr", "volcengine"
    """
    try:
        # 验证URL格式
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("无效的URL格式")
        
        # 1. 提取音频URL
        print(f"正在从{url}提取音频...")
        audio_url, title = extract_audio_url(url)
        
        # 2. 下载音频
        audio_path = download_audio(audio_url)
        
        # 3. 转录音频
        text = None
        if transcription_method == "volcengine":
            print("使用火山引擎进行转录...")
            text = transcribe_with_volcengine(audio_url=audio_url)
        else:  # sr
            print("使用Speech Recognition进行转录...")
            text = transcribe_with_sr(audio_path)
        
        # 4. 保存文本
        if not output_file and title:
            # 使用标题作为文件名的一部分
            safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            if len(safe_title) > 50:
                safe_title = safe_title[:50]
            output_file = f"{safe_title}.txt"
        
        result_file = save_text(text, output_file, title)
        
        # 5. 清理临时文件
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        
        print(f"处理完成! 文本已保存到: {result_file}")
        return result_file, text
    
    except Exception as e:
        print(f"处理URL时出错: {e}")
        raise
    finally:
        # 确保临时文件被删除
        if 'audio_path' in locals() and os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
            except:
                pass


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="将小宇宙播客转换为文字")
    parser.add_argument("url", help="小宇宙播客的URL")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("--method", choices=["volcengine", "sr"], default="volcengine",
                        help="转录方法: volcengine (火山引擎), sr (Speech Recognition)")
    parser.add_argument("--summarize", action="store_true",
                        help="转录完成后使用LLM进行总结")
    
    args = parser.parse_args()
    
    try:
        file_path, text = process_url(args.url, args.output, args.method)
        print("\n转录文本预览:")
        print("-" * 40)
        preview = text[:500] + "..." if len(text) > 500 else text
        print(preview)
        print("-" * 40)
        print(f"完整转录已保存到: {file_path}")
        
        # 如果指定了总结选项，则调用总结功能
        if args.summarize:
            try:
                from summarize_transcript import summarize_with_volcengine
                print("\n正在使用LLM对转录内容进行总结...")
                summary_path, summary = summarize_with_volcengine(file_path)
                print("\n总结预览:")
                print("-" * 40)
                preview = summary[:500] + "..." if len(summary) > 500 else summary
                print(preview)
                print("-" * 40)
                print(f"完整总结已保存到: {summary_path}")
            except Exception as e:
                print(f"总结失败: {e}")
    
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
