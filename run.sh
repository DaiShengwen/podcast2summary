#!/bin/bash

# 定义虚拟环境中Python解释器的路径
VENV_PYTHON="./venv/bin/python"

# 如果没有参数，直接运行脚本，进入交互模式
if [ $# -eq 0 ]; then
    echo "进入交互模式..."
    # 直接使用虚拟环境中的Python解释器运行脚本
    $VENV_PYTHON main.py
    exit 0
fi

# 使用虚拟环境中的Python解释器运行脚本
$VENV_PYTHON main.py "$@"
