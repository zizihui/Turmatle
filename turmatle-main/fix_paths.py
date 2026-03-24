"""
修复datas和datas_fintuning中tsv文件中的路径分隔符
将反斜杠替换为正斜杠
"""

import os
import argparse


def fix_paths_in_tsv(input_file, output_file=None):
    """
    修复tsv文件中的路径分隔符
    
    Args:
        input_file: 输入的tsv文件路径
        output_file: 输出的tsv文件路径，如果为None则覆盖原文件
    """
    if output_file is None:
        output_file = input_file
    
    print(f"正在处理文件: {input_file}")
    
    # 读取文件内容
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    fixed_count = 0
    
    for line in lines:
        original_line = line
        # 替换反斜杠为正斜杠
        fixed_line = line.replace('\\', '/')
        
        if fixed_line != original_line:
            fixed_count += 1
            print(f"修复: {original_line.strip()} -> {fixed_line.strip()}")
        
        fixed_lines.append(fixed_line)
    
    # 写入修复后的内容
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"处理完成！共修复 {fixed_count} 行")
    print(f"输出文件: {output_file}")

#改地址
def main():
    parser = argparse.ArgumentParser(description='修复tsv文件中的路径分隔符')
    parser.add_argument('--train', type=str, default='datas_finetuning/finetuning-trocr-index/train.tsv', 
                       help='训练集tsv文件路径 (默认: datas_finetuning/finetuning-trocr-index/train.tsv)')
    parser.add_argument('--dev', type=str, default='datas_finetuning/finetuning-trocr-index/dev.tsv', 
                       help='验证集tsv文件路径 (默认: datas_finetuning/finetuning-trocr-index/dev.tsv)')
    parser.add_argument('--backup', action='store_true', 
                       help='是否备份原文件')
    
    args = parser.parse_args()
    
    # 处理训练集
    if os.path.exists(args.train):
        if args.backup:
            backup_file = args.train + '.backup'
            os.system(f'cp "{args.train}" "{backup_file}"')
            print(f"已备份训练集到: {backup_file}")
        
        fix_paths_in_tsv(args.train)
    else:
        print(f"警告: 训练集文件不存在: {args.train}")
    
    print("-" * 50)
    
    # 处理验证集
    if os.path.exists(args.dev):
        if args.backup:
            backup_file = args.dev + '.backup'
            os.system(f'cp "{args.dev}" "{backup_file}"')
            print(f"已备份验证集到: {backup_file}")
        
        fix_paths_in_tsv(args.dev)
    else:
        print(f"警告: 验证集文件不存在: {args.dev}")


if __name__ == '__main__':
    main()
