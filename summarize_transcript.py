#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将转录文本发送给火山引擎LLM API进行总结
"""

import os
import json
import argparse
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def summarize_with_volcengine(transcript_file, output_file=None):
    """
    使用火山引擎LLM API对转录文本进行总结
    
    参数:
        transcript_file: 转录文本文件路径
        output_file: 输出文件路径，默认为None（自动生成）
    
    返回:
        tuple: (输出文件路径, 总结文本)
    """
    # 读取转录文本
    print(f"读取转录文本: {transcript_file}")
    with open(transcript_file, 'r', encoding='utf-8') as f:
        transcript_text = f.read()
    
    # 构建提示词
    prompt = f"""我现在要给你发一个播客的内容记录。我需要你：
1. 首先用一段话总结播客的答题内容；
2. 按照"问题"和"回答"进行播客内容的具体总结，格式是：问题1：balabala, 回答：balabal; 问题2：...

播客内容：{transcript_text}
"""
    
    # 准备API请求
    api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    # 从环境变量获取API密钥
    ark_api_key = os.getenv("ARK_API_KEY")
    
    if not ark_api_key:
        raise ValueError("请在.env文件中设置ARK_API_KEY")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ark_api_key}"
    }
    
    # 构建请求体
    payload = {
        "model": "ep-20250214142937-g8bvt",  # 使用用户提供的模型标识符
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的播客内容分析助手。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    print("正在发送请求到火山引擎LLM API...")
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"API请求失败: {response.status_code}")
        print(response.text)
        raise Exception(f"API请求失败: {response.status_code}, {response.text}")
    
    # 解析响应
    result = response.json()
    print(f"API响应状态码: {response.status_code}")
    
    try:
        summary_text = result["choices"][0]["message"]["content"]
    except KeyError as e:
        print(f"API响应解析错误: {e}")
        print(f"API响应内容: {result}")
        raise Exception(f"API响应格式不符合预期: {e}")
    
    # 保存总结文本
    if output_file is None:
        base_name = os.path.splitext(transcript_file)[0]
        output_file = f"{base_name}_summary.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    
    print(f"总结文本已保存到: {output_file}")
    
    # 返回文件路径和总结文本
    return output_file, summary_text

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="将转录文本发送给LLM进行总结")
    parser.add_argument("transcript_file", help="转录文本文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    try:
        file_path, summary = summarize_with_volcengine(args.transcript_file, args.output)
        print("\n总结预览:")
        print("-" * 40)
        preview = summary[:500] + "..." if len(summary) > 500 else summary
        print(preview)
        print("-" * 40)
        print(f"完整总结已保存到: {file_path}")
    except Exception as e:
        print(f"处理失败: {e}")

if __name__ == "__main__":
    main()
