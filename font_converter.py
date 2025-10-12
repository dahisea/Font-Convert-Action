#!/usr/bin/env python3
"""
字体格式转换脚本
支持常见字体格式之间的转换
"""

import os
import sys
import argparse
import requests
from fontTools.ttLib import TTFont
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FontConverter:
    def __init__(self):
        self.supported_formats = {
            'ttf': True,
            'otf': True,
            'woff': True,
            'woff2': True
        }
    
    def download_font(self, url, output_path):
        """从URL下载字体文件"""
        try:
            logger.info(f"正在下载字体: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"字体下载完成: {output_path}")
            return True
        except Exception as e:
            logger.error(f"下载字体失败: {e}")
            return False
    
    def detect_font_format(self, file_path):
        """检测字体文件格式"""
        _, ext = os.path.splitext(file_path)
        return ext.lower().lstrip('.')
    
    def convert_font(self, input_path, output_path, output_format):
        """转换字体格式"""
        try:
            logger.info(f"开始转换字体: {input_path} -> {output_path}")
            
            # 读取字体文件
            font = TTFont(input_path)
            
            # 根据目标格式进行转换
            if output_format == 'woff2':
                font.flavor = 'woff2'
            elif output_format == 'woff':
                font.flavor = 'woff'
            elif output_format == 'ttf':
                # TTF是默认格式，不需要特殊处理
                pass
            elif output_format == 'otf':
                # OTF通常也是TTF格式，但可以设置一些OTF特性
                pass
            
            # 保存转换后的字体
            font.save(output_path)
            font.close()
            
            logger.info(f"字体转换完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"字体转换失败: {e}")
            return False
    
    def validate_font(self, file_path):
        """验证字体文件是否有效"""
        try:
            font = TTFont(file_path)
            valid = len(font.getGlyphOrder()) > 0
            font.close()
            return valid
        except:
            return False

def main():
    parser = argparse.ArgumentParser(description='字体格式转换工具')
    parser.add_argument('--url', required=True, help='字体文件URL')
    parser.add_argument('--output-format', required=True, choices=['ttf', 'otf', 'woff', 'woff2'], 
                       help='目标格式')
    parser.add_argument('--output-name', help='输出文件名（不含扩展名）')
    
    args = parser.parse_args()
    
    converter = FontConverter()
    
    # 临时文件路径
    temp_dir = "temp_fonts"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 生成输入文件名
    input_filename = os.path.basename(args.url).split('?')[0]  # 移除URL参数
    input_path = os.path.join(temp_dir, input_filename)
    
    # 下载字体
    if not converter.download_font(args.url, input_path):
        sys.exit(1)
    
    # 验证下载的字体
    if not converter.validate_font(input_path):
        logger.error("下载的字体文件无效")
        sys.exit(1)
    
    # 确定输出文件名
    if args.output_name:
        output_filename = f"{args.output_name}.{args.output_format}"
    else:
        base_name = os.path.splitext(input_filename)[0]
        output_filename = f"{base_name}.{args.output_format}"
    
    output_path = os.path.join(temp_dir, output_filename)
    
    # 转换字体
    if not converter.convert_font(input_path, output_path, args.output_format):
        sys.exit(1)
    
    # 验证转换后的字体
    if not converter.validate_font(output_path):
        logger.error("转换后的字体文件无效")
        sys.exit(1)
    
    # 输出文件信息
    input_size = os.path.getsize(input_path)
    output_size = os.path.getsize(output_path)
    
    logger.info(f"转换完成!")
    logger.info(f"输入文件: {input_filename} ({input_size} bytes)")
    logger.info(f"输出文件: {output_filename} ({output_size} bytes)")
    logger.info(f"压缩率: {(1 - output_size/input_size) * 100:.1f}%")
    
    # 将输出文件移动到工作目录
    final_output_path = output_filename
    os.rename(output_path, final_output_path)
    
    # 清理临时文件
    import shutil
    shutil.rmtree(temp_dir)
    
    print(f"::set-output name=converted_file::{final_output_path}")
    print(f"::set-output name=input_size::{input_size}")
    print(f"::set-output name=output_size::{output_size}")

if __name__ == "__main__":
    main()