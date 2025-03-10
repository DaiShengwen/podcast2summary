#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小宇宙播客一键转录与总结工具
此工具可以从小宇宙播客URL中提取音频内容，将其转换为文字，并生成内容总结
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 导入现有模块
from xiaoyuzhou_to_text import process_url
from summarize_transcript import summarize_with_volcengine

# 加载环境变量
load_dotenv()

def process_podcast(url, output_file=None, transcription_method="volcengine", summarize=True):
    """
    处理播客URL，转录为文字并生成总结
    
    参数:
        url: 小宇宙播客URL
        output_file: 输出文件路径
        transcription_method: 转录方法，可选值: "volcengine", "sr"
        summarize: 是否生成总结
    
    返回:
        tuple: (转录文件路径, 总结文件路径)
    """
    print(f"开始处理播客: {url}")
    
    # 第一步：转录
    transcript_file, transcript_text = process_url(url, output_file, transcription_method)
    print(f"转录完成，文件保存在: {transcript_file}")
    
    # 第二步：总结（如果需要）
    summary_file = None
    if summarize:
        print("开始生成内容总结...")
        try:
            summary_file, summary_text = summarize_with_volcengine(transcript_file)
            print(f"总结完成，文件保存在: {summary_file}")
        except Exception as e:
            print(f"总结生成失败: {e}")
    
    return transcript_file, summary_file

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小宇宙播客一键转录与总结工具")
    parser.add_argument("url", nargs="?", help="小宇宙播客的URL")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("--method", choices=["volcengine", "sr"], default="volcengine",
                      help="转录方法: volcengine (火山引擎), sr (Speech Recognition)")
    parser.add_argument("--no-summary", action="store_true", help="不生成内容总结")
    
    args = parser.parse_args()
    
    # 如果没有提供URL，进入交互模式
    url = args.url
    if not url:
        print("请输入待总结的小宇宙URL:")
        url = input().strip()
        
        if not url:
            print("未提供URL，退出程序")
            sys.exit(1)
    
    try:
        transcript_file, summary_file = process_podcast(
            url, 
            args.output, 
            args.method, 
            not args.no_summary
        )
        
        print("\n处理完成!")
        print(f"转录文件: {transcript_file}")
        if summary_file:
            print(f"总结文件: {summary_file}")
    
    except Exception as e:
        print(f"处理失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
