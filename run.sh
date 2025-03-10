#!/bin/bash

# 激活虚拟环境
source venv/bin/activate

# 如果没有参数，直接运行脚本，进入交互模式
if [ $# -eq 0 ]; then
    echo "进入交互模式..."
    # 直接运行脚本，不需要参数
    python main.py
    exit 0
fi

# 运行脚本
python main.py "$@"

# 可选: 添加此行以在脚本完成后退出虚拟环境
# deactivate
