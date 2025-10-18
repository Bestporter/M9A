#!/bin/bash

echo "==================================================================="
echo "M9A项目 - Conda环境设置与启动脚本"
echo "==================================================================="
echo ""

# 检查是否安装了conda
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到conda命令，请确保已安装Anaconda或Miniconda并添加到系统PATH"
    echo "或手动运行以下命令创建环境："
    echo "conda env create -f environment.yml"
    exit 1
fi

# 检查conda环境是否存在
if conda env list | grep -q "m9a_env"; then
    echo "发现已存在的m9a_env环境，将更新环境..."
    conda env update -f environment.yml
else
    echo "未发现m9a_env环境，开始创建..."
    conda env create -f environment.yml
    if [ $? -ne 0 ]; then
        echo "错误: 创建conda环境失败"
        exit 1
    fi
fi

# 激活conda环境
echo "激活conda环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate m9a_env

# 设置使用conda环境的标志
echo "设置使用conda环境的标志..."
export M9A_USE_CONDA=true

# 启动M9A
echo "环境设置完成，正在启动M9A..."
python agent/main.py

# 保存退出码
exit_code=$?

# 恢复默认环境
echo "正在恢复环境设置..."
conda deactivate

echo "程序已退出，退出码: $exit_code"