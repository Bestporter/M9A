# -*- coding: utf-8 -*-

import os
import sys
import json
import subprocess
from pathlib import Path

# utf-8
sys.stdout.reconfigure(encoding="utf-8")

# 获取当前main.py路径并设置上级目录为工作目录
current_file_path = os.path.abspath(__file__)
current_script_dir = os.path.dirname(current_file_path)  # 包含此脚本的目录
project_root_dir = os.path.dirname(current_script_dir)  # 假定的项目根目录

# 更改CWD到项目根目录
if os.getcwd() != project_root_dir:
    os.chdir(project_root_dir)
print(f"set cwd: {os.getcwd()}")

# 将脚本自身的目录添加到sys.path，以便导入utils、maa等模块
if current_script_dir not in sys.path:
    sys.path.insert(0, current_script_dir)

from utils import logger

# 虚拟环境配置 - 支持conda和标准venv
# 默认设置为true，优先使用conda环境
USE_CONDA = os.environ.get("M9A_USE_CONDA", "true").lower() in ("true", "1", "yes")
VENV_NAME = os.environ.get("M9A_VENV_NAME", ".venv").strip()  # 虚拟环境名称，可通过环境变量配置，去除首尾空格
VENV_DIR = Path(project_root_dir) / VENV_NAME

logger.debug(f"虚拟环境配置: USE_CONDA={USE_CONDA}, VENV_NAME={VENV_NAME}")

### 虚拟环境相关 ###


def _is_running_in_our_venv():
    """检查脚本是否在指定的虚拟环境中运行，支持conda和标准venv。"""
    try:
        current_python = Path(sys.executable).resolve()

        logger.debug(f"当前Python解释器: {current_python}")
        
        # 检查是否在conda环境中
        conda_prefix = os.environ.get("CONDA_PREFIX")
        conda_default_env = os.environ.get("CONDA_DEFAULT_ENV")
        
        if USE_CONDA and conda_prefix and conda_default_env:
            # 如果使用conda模式且检测到conda环境
            try:
                conda_env_name = Path(conda_prefix).name
                logger.debug(f"检测到conda环境: {conda_env_name} (CONDA_DEFAULT_ENV={conda_default_env})")
                # 检查是否为目标conda环境
                if conda_env_name == VENV_NAME or conda_default_env == VENV_NAME:
                    logger.debug(f"当前在目标conda环境中: {VENV_NAME}")
                    return True
                else:
                    logger.debug(f"当前不在目标conda环境中 (当前: {conda_env_name}, 目标: {VENV_NAME})")
                    return False
            except Exception as e:
                logger.debug(f"解析conda环境路径时出错: {e}")
                return False
        
        # 标准venv检测逻辑
        if sys.platform.startswith("win"):
            # Windows: 如果在虚拟环境中，Python应该在 Scripts 目录下
            if current_python.parent.name == "Scripts":
                # 进一步检查是否是我们的虚拟环境
                venv_base = current_python.parent.parent
                if venv_base.name == VENV_NAME:
                    return True
        else:
            # Linux/Unix: 如果在虚拟环境中，Python应该在 bin 目录下
            if current_python.parent.name == "bin":
                # 进一步检查是否是我们的虚拟环境
                venv_base = current_python.parent.parent
                if venv_base.name == VENV_NAME:
                    return True
        
        logger.debug("当前不在目标虚拟环境中")
        return False
    except Exception as e:
        logger.debug(f"检查虚拟环境状态时发生异常: {e}")
        return False


