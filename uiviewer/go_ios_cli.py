#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
go-ios命令封装模块
提供对go-ios命令的封装，方便在Python中使用
"""

import os
import json
import time
import subprocess
from typing import Dict, List, Optional, Union, Any

# 配置日志


class GoIOSError(Exception):
    """go-ios命令执行错误"""
    def __init__(self, message: str, cmd: str = "", stderr: str = ""):
        self.message = message
        self.cmd = cmd
        self.stderr = stderr
        super().__init__(f"{message}, cmd: {cmd}, stderr: {stderr}")


class SimulatorError(Exception):
    """模拟器操作异常类"""
    
    def __init__(self, message: str, cmd: str = "", stderr: str = ""):
        self.message = message
        self.cmd = cmd
        self.stderr = stderr
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.message} (cmd: {self.cmd}, stderr: {self.stderr})"


class GoIOS:
    """go-ios命令封装类"""
    
    @staticmethod
    def _run_command(cmd: List[str], check: bool = True, json_output: bool = True) -> Union[Dict, str]:
        """
        运行go-ios命令
        
        Args:
            cmd: 命令列表
            check: 是否检查命令执行状态
            json_output: 是否将输出解析为JSON
            
        Returns:
            Dict或str: 命令执行结果
            
        Raises:
            GoIOSError: 命令执行错误
        """
        try:
            # logger.debug(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=check
            )
            
            if result.returncode != 0:
                raise GoIOSError(
                    f"命令执行失败，返回码: {result.returncode}",
                    cmd=' '.join(cmd),
                    stderr=result.stderr
                )
            
            if json_output:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    # logger.warning(f"无法解析JSON输出: {result.stdout}")
                    return result.stdout
            else:
                return result.stdout
        except subprocess.CalledProcessError as e:
            raise GoIOSError(
                f"命令执行异常: {e}",
                cmd=' '.join(cmd),
                stderr=e.stderr if hasattr(e, 'stderr') else ""
            )
        except Exception as e:
            raise GoIOSError(f"执行命令时发生错误: {e}", cmd=' '.join(cmd))
    
    @classmethod
    def get_version(cls) -> Dict:
        """
        获取go-ios版本信息
        
        Returns:
            Dict: 版本信息
        """
        return cls._run_command(["ios", "version"])
    
    @classmethod
    def list_devices(cls, details: bool = False) -> Dict:
        """
        获取设备列表
        
        Args:
            details: 是否获取详细信息
            
        Returns:
            Dict: 设备列表
        """
        cmd = ["ios", "list"]
        if details:
            cmd.append("--details")
        return cls._run_command(cmd)
    
    @classmethod
    def get_device_info(cls, udid: str) -> Dict:
        """
        获取设备信息
        
        Args:
            udid: 设备UDID
            
        Returns:
            Dict: 设备信息
        """
        return cls._run_command(["ios", "info", f"--udid={udid}"])
    
    @classmethod
    def ios_tunnel_status(cls,udid:str=None) -> Dict:
        """
        启动隧道
        
        Returns:
            Dict: 隧道信息
        """
        cmd = ["ios", "tunnel", "ls"]
        if udid:
            cmd.append(f"--udid={udid}")
        return cls._run_command(cmd)
    
    @classmethod
    def forward_port(cls, host_port: int, device_port: int, udid: Optional[str] = None) -> Dict:
        """
        端口转发
        
        Args:
            host_port: 主机端口
            device_port: 设备端口
            udid: 设备UDID，如果为None则使用第一个可用设备
            
        Returns:
            Dict: 转发结果
        """
        cmd = ["ios", "forward", f"{host_port}", f"{device_port}"]
        if udid:
            cmd.append(f"--udid={udid}")
        return cls._run_command(cmd)
    
    @classmethod
    def remove_forward(cls, host_port: int, udid: Optional[str] = None) -> Dict:
        """
        移除端口转发
        
        Args:
            host_port: 主机端口
            udid: 设备UDID，如果为None则使用第一个可用设备
            
        Returns:
            Dict: 移除结果
        """
        cmd = ["ios", "forward", "--remove", f"{host_port}"]
        if udid:
            cmd.append(f"--udid={udid}")
        return cls._run_command(cmd)
    
    @classmethod
    def list_forward(cls, udid: Optional[str] = None) -> Dict:
        """
        列出端口转发
        
        Args:
            udid: 设备UDID，如果为None则使用第一个可用设备
            
        Returns:
            Dict: 转发列表
        """
        cmd = ["ios", "forward", "--list"]
        if udid:
            cmd.append(f"--udid={udid}")
        return cls._run_command(cmd)
    
    @classmethod
    def run_wda(cls, bundle_id: str, test_runner_bundle_id: str, 
                xctestconfig: str = "WebDriverAgentRunner.xctest",
                udid: Optional[str] = None) -> subprocess.Popen:
        """
        运行WDA（非阻塞方式）
        
        Args:
            bundle_id: WDA Bundle ID
            test_runner_bundle_id: Test Runner Bundle ID
            xctestconfig: XCTest配置
            udid: 设备UDID，如果为None则使用第一个可用设备
            
        Returns:
            subprocess.Popen: 进程对象，可用于后续管理
        """
        cmd = [
            "ios", "runwda", 
            f"--bundleid={bundle_id}", 
            f"--testrunnerbundleid={test_runner_bundle_id}",
            f"--xctestconfig={xctestconfig}"
        ]
        if udid:
            cmd.append(f"--udid={udid}")
        
        # logger.debug(f"执行命令: {' '.join(cmd)}")
        try:
            # 使用Popen非阻塞方式启动WDA
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # 等待一小段时间，确保进程启动
            time.sleep(1)
            
            # 检查进程是否已经终止（表示启动失败）
            if process.poll() is not None:
                stderr = process.stderr.read() if process.stderr else ""
                raise GoIOSError(
                    f"WDA启动失败，进程已终止，返回码: {process.returncode}",
                    cmd=' '.join(cmd),
                    stderr=stderr
                )
            
            # logger.info("WDA启动成功（非阻塞）")
            return process
        except Exception as e:
            if not isinstance(e, GoIOSError):
                e = GoIOSError(f"启动WDA时发生错误: {e}", cmd=' '.join(cmd))
            raise e
    
    @classmethod
    def list_apps(cls, udid:str, is_system:bool=False, is_all:bool=False) -> Dict:
        """
        获取应用列表
        
        Args:
            udid: 设备UDID，如果为None则使用第一个可用设备
            
        Returns:
            Dict: 应用列表
        """
        cmd = ["ios", "apps", '--list']
        if is_system:
            cmd.append("--system")
        if is_all:
            cmd.append("--all")
        cmd.append(f"--udid={udid}")

        return cls._run_command(cmd)
    
    @classmethod
    def install_app(cls, ipa_path: str, udid: Optional[str] = None) -> Dict:
        """
        安装应用
        
        Args:
            ipa_path: IPA文件路径
            udid: 设备UDID，如果为None则使用第一个可用设备
            
        Returns:
            Dict: 安装结果
        """
        cmd = ["ios", "install", ipa_path]
        if udid:
            cmd.append(f"--udid={udid}")
        return cls._run_command(cmd)
    
    @classmethod
    def uninstall_app(cls, bundle_id: str, udid: Optional[str] = None) -> Dict:
        """
        卸载应用
        
        Args:
            bundle_id: 应用Bundle ID
            udid: 设备UDID，如果为None则使用第一个可用设备
            
        Returns:
            Dict: 卸载结果
        """
        cmd = ["ios", "uninstall", bundle_id]
        if udid:
            cmd.append(f"--udid={udid}")
        return cls._run_command(cmd)
    
    @classmethod
    def launch_app(cls, bundle_id: str, udid: Optional[str] = None) -> Dict:
        """
        启动应用
        
        Args:
            bundle_id: 应用Bundle ID
            udid: 设备UDID，如果为None则使用第一个可用设备
            
        Returns:
            Dict: 启动结果
        """
        cmd = ["ios", "launch", bundle_id]
        if udid:
            cmd.append(f"--udid={udid}")
        return cls._run_command(cmd)
    
    @classmethod
    def terminate_app(cls, bundle_id: str, udid: Optional[str] = None) -> Dict:
        """
        终止应用
        
        Args:
            bundle_id: 应用Bundle ID
            udid: 设备UDID，如果为None则使用第一个可用设备
            
        Returns:
            Dict: 终止结果
        """
        cmd = ["ios", "kill", bundle_id]
        if udid:
            cmd.append(f"--udid={udid}")
        return cls._run_command(cmd)
    
    @classmethod
    def get_app_state(cls, bundle_id: str, udid: Optional[str] = None) -> Dict:
        """
        获取应用状态
        
        Args:
            bundle_id: 应用Bundle ID
            udid: 设备UDID，如果为None则使用第一个可用设备
            
        Returns:
            Dict: 应用状态
        """
        cmd = ["ios", "appstate", bundle_id]
        if udid:
            cmd.append(f"--udid={udid}")
        return cls._run_command(cmd)
    
    @classmethod
    def take_screenshot(cls, output_path: Optional[str], udid: Optional[str] = None) -> str:
        """
        截图
        
        Args:
            output_path: 输出路径，如果为None则使用临时文件
            udid: 设备UDID，如果为None则使用第一个可用设备
            
        Returns:
            str: 截图路径
        """
        if not output_path:
            raise ValueError("输出路径不能为空")
        
        cmd = ["ios", "screenshot", f"--output={output_path}"]
        if udid:
            cmd.append(f"--udid={udid}")
        
        try:
            cls._run_command(cmd, json_output=False)
            return output_path
        except Exception as e:
            # logger.error(f"截图失败: {e}")
            return ""


class Simulator:
    """iOS模拟器操作类，基于xcrun simctl命令"""
    
    @classmethod
    def _run_command(cls, cmd: List[str], json_output: bool = True, check: bool = True) -> Union[Dict, str]:
        """
        运行命令并返回结果
        
        Args:
            cmd: 命令
            json_output: 是否解析JSON输出
            check: 是否检查返回码
            
        Returns:
            Dict或str: 命令输出
        """
        # logger.debug(f"执行命令: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)
            if result.returncode != 0:
                raise SimulatorError(
                    f"命令执行失败，返回码: {result.returncode}",
                    cmd=' '.join(cmd),
                    stderr=result.stderr
                )
            
            if json_output:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    raise SimulatorError(
                        f"解析JSON输出失败",
                        cmd=' '.join(cmd),
                        stderr=result.stderr
                    )
            else:
                return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise SimulatorError(
                f"命令执行失败: {e}",
                cmd=' '.join(cmd),
                stderr=e.stderr if hasattr(e, 'stderr') else ""
            )
        except Exception as e:
            if not isinstance(e, SimulatorError):
                raise SimulatorError(f"命令执行出错: {e}", cmd=' '.join(cmd))
            raise e
    
    @classmethod
    def list_devices(cls) -> Dict:
        """
        列出所有可用的模拟器
        
        Returns:
            Dict: 模拟器列表
        """
        cmd = ["xcrun", "simctl", "list", "devices", "--json"]
        return cls._run_command(cmd)
    
    @classmethod
    def boot_device(cls, udid: str) -> str:
        """
        启动指定的模拟器
        
        Args:
            udid: 模拟器UDID
            
        Returns:
            str: 启动结果
        """
        cmd = ["xcrun", "simctl", "boot", udid]
        return cls._run_command(cmd, json_output=False)
    
    @classmethod
    def shutdown_device(cls, udid: str) -> str:
        """
        关闭指定的模拟器
        
        Args:
            udid: 模拟器UDID
            
        Returns:
            str: 关闭结果
        """
        cmd = ["xcrun", "simctl", "shutdown", udid]
        return cls._run_command(cmd, json_output=False)
    
    @classmethod
    def erase_device(cls, udid: str) -> str:
        """
        擦除指定模拟器的所有内容
        
        Args:
            udid: 模拟器UDID
            
        Returns:
            str: 擦除结果
        """
        cmd = ["xcrun", "simctl", "erase", udid]
        return cls._run_command(cmd, json_output=False)
    
    @classmethod
    def create_device(cls, name: str, device_type: str, runtime: str) -> str:
        """
        创建新的模拟器
        
        Args:
            name: 模拟器名称
            device_type: 设备类型，例如 "iPhone 12"
            runtime: 运行时版本，例如 "iOS-14-0"
            
        Returns:
            str: 创建结果，包含新模拟器的UDID
        """
        cmd = ["xcrun", "simctl", "create", name, device_type, runtime]
        return cls._run_command(cmd, json_output=False)
    
    @classmethod
    def delete_device(cls, udid: str) -> str:
        """
        删除指定的模拟器
        
        Args:
            udid: 模拟器UDID
            
        Returns:
            str: 删除结果
        """
        cmd = ["xcrun", "simctl", "delete", udid]
        return cls._run_command(cmd, json_output=False)
    
    @classmethod
    def list_runtimes(cls) -> Dict:
        """
        列出所有可用的模拟器运行时
        
        Returns:
            Dict: 运行时列表
        """
        cmd = ["xcrun", "simctl", "list", "runtimes", "--json"]
        return cls._run_command(cmd)
    
    @classmethod
    def list_device_types(cls) -> Dict:
        """
        列出所有可用的模拟器设备类型
        
        Returns:
            Dict: 设备类型列表
        """
        cmd = ["xcrun", "simctl", "list", "devicetypes", "--json"]
        return cls._run_command(cmd)
    
    @classmethod
    def install_app(cls, udid: str, app_path: str) -> str:
        """
        在模拟器上安装应用
        
        Args:
            udid: 模拟器UDID
            app_path: 应用路径
            
        Returns:
            str: 安装结果
        """
        cmd = ["xcrun", "simctl", "install", udid, app_path]
        return cls._run_command(cmd, json_output=False)
    
    @classmethod
    def uninstall_app(cls, udid: str, bundle_id: str) -> str:
        """
        从模拟器卸载应用
        
        Args:
            udid: 模拟器UDID
            bundle_id: 应用Bundle ID
            
        Returns:
            str: 卸载结果
        """
        cmd = ["xcrun", "simctl", "uninstall", udid, bundle_id]
        return cls._run_command(cmd, json_output=False)
    
    @classmethod
    def launch_app(cls, udid: str, bundle_id: str) -> str:
        """
        在模拟器上启动应用
        
        Args:
            udid: 模拟器UDID
            bundle_id: 应用Bundle ID
            
        Returns:
            str: 启动结果
        """
        cmd = ["xcrun", "simctl", "launch", udid, bundle_id]
        return cls._run_command(cmd, json_output=False)
    
    @classmethod
    def terminate_app(cls, udid: str, bundle_id: str) -> str:
        """
        终止模拟器上的应用
        
        Args:
            udid: 模拟器UDID
            bundle_id: 应用Bundle ID
            
        Returns:
            str: 终止结果
        """
        cmd = ["xcrun", "simctl", "terminate", udid, bundle_id]
        return cls._run_command(cmd, json_output=False)
    
    @classmethod
    def take_screenshot(cls, udid: str, output_path: str) -> str:
        """
        模拟器截图
        
        Args:
            udid: 模拟器UDID
            output_path: 输出路径
            
        Returns:
            str: 截图结果
        """
        cmd = ["xcrun", "simctl", "io", udid, "screenshot", output_path]
        return cls._run_command(cmd, json_output=False)
    
    @classmethod
    def open_url(cls, udid: str, url: str) -> str:
        """
        在模拟器上打开URL
        
        Args:
            udid: 模拟器UDID
            url: URL
            
        Returns:
            str: 打开结果
        """
        cmd = ["xcrun", "simctl", "openurl", udid, url]
        return cls._run_command(cmd, json_output=False)
    
    @classmethod
    def get_app_container(cls, udid: str, bundle_id: str, container_type: str = "app") -> str:
        """
        获取应用容器路径
        
        Args:
            udid: 模拟器UDID
            bundle_id: 应用Bundle ID
            container_type: 容器类型，可选值: app, data, groups
            
        Returns:
            str: 容器路径
        """
        cmd = ["xcrun", "simctl", "get_app_container", udid, bundle_id, container_type]
        return cls._run_command(cmd, json_output=False)


if __name__ == "__main__":
    # # 测试代码
    devices = GoIOS.list_devices()
    print(devices)