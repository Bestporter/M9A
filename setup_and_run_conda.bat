@echo off
setlocal enabledelayedexpansion

echo ===================================================================
echo M9A项目 - Conda环境设置与启动脚本
echo ===================================================================
echo 

REM 检查是否安装了conda
where conda > nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到conda命令，请确保已安装Anaconda或Miniconda并添加到系统PATH
    echo 或手动运行以下命令创建环境：
    echo conda env create -f environment.yml
    pause
    exit /b 1
)

echo 检查conda环境是否存在...
conda env list | findstr /i "m9a_env" > nul
if %errorlevel% equ 0 (
    echo 发现已存在的m9a_env环境，将更新环境...
    conda env update -f environment.yml
) else (
    echo 未发现m9a_env环境，开始创建...
    conda env create -f environment.yml
    if %errorlevel% neq 0 (
        echo 错误: 创建conda环境失败
        pause
        exit /b 1
    )
)

echo 激活conda环境...
call conda activate m9a_env

echo 设置使用conda环境的标志...
set M9A_USE_CONDA=true

echo 环境设置完成，正在启动M9A...
python agent/main.py

REM 保存退出码
set exit_code=%errorlevel%

REM 恢复默认环境
echo 正在恢复环境设置...
call conda deactivate

echo 程序已退出，退出码: %exit_code%
pause
endlocal