def ensure_venv_and_relaunch_if_needed():
    """
    确保虚拟环境存在，并且如果尚未在指定的虚拟环境中运行，
    则在其中重新启动脚本。支持conda和标准venv，以及Linux和Windows系统。
    """
    logger.info(f"检测到系统: {sys.platform}。当前Python解释器: {sys.executable}")

    # 验证VENV_NAME是否有效
    if not VENV_NAME or not isinstance(VENV_NAME, str) or len(VENV_NAME.strip()) == 0:
        logger.error("虚拟环境名称无效，请检查M9A_VENV_NAME环境变量设置")
        sys.exit(1)

    if _is_running_in_our_venv():
        if USE_CONDA:
            logger.info(f"已在目标conda环境 ({VENV_NAME}) 中运行。")
        else:
            logger.info(f"已在目标虚拟环境 ({VENV_DIR}) 中运行。")
        return

    # 全局变量需要nonlocal或global声明
    use_conda = USE_CONDA  # 创建本地变量避免修改全局变量

    if use_conda:
        # Conda环境处理逻辑
        logger.info(f"使用conda模式，目标环境: {VENV_NAME}")
        
        # 检查conda是否安装
        try:
            result = subprocess.run(
                ["conda", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.error("未检测到conda。请确保conda已正确安装并添加到系统PATH。")
                logger.error("您可以通过设置环境变量 M9A_USE_CONDA=false 来使用标准venv。")
                sys.exit(1)
            conda_version = result.stdout.strip()
            logger.info(f"检测到conda: {conda_version}")
        except FileNotFoundError:
            logger.error("未找到conda命令。请确保conda已正确安装并添加到系统PATH。")
            logger.error("您可以通过设置环境变量 M9A_USE_CONDA=false 来使用标准venv。")
            sys.exit(1)
        except Exception as e:
            logger.error(f"检查conda安装状态时发生错误: {e}")
            sys.exit(1)
        
        # 检查conda环境是否存在
        try:
            result = subprocess.run(
                ["conda", "env", "list"],
                capture_output=True,
                text=True
            )
            
            # 更严格地检查conda环境是否存在
            env_exists = False
            for line in result.stdout.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    # conda env list输出格式: env_name  /path/to/env
                    parts = line.split(None, 1)
                    if len(parts) > 0 and parts[0] == VENV_NAME:
                        env_exists = True
                        break
            
            if env_exists:
                logger.info(f"conda环境 '{VENV_NAME}' 已存在")
            else:
                logger.info(f"正在创建conda环境 '{VENV_NAME}'...")
                try:
                    # 创建conda环境
                    create_cmd = ["conda", "create", "-n", VENV_NAME, "python>=3.10,<3.14", "-y"]
                    logger.debug(f"执行命令: {' '.join(create_cmd)}")
                    
                    # 使用更详细的错误处理
                    create_result = subprocess.run(
                        create_cmd,
                        capture_output=True,
                        text=True
                    )
                    
                    if create_result.returncode != 0:
                        logger.error(f"创建conda环境失败，返回码: {create_result.returncode}")
                        error_output = create_result.stderr if create_result.stderr else create_result.stdout
                        logger.error(f"错误输出: {error_output[:500]}..." if len(error_output) > 500 else f"错误输出: {error_output}")
                        sys.exit(1)
                    
                    logger.info(f"conda环境 '{VENV_NAME}' 创建成功")
                except Exception as e:
                    logger.error(f"创建conda环境时发生异常: {e}")
                    sys.exit(1)
        except Exception as e:
            logger.exception(f"检查conda环境时发生错误: {e}")
            sys.exit(1)
        
        # 确定conda中的python路径
        try:
            if sys.platform.startswith("win"):
                # Windows下conda环境的python路径
                try:
                    conda_root = subprocess.check_output(["conda", "info", "--base"], text=True).strip()
                except subprocess.CalledProcessError as e:
                    logger.error(f"获取conda基础路径失败: {e}")
                    sys.exit(1)
                
                python_in_venv = Path(conda_root) / "envs" / VENV_NAME / "python.exe"
                
                if not python_in_venv.exists():
                    logger.error(f"在conda环境中未找到Python解释器: {python_in_venv}")
                    sys.exit(1)
            else:
                # Linux/macOS下使用conda run来执行
                logger.info(f"使用conda run在环境 '{VENV_NAME}' 中执行脚本")
                cmd = ["conda", "run", "-n", VENV_NAME, "--no-capture-output", sys.executable] + sys.argv
                logger.info(f"执行命令: {' '.join(cmd)}")
                
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=os.getcwd(),
                        env=os.environ.copy(),
                        check=False,
                    )
                    sys.exit(result.returncode)
                except FileNotFoundError:
                    logger.error("找不到conda命令，请检查conda安装")
                    sys.exit(1)
                except PermissionError:
                    logger.error("没有执行conda命令的权限")
                    sys.exit(1)
        except Exception as e:
            logger.exception(f"获取conda环境Python路径失败: {e}")
            sys.exit(1)
    else:
        # 标准venv处理逻辑
        if not VENV_DIR.exists():
            logger.info(f"正在 {VENV_DIR} 创建虚拟环境...")
            try:
                # 使用当前运行此脚本的Python（系统/外部Python）
                result = subprocess.run(
                    [sys.executable, "-m", "venv", str(VENV_DIR)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.error(f"创建虚拟环境失败，返回码: {result.returncode}")
                    error_output = result.stderr if result.stderr else result.stdout
                    logger.error(f"错误输出: {error_output[:500]}..." if len(error_output) > 500 else f"错误输出: {error_output}")
                    logger.error("正在退出")
                    sys.exit(1)
                    
                logger.info(f"创建成功")
            except FileNotFoundError:
                logger.error(
                    f"命令 '{sys.executable} -m venv' 未找到。请确保 'venv' 模块可用。"
                )
                logger.error("无法在没有虚拟环境的情况下继续。正在退出。")
                sys.exit(1)
            except Exception as e:
                logger.error(f"创建虚拟环境时发生未知错误: {e}")
                sys.exit(1)

        # 确定虚拟环境中的Python解释器路径
        if sys.platform.startswith("win"):
            python_in_venv = VENV_DIR / "Scripts" / "python.exe"
        else:
            python3_path = VENV_DIR / "bin" / "python3"
            python_path = VENV_DIR / "bin" / "python"
            if python3_path.exists():
                python_in_venv = python3_path
            elif python_path.exists():
                python_in_venv = python_path
            else:
                python_in_venv = python3_path  # 默认使用python3，让后续错误处理捕获

    if not python_in_venv.exists():
        logger.error(f"在虚拟环境 {python_in_venv} 中未找到Python解释器。")
        logger.error("虚拟环境创建可能失败或虚拟环境结构异常。")
        sys.exit(1)

    logger.info(f"正在使用虚拟环境Python重新启动")

    try:
        cmd = [str(python_in_venv)] + sys.argv
        logger.info(f"执行命令: {' '.join(cmd)}")

        # 使用更详细的错误处理
        try:
            result = subprocess.run(
                cmd,
                cwd=os.getcwd(),
                env=os.environ.copy(),
                check=False,  # 不在非零退出码时抛出异常
            )
            # 退出时使用子进程的退出码
            sys.exit(result.returncode)
        except FileNotFoundError:
            logger.error(f"找不到Python解释器: {python_in_venv}")
            sys.exit(1)
        except PermissionError:
            logger.error(f"没有执行权限: {python_in_venv}")
            sys.exit(1)

    except Exception as e:
        logger.exception(f"在虚拟环境中重新启动脚本失败: {e}")
        sys.exit(1)


### 配置相关 ###


def read_interface_version(interface_file_name="./interface.json") -> str:
    interface_path = Path(project_root_dir) / interface_file_name
    assets_interface_path = Path(project_root_dir) / "assets" / interface_file_name

    target_path = None
    if interface_path.exists():
        target_path = interface_path
    elif assets_interface_path.exists():
        return "DEBUG"

    if target_path is None:
        logger.warning("未找到interface.json")
        return "unknown"

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            interface_data = json.load(f)
            return interface_data.get("version", "unknown")
    except Exception:
        logger.exception(f"读取interface.json版本失败，文件路径：{target_path}")
        return "unknown"


def read_pip_config() -> dict:
    config_dir = Path("./config")
    config_dir.mkdir(exist_ok=True)
    config_path = config_dir / "pip_config.json"
    default_config = {
        "enable_pip_install": True,
        "mirror": "https://pypi.tuna.tsinghua.edu.cn/simple",
        "backup_mirror": "https://mirrors.ustc.edu.cn/pypi/simple",
    }
    if not config_path.exists():
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        return default_config
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logger.exception("读取pip配置失败，使用默认配置")
        return default_config


### 依赖安装相关 ###


def find_local_wheels_dir():
    """查找本地deps目录中的whl文件"""
    project_root = Path(project_root_dir)
    deps_dir = project_root / "deps"

    if deps_dir.exists() and any(deps_dir.glob("*.whl")):
        whl_count = len(list(deps_dir.glob("*.whl")))
        logger.info(f"发现本地deps目录包含 {whl_count} 个 whl 文件")
        return deps_dir

    logger.debug("未找到deps目录或目录中无 whl 文件")
    return None


def _run_pip_command(cmd_args: list, operation_name: str) -> bool:
    """
    运行pip命令并处理输出
    
    Args:
        cmd_args: 要运行的命令列表
        operation_name: 操作名称，用于日志记录
        
    Returns:
        bool: 命令是否成功执行
    """
    # 验证命令参数
    if not cmd_args or not isinstance(cmd_args, list) or len(cmd_args) < 1:
        logger.error(f"{operation_name} 命令无效: {cmd_args}")
        return False
        
    # 检查命令路径是否有效
    import shutil
    cmd_path = cmd_args[0]
    if not os.path.isfile(cmd_path) and not shutil.which(cmd_path):
        logger.error(f"{operation_name} 无法找到命令: {cmd_path}")
        return False
    
    try:
        logger.info(f"开始 {operation_name}")
        logger.debug(f"执行命令: {' '.join(cmd_args)}")
        
        # 创建进程时增加超时控制和环境变量处理
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"  # 确保输出编码一致性
        
        process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 将stderr重定向到stdout
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,  # 行缓冲
            universal_newlines=True,
            env=env
        )

        # 收集所有输出用于日志记录
        all_output = []
        error_lines = []

        try:
            # 实时读取并显示输出
            while process.poll() is None:
                line = process.stdout.readline()
                if not line:
                    break
                    
                line = line.rstrip("\n\r")
                if line.strip():  # 只显示非空行
                    print(line)  # 实时显示到终端
                    all_output.append(line)
                    
                    # 收集错误信息行
                    if any(keyword in line.lower() for keyword in ["error", "failed", "exception", "traceback"]):
                        error_lines.append(line)
        except KeyboardInterrupt:
            logger.warning(f"{operation_name} 被用户中断")
            process.terminate()
            try:
                process.wait(timeout=5)  # 等待进程终止
            except subprocess.TimeoutExpired:
                process.kill()
            return False
        except Exception as read_error:
            logger.error(f"读取命令输出时出错: {read_error}")
            try:
                process.terminate()
                process.wait(timeout=3)
            except:
                pass
            return False

        # 等待进程结束
        try:
            return_code = process.wait(timeout=300)  # 设置5分钟超时
        except subprocess.TimeoutExpired:
            logger.error(f"{operation_name} 超时，强制终止")
            process.kill()
            return False

        # 记录完整输出到日志，但限制大小
        if all_output:
            # 限制日志大小，避免日志过大
            output_to_log = all_output[-50:] if len(all_output) > 50 else all_output
            full_output = "\n".join(output_to_log)
            logger.debug(f"{operation_name} 输出:\n{full_output}")
            
            # 如果有错误行，单独记录
            if error_lines:
                error_output = "\n".join(error_lines)
                logger.debug(f"{operation_name} 错误信息:\n{error_output}")

        if return_code == 0:
            logger.info(f"{operation_name} 完成")
            return True
        else:
            logger.error(f"{operation_name} 时出错。返回码: {return_code}")
            return False

    except FileNotFoundError:
        logger.error(f"{operation_name} 找不到命令: {cmd_args[0]}")
        return False
    except PermissionError:
        logger.error(f"{operation_name} 没有执行权限: {cmd_args[0]}")
        return False
    except Exception as e:
        logger.exception(f"{operation_name} 时发生未知异常: {e}")
        return False


def install_requirements(req_file="requirements.txt", pip_config=None) -> bool:
    """
    安装项目依赖
    
    Args:
        req_file: 依赖文件名称
        pip_config: pip配置字典
        
    Returns:
        bool: 安装是否成功
    """
    # 参数验证
    if not req_file or not isinstance(req_file, str):
        logger.error(f"无效的依赖文件名: {req_file}")
        return False
    
    if pip_config is None:
        pip_config = {}
    elif not isinstance(pip_config, dict):
        logger.error(f"无效的pip配置类型: {type(pip_config)}")
        return False
    
    # 确保路径处理正确
    try:
        req_path = Path(project_root_dir) / req_file  # 确保相对于项目根目录
        req_path = req_path.resolve()  # 获取绝对路径
    except Exception as e:
        logger.error(f"解析依赖文件路径时出错: {e}")
        return False
    
    if not req_path.exists():
        logger.error(f"{req_file} 文件不存在于 {req_path}，无法安装依赖")
        return False
    
    try:
        # 检查文件是否可读
        with open(req_path, 'r', encoding='utf-8') as f:
            # 简单验证文件内容
            content = f.read(1024)  # 只读取前1024字节验证
            if not content.strip():
                logger.warning(f"{req_file} 文件为空，跳过依赖安装")
                return True
    except Exception as e:
        logger.error(f"读取依赖文件时出错: {e}")
        return False

    # 查找本地deps目录
    deps_dir = find_local_wheels_dir()
    if deps_dir:
        logger.info(f"使用本地 whl 文件安装，目录: {deps_dir}")

        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-U",
            "-r",
            str(req_path),
            "--no-warn-script-location",
        ]
        
        # 只在非Windows系统上使用 --break-system-packages
        if not sys.platform.startswith("win"):
            cmd.append("--break-system-packages")
            
        cmd.extend([
            "--find-links",
            str(deps_dir),  # pip会优先使用这里的文件
            "--no-index",  # 禁止在线索引
        ])

        if _run_pip_command(cmd, f"从本地deps安装依赖"):
            return True
        else:
            logger.warning("本地deps安装失败，回退到在线安装")

    # 回退到在线安装
    primary_mirror = pip_config.get("mirror", "")
    backup_mirror = pip_config.get("backup_mirror", "")

    if primary_mirror:
        # 验证镜像URL格式
        if not (primary_mirror.startswith("http://") or primary_mirror.startswith("https://")):
            logger.warning(f"镜像源URL格式可能无效: {primary_mirror}")
            
        # 使用主镜像源，只添加一个备用源避免冲突
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-U",
            "-r",
            str(req_path),
            "--no-warn-script-location",
        ]
        
        # 只在非Windows系统上使用 --break-system-packages
        if not sys.platform.startswith("win"):
            cmd.append("--break-system-packages")
            
        cmd.extend(["-i", primary_mirror])

        # 只添加一个备用源
        if backup_mirror and backup_mirror != primary_mirror:  # 避免重复镜像源
            # 验证备用镜像URL格式
            if not (backup_mirror.startswith("http://") or backup_mirror.startswith("https://")):
                logger.warning(f"备用镜像源URL格式可能无效: {backup_mirror}")
            
            cmd.extend(["--extra-index-url", backup_mirror])
            logger.info(f"使用主源 {primary_mirror} 和备用源 {backup_mirror} 安装依赖")
        else:
            logger.info(f"使用主源 {primary_mirror} 安装依赖")

        if _run_pip_command(cmd, f"从 {req_path.name} 安装依赖"):
            return True
        else:
            logger.error("在线安装失败")
            return False
    else:
        # 如果没有配置主镜像源，使用pip的本地全局配置
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-U",
            "-r",
            str(req_path),
            "--no-warn-script-location",
        ]
        
        # 只在非Windows系统上使用 --break-system-packages
        if not sys.platform.startswith("win"):
            cmd.append("--break-system-packages")

        if _run_pip_command(cmd, f"从 {req_path.name} 安装依赖 (本地全局配置)"):
            return True
        else:
            logger.error("使用pip本地全局配置安装失败")
            return False


