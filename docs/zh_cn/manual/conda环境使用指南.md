# Conda 环境使用指南

M9A 现在默认支持使用 Conda 虚拟环境来运行程序，本指南将介绍如何配置和使用这一功能。

## 前提条件

- 已安装 [Anaconda](https://www.anaconda.com/download) 或 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- 确保 conda 命令已添加到系统 PATH 环境变量中

## 配置方法

M9A 通过环境变量来控制是否使用 conda 环境以及使用哪个 conda 环境。程序默认已启用conda环境支持，如需切换回标准venv环境，可按以下方式配置：

### 方式一：临时设置环境变量（每次运行前设置）

在命令行中运行以下命令：

```bash
# Windows (cmd) - 切换回标准venv环境
set M9A_USE_CONDA=false
python agent/main.py

# Windows (PowerShell) - 切换回标准venv环境
$env:M9A_USE_CONDA="false"
python agent/main.py
```

### 方式二：创建启动脚本

创建一个批处理文件（`.bat`）或 PowerShell 脚本（`.ps1`）来自动设置环境变量并启动程序：

#### Windows 批处理文件示例（`start_venv.bat`）

```batch
@echo off
set M9A_USE_CONDA=false
echo 正在使用标准venv环境
python agent/main.py
pause
```

#### Windows PowerShell 脚本示例（`start_venv.ps1`）

```powershell
$env:M9A_USE_CONDA="false"
Write-Host "正在使用标准venv环境"
python agent/main.py
```

## 工作原理

当设置 `M9A_USE_CONDA=true` 后，程序会：

1. 检查系统中是否已安装 conda
2. 检查指定名称的 conda 环境是否存在，如果不存在则自动创建
3. 在指定的 conda 环境中运行程序
4. 如果当前已经在正确的 conda 环境中，则直接运行程序

## 虚拟环境名称自定义

通过 `M9A_VENV_NAME` 环境变量，您可以自定义使用的 conda 环境名称，例如：

```bash
set M9A_VENV_NAME=my_custom_env  # 使用名为 my_custom_env 的 conda 环境
```

如果不指定，则默认为 `.venv`。

## 切换回标准 venv

如果想要切换回使用标准的 Python venv 虚拟环境，只需设置：

```bash
set M9A_USE_CONDA=false  # 或直接删除这个环境变量
```

## 注意事项

1. 首次使用 conda 环境时，程序会自动创建环境并安装依赖，可能需要一些时间
2. 确保您的 conda 环境中安装了兼容的 Python 版本（3.10-3.13）
3. 如果遇到 conda 相关的错误，请确保 conda 已正确安装并添加到系统 PATH
4. 在 Linux/macOS 系统上，程序使用 `conda run` 命令在指定环境中执行脚本

## 常见问题排查

### Q: 程序提示找不到 conda

A: 请确保 conda 已正确安装，并将 conda 的安装目录（通常是 `C:\Users\用户名\anaconda3\Scripts` 或 `C:\Users\用户名\miniconda3\Scripts`）添加到系统 PATH 环境变量中。

### Q: 创建 conda 环境失败

A: 可能是网络问题或权限问题。请尝试手动创建 conda 环境：

```bash
conda create -n m9a_env python>=3.10,<3.14 -y
```

### Q: 如何查看当前正在使用哪个虚拟环境

A: 程序启动时会在日志中显示当前使用的环境信息，您也可以通过以下命令查看：

```bash
# 查看 conda 环境列表
conda env list

# 查看当前激活的 conda 环境
conda info --envs
```