# M9A Conda 环境配置指南

## 简介

M9A 项目现已支持使用 Conda 虚拟环境来运行程序。相比标准的 Python `venv`，Conda 环境具有以下优势：

- 更好地管理复杂的依赖关系
- 更灵活地处理不同 Python 版本
- 更强大的包管理功能
- 支持跨平台一致的环境配置

## 快速开始

### 一键配置（推荐）

M9A 提供了便捷的脚本，可以一键完成 Conda 环境的配置并启动程序：

#### Windows 用户

1. 确保已安装 [Anaconda](https://www.anaconda.com/) 或 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
2. 双击运行项目根目录下的 `setup_and_run_conda.bat`
3. 脚本会自动：
   - 检查系统中的 Conda 安装
   - 创建或更新名为 `m9a_env` 的 Conda 环境
   - 安装所有必要的依赖
   - 设置正确的环境变量
   - 启动 M9A 程序

#### Linux/macOS 用户

1. 确保已安装 Anaconda 或 Miniconda
2. 在终端中执行以下命令：
   ```bash
   cd /path/to/M9A
   chmod +x setup_and_run_conda.sh
   ./setup_and_run_conda.sh
   ```
3. 脚本会自动完成环境配置并启动程序

### 手动配置

如果您需要手动控制环境配置过程，可以按照以下步骤操作：

1. 确保已安装 Anaconda 或 Miniconda
2. 创建 Conda 环境：
   ```bash
   conda env create -f environment.yml
   ```
3. 激活环境：
   ```bash
   # Windows
   conda activate m9a_env
   
   # Linux/macOS
   source activate m9a_env
   ```
4. 设置使用 Conda 的环境变量：
   ```bash
   # Windows (cmd)
   set M9A_USE_CONDA=true
   
   # Windows (PowerShell)
   $env:M9A_USE_CONDA="true"
   
   # Linux/macOS
   export M9A_USE_CONDA=true
   ```
5. 运行 M9A：
   ```bash
   python agent/main.py
   ```

## 自定义环境名称

默认情况下，脚本会创建名为 `m9a_env` 的 Conda 环境。如果您需要使用自定义名称，可以通过设置 `M9A_VENV_NAME` 环境变量来实现：

```bash
# Windows (cmd)
set M9A_VENV_NAME=my_custom_env

# Linux/macOS
export M9A_VENV_NAME=my_custom_env
```

然后再运行启动脚本或手动创建环境。

## 切换回标准 venv 环境

如果您想暂时使用标准的 Python venv 而不是 Conda 环境，可以设置：

```bash
# Windows (cmd)
set M9A_USE_CONDA=false

# Linux/macOS
export M9A_USE_CONDA=false
```

或者创建一个使用标准 venv 的快捷启动脚本。

## 疑难解答

### Conda 未找到

如果脚本提示找不到 Conda，请确保：
- Anaconda/Miniconda 已正确安装
- Conda 已添加到系统 PATH 环境变量中
- 尝试重新启动命令提示符或终端

### 环境创建失败

如果创建 Conda 环境时出现问题：
- 检查网络连接是否正常
- 确认 Anaconda/Miniconda 有足够的权限
- 可以尝试手动运行 `conda env create -f environment.yml` 查看详细错误信息

### 依赖安装失败

如果遇到依赖安装问题：
- 可能是特定包的版本冲突
- 可以检查项目根目录的 `requirements.txt` 文件
- 考虑使用国内镜像源加速安装（通过 `config/pip_config.json` 配置）

## 相关文档

- [Conda 官方文档](https://conda.io/projects/conda/en/latest/user-guide/index.html)
- [Python 虚拟环境使用指南](https://docs.python.org/zh-cn/3/tutorial/venv.html)
- [M9A 新手上路文档](docs/zh_cn/manual/新手上路.md)
- [M9A Conda 环境使用指南](docs/zh_cn/manual/conda环境使用指南.md)