def check_and_install_dependencies():
    """检查并安装项目依赖"""
    pip_config = read_pip_config()
    enable_pip_install = pip_config.get("enable_pip_install", True)

    logger.info(f"启用 pip 安装依赖: {enable_pip_install}")

    if enable_pip_install:
        logger.info("开始安装/更新依赖")
        if install_requirements(pip_config=pip_config):
            logger.info("依赖检查和安装完成")
        else:
            logger.warning("依赖安装失败，程序可能无法正常运行")
    else:
        logger.info("Pip 依赖安装已禁用，跳过依赖安装")


### 核心业务 ###


def agent(is_dev_mode=False):
    """
    Agent主函数，负责启动Agent服务器并处理异常情况
    
    Args:
        is_dev_mode: 是否启用开发模式
    """
    # 先导入必要的基础模块
    import sys
    import importlib
    
    # 导入日志模块并设置日志级别
    from utils import logger
    
    if is_dev_mode:
        from utils.logger import change_console_level
        change_console_level("DEBUG")
        logger.info("开发模式：日志等级已设置为DEBUG")
    
    try:
        # 导入项目所需的其他模块
        from maa.toolkit import Toolkit
        from maa.agent.agent_server import AgentServer
        import custom
        
        # 可选地重新加载utils模块以确保使用最新代码
        import utils
        importlib.reload(utils)
        
        logger.info("所有必要模块导入成功")
        
        # 初始化Toolkit
        logger.info("初始化MAA Toolkit...")
        Toolkit.init_option("./")
        
        # 验证命令行参数
        if len(sys.argv) < 2:
            error_msg = "缺少必要的 socket_id 参数"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        socket_id = sys.argv[-1]
        logger.info(f"socket_id: {socket_id}")
        
        # 启动Agent服务器
        logger.info("准备启动AgentServer...")
        AgentServer.start_up(socket_id)
        logger.info("AgentServer启动成功")
        
        # 等待服务器关闭
        logger.info("AgentServer运行中，等待关闭信号...")
        AgentServer.join()
        
    except ImportError as e:
        # 处理导入错误
        logger.error(f"导入模块失败: {e}")
        logger.error("建议：")
        logger.error("1. 检查Python环境是否正确配置")
        logger.error("2. 确保已安装所有依赖：pip install -r requirements.txt")
        logger.error("3. 检查MAA相关库是否正确安装")
        sys.exit(1)
    
    except ValueError as e:
        # 处理参数错误
        logger.error(f"参数错误: {e}")
        sys.exit(2)
    
    except KeyboardInterrupt:
        # 处理用户中断
        logger.info("用户中断操作")
        
    except Exception as e:
        # 处理其他所有异常
        logger.exception("Agent运行过程中发生未预期的异常")
        sys.exit(3)
    
    finally:
        # 确保资源清理
        try:
            # 尝试关闭AgentServer（如果已经启动）
            if 'AgentServer' in locals():
                logger.info("正在关闭AgentServer...")
                AgentServer.shut_down()
                logger.info("AgentServer已成功关闭")
        except Exception as cleanup_error:
            logger.error(f"关闭AgentServer时发生错误: {cleanup_error}")
    
    logger.info("Agent执行完毕")
    return 0


