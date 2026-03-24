#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复val_datas中labels.txt文件中的路径分隔符
将反斜杠替换为正斜杠
"""

import os
import argparse


def fix_paths_in_labels(input_file, output_file=None):
    """
    修复labels.txt文件中的路径分隔符
    
    Args:
        input_file: 输入的labels.txt文件路径
        output_file: 输出的labels.txt文件路径，如果为None则覆盖原文件
    """
    if output_file is None:
        output_file = input_file
    
    print(f"正在处理文件: {input_file}")
    
    # 读取文件内容
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    fixed_count = 0
    
    for line_num, line in enumerate(lines, 1):
        original_line = line
        # 替换反斜杠为正斜杠
        fixed_line = line.replace('\\', '/')
        
        if fixed_line != original_line:
            fixed_count += 1
            print(f"第{line_num}行修复: {original_line.strip()} -> {fixed_line.strip()}")
        
        fixed_lines.append(fixed_line)
    
    # 写入修复后的内容
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"处理完成！共修复 {fixed_count} 行")
    print(f"输出文件: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='修复labels.txt文件中的路径分隔符')
    parser.add_argument('--input', type=str, default='val_datas/labels.txt', 
                       help='输入的labels.txt文件路径 (默认: val_datas/labels.txt)')
    parser.add_argument('--output', type=str, default=None, 
                       help='输出的labels.txt文件路径，如果为None则覆盖原文件')
    parser.add_argument('--backup', action='store_true', 
                       help='是否备份原文件')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        return
    
    # 备份原文件
    if args.backup:
        backup_file = args.input + '.backup'
        import shutil
        shutil.copy2(args.input, backup_file)
        print(f"已备份原文件到: {backup_file}")
    
    # 修复路径分隔符
    fix_paths_in_labels(args.input, args.output)


if __name__ == '__main__':
    main()
