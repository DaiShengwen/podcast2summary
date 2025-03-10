#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用火山引擎语音识别服务转录音频
"""

import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 火山引擎API配置
VOLCENGINE_APPID = os.getenv("VOLCENGINE_APPID", "8503125436")
VOLCENGINE_TOKEN = os.getenv("VOLCENGINE_TOKEN", "7ZUtArAGWSuh3qu2Z48EcFs4HhwTifYd")
VOLCENGINE_CLUSTER = os.getenv("VOLCENGINE_CLUSTER", "volc_auc_common")

# API URL
SUBMIT_URL = "https://openspeech.bytedance.com/api/v1/auc/submit"
QUERY_URL = "https://openspeech.bytedance.com/api/v1/auc/query"

# 请求头
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer; {VOLCENGINE_TOKEN}'
}

def transcribe_with_volcengine(audio_url=None, audio_path=None, language="zh-CN", with_speaker_info=False):
    """
    使用火山引擎语音识别服务转录音频
    
    参数:
        audio_url: 音频URL
        audio_path: 本地音频文件路径
        language: 语言代码，默认为中文
        with_speaker_info: 是否返回说话人信息
        
    返回:
        转录文本
    """
    if not audio_url and not audio_path:
        raise ValueError("必须提供音频URL或本地音频文件路径")
    
    # 如果提供了本地文件路径，需要上传到可访问的URL
    if audio_path and not audio_url:
        # 这里需要实现文件上传逻辑，或者使用本地文件路径
        # 由于火山引擎API需要可访问的URL，这里暂时抛出错误
        raise NotImplementedError("暂不支持直接使用本地文件，请提供可访问的音频URL")
    
    # 确定音频格式
    audio_format = "mp3"  # 默认格式
    if audio_url:
        if audio_url.lower().endswith(".mp3"):
            audio_format = "mp3"
        elif audio_url.lower().endswith(".wav"):
            audio_format = "wav"
        elif audio_url.lower().endswith(".m4a"):
            audio_format = "m4a"
        elif audio_url.lower().endswith(".ogg"):
            audio_format = "ogg"
    
    # 构建请求数据
    submit_data = {
        "app": {
            "appid": VOLCENGINE_APPID,
            "token": VOLCENGINE_TOKEN,
            "cluster": VOLCENGINE_CLUSTER
        },
        "user": {
            "uid": f"user_{int(time.time())}"  # 使用时间戳作为用户ID
        },
        "audio": {
            "format": audio_format,
            "url": audio_url
        },
        "additions": {
            "use_itn": "True",  # 数字归一化
            "use_punc": "True",  # 添加标点
            "with_speaker_info": "True" if with_speaker_info else "False",
            "language": language
        }
    }
    
    try:
        print(f"正在提交音频识别任务...")
        # 提交任务
        submit_response = requests.post(SUBMIT_URL, headers=HEADERS, data=json.dumps(submit_data))
        submit_response.raise_for_status()
        
        submit_result = submit_response.json()
        if 'resp' not in submit_result or submit_result['resp'].get('code') != 1000:
            error_msg = submit_result.get('resp', {}).get('message', '未知错误')
            raise Exception(f"提交任务失败: {error_msg}")
        
        task_id = submit_result['resp']['id']
        print(f"任务提交成功，任务ID: {task_id}")
        
        # 构建查询数据
        query_data = {
            "appid": VOLCENGINE_APPID,
            "token": VOLCENGINE_TOKEN,
            "cluster": VOLCENGINE_CLUSTER,
            "id": task_id
        }
        
        # 查询结果，最多等待10分钟
        start_time = time.time()
        max_wait_time = 600  # 10分钟
        
        while True:
            # 等待15秒后查询
            time.sleep(15)
            
            query_response = requests.post(QUERY_URL, headers=HEADERS, data=json.dumps(query_data))
            query_response.raise_for_status()
            
            query_result = query_response.json()
            if 'resp' not in query_result:
                raise Exception("查询结果格式错误")
            
            code = query_result['resp'].get('code', 0)
            message = query_result['resp'].get('message', '')
            
            # 任务完成
            if code == 1000:
                text = query_result['resp'].get('text', '')
                
                # 保存详细结果到文件
                result_file = f"volcengine_result_{task_id}.json"
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(query_result, f, ensure_ascii=False, indent=2)
                print(f"详细结果已保存到: {result_file}")
                
                return text
            
            # 任务失败
            elif code < 2000 and code != 1000:
                raise Exception(f"任务失败: {message}")
            
            # 检查是否超时
            if time.time() - start_time > max_wait_time:
                raise Exception("等待超时，任务可能仍在处理中")
            
            print(f"任务处理中: {message}，继续等待...")
    
    except Exception as e:
        print(f"使用火山引擎转录时出错: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="使用火山引擎语音识别服务转录音频")
    parser.add_argument("--url", help="音频URL")
    parser.add_argument("--path", help="本地音频文件路径")
    parser.add_argument("--language", default="zh-CN", help="语言代码，默认为中文")
    parser.add_argument("--speaker", action="store_true", help="是否返回说话人信息")
    
    args = parser.parse_args()
    
    try:
        text = transcribe_with_volcengine(
            audio_url=args.url,
            audio_path=args.path,
            language=args.language,
            with_speaker_info=args.speaker
        )
        
        print("\n转录文本预览:")
        print("-" * 40)
        preview = text[:500] + "..." if len(text) > 500 else text
        print(preview)
        print("-" * 40)
        
        # 保存文本到文件
        output_file = f"volcengine_transcript_{int(time.time())}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"完整转录已保存到: {output_file}")
    
    except Exception as e:
        print(f"错误: {e}")