### 程序入口 ###


def main():
    """
    程序主入口函数
    """
    try:
        # 获取接口版本信息
        current_version = read_interface_version()
        if not current_version:
            current_version = "UNKNOWN"
            logger.warning("无法获取接口版本信息，使用默认值")
            
        is_dev_mode = current_version == "DEBUG"
        
        logger.info(f"当前版本: {current_version}, 开发模式: {is_dev_mode}")

        # 根据系统和开发模式决定是否使用虚拟环境
        # 对于Windows，默认也使用虚拟环境
        if sys.platform.startswith("linux") or sys.platform.startswith("win") or is_dev_mode:
            logger.debug(f"系统: {sys.platform}, 开发模式: {is_dev_mode}, 准备启动虚拟环境")
            ensure_venv_and_relaunch_if_needed()
        else:
            logger.info(f"在系统 {sys.platform} 上，跳过虚拟环境检查")

        # 检查并安装依赖
        check_and_install_dependencies()

        # 在开发模式下切换到assets目录
        if is_dev_mode:
            try:
                assets_dir = Path("./assets")
                if assets_dir.exists() and assets_dir.is_dir():
                    os.chdir(assets_dir)
                    logger.info(f"已切换工作目录: {os.getcwd()}")
                else:
                    logger.warning(f"assets目录不存在或不是有效目录: {assets_dir}")
            except Exception as e:
                logger.error(f"切换到assets目录时出错: {e}")
                # 不退出，继续运行程序

        # 调用agent函数并处理返回值
        exit_code = agent(is_dev_mode=is_dev_mode)
        logger.info(f"程序正常退出，退出码: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("用户中断程序执行")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"程序启动过程中发生未预期的异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
