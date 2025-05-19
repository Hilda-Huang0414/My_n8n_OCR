#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
from pathlib import Path


def format_python_files_windows(directory):
    """
    在Windows系统中规范化所有Python代码文件
    """
    # 获取所有Python文件（包括子目录）
    python_files = list(Path(directory).rglob("*.py"))

    print(f"找到 {len(python_files)} 个Python文件需要规范化...")

    for file_path in python_files:
        file_path = str(file_path)
        print(f"\n正在处理: {file_path}")

        try:
            # 1. 使用isort规范导入顺序
            subprocess.run(["isort", file_path], shell=True, check=True)
            print("  ✓ 导入顺序已规范化")

            # 2. 使用autopep8自动格式化
            subprocess.run(
                ["autopep8", "--in-place", "--aggressive", file_path],
                shell=True,
                check=True,
            )
            print("  ✓ 代码格式已调整")

            # 3. 使用black统一代码风格
            subprocess.run(["black", file_path], shell=True, check=True)
            print("  ✓ 代码风格已统一")

            # 4. 使用flake8检查代码问题
            flake8_result = subprocess.run(
                ["flake8", file_path], shell=True, capture_output=True, text=True
            )
            if flake8_result.returncode == 0:
                print("  ✓ 代码检查通过")
            else:
                print(f"  ! 代码检查发现问题:\n{flake8_result.stdout}")

        except subprocess.CalledProcessError as e:
            print(f"  × 处理文件时出错: {e}")

    print("\n所有文件处理完成!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Windows系统Python代码规范化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
                python format_python_win.py                  # 规范化当前目录
                python format_python_win.py C:\\my_project   # 规范化指定目录
                """,
    )

    parser.add_argument(
        "directory",
        help="要规范化的目录路径(默认为当前目录)",
        nargs="?",
        default=os.getcwd(),
    )

    args = parser.parse_args()

    # 确保路径是Windows格式
    target_dir = os.path.normpath(args.directory)

    if not os.path.isdir(target_dir):
        print(f"错误: 目录不存在 - {target_dir}")
        exit(1)

    print(f"开始规范化目录: {target_dir}")
    format_python_files_windows(target_dir)
