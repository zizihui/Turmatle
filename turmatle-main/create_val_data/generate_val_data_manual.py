"""
测试数据生成脚本 - 手动版
仅运行create_fine_data中的生成脚本，修改输出路径到val_datas
注意：不包含create_data中的基础数据生成
"""

import os
import sys
import subprocess
import tempfile
import re

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAL_DATA_DIR = os.path.join(PROJECT_ROOT, 'val_datas')
IMAGES_DIR = os.path.join(VAL_DATA_DIR, 'images')

def create_val_directories():
    """创建验证数据目录"""
    os.makedirs(VAL_DATA_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"创建验证数据目录: {VAL_DATA_DIR}")

def modify_script_content(script_path, max_images=10):
    """
    修改脚本内容，替换路径和生成数量
    
    Args:
        script_path: 原始脚本路径
        max_images: 最大生成图片数量
    
    Returns:
        修改后的脚本内容
    """
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修改路径 - 仅处理create_fine_data脚本
    if 'create_fine_data' in script_path:
        # 修改create_fine_data脚本的路径
        content = content.replace(
            "IMG_DIR = os.path.join(project_root, 'datas_finetuning/",
            f"IMG_DIR = os.path.join(project_root, 'val_datas/images/"
        )
        content = content.replace(
            "LABEL_FILE = os.path.join(project_root, 'datas_finetuning/",
            f"LABEL_FILE = os.path.join(project_root, 'val_datas/"
        )
    
    # 更精确的路径替换 - 处理具体的子目录
    content = re.sub(
        r"IMG_DIR = os\.path\.join\(project_root, '[^']*images[^']*'\)",
        f"IMG_DIR = os.path.join(project_root, 'val_datas/images')",
        content
    )
    
    # 为每个脚本生成唯一的标签文件名
    script_name = os.path.basename(script_path).replace('.py', '')
    unique_label_file = f"val_datas/labels_{script_name}.txt"
    content = re.sub(
        r"LABEL_FILE = os\.path\.join\(project_root, '[^']*labels[^']*'\)",
        f"LABEL_FILE = os.path.join(project_root, '{unique_label_file}')",
        content
    )
    
    # 修改生成数量
    replacements = [
        (r'samples_per_group\s*=\s*\d+', f'samples_per_group = {max_images}'),
        (r'samples_per_subcase1\s*=\s*\d+', f'samples_per_subcase1 = {max_images}'),
        (r'samples_per_subcase2\s*=\s*\d+', f'samples_per_subcase2 = {max_images}'),
        (r'samples_per_subcase\s*=\s*\d+', f'samples_per_subcase = {max_images}'),
        (r'samples_per_case\s*=\s*\d+', f'samples_per_case = {max_images}'),
        (r'samples_per_type\s*=\s*\d+', f'samples_per_type = {max_images}'),
        (r'samples_per_category\s*=\s*\d+', f'samples_per_category = {max_images}'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # 替换循环中的数量 - 更精确的匹配，只替换使用samples_per_*变量的循环
    loop_replacements = [
        (r'for _ in range\(samples_per_\w+\):', f'for _ in range({max_images}):'),
        (r'for j in range\(samples_per_\w+\):', f'for j in range({max_images}):'),
        (r'for i in range\(samples_per_\w+\):', f'for i in range({max_images}):'),
    ]
    
    for pattern, replacement in loop_replacements:
        content = re.sub(pattern, replacement, content)
    
    return content

def run_script(script_path, max_images=10):
    """运行单个脚本"""
    script_name = os.path.basename(script_path)
    print(f"\n正在处理: {script_name}")
    
    try:
        # 修改脚本内容
        modified_content = modify_script_content(script_path, max_images)
        
        # 创建临时脚本文件
        temp_script_path = os.path.join(VAL_DATA_DIR, f"temp_{script_name}")
        
        with open(temp_script_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        # 运行脚本
        print(f"运行修改后的脚本...")
        result = subprocess.run(
            [sys.executable, temp_script_path],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print(f"✅ {script_name} 运行成功")
            if result.stdout.strip():
                print(f"输出: {result.stdout.strip()}")
        else:
            print(f"❌ {script_name} 运行失败")
            if result.stderr.strip():
                print(f"错误: {result.stderr.strip()}")
        
        # 清理临时文件
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)
            
    except subprocess.TimeoutExpired:
        print(f"❌ {script_name} 运行超时")
    except Exception as e:
        print(f"❌ 运行 {script_name} 时出错: {e}")

def get_all_scripts():
    """获取所有生成脚本 - 仅create_fine_data"""
    scripts = []
    
    # 只使用create_fine_data脚本
    create_fine_data_dir = os.path.join(PROJECT_ROOT, 'create_fine_data')
    if os.path.exists(create_fine_data_dir):
        for file in sorted(os.listdir(create_fine_data_dir)):
            if file.startswith('generation_') and file.endswith('.py'):
                scripts.append(os.path.join(create_fine_data_dir, file))
    
    return scripts

def merge_labels():
    """合并所有标签文件"""
    print("\n=== 合并标签文件 ===")
    
    # 查找所有标签文件
    label_files = []
    for root, dirs, files in os.walk(VAL_DATA_DIR):
        for file in files:
            if file.endswith('.txt') and file != 'labels copy 2.txt':
                label_files.append(os.path.join(root, file))
    
    # 合并到主标签文件
    main_label_file = os.path.join(VAL_DATA_DIR, 'labels copy 2.txt')
    total_lines = 0
    
    with open(main_label_file, 'w', encoding='utf-8') as main_f:
        for label_file in label_files:
            if os.path.exists(label_file):
                with open(label_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line:
                            main_f.write(line + '\n')
                            total_lines += 1
                print(f"合并: {os.path.basename(label_file)} ({len(lines)} 行)")
    
    print(f"总共合并 {total_lines} 行标签数据")

def main():
    """主函数"""
    print("开始生成验证数据...")
    print(f"项目根目录: {PROJECT_ROOT}")
    
    # 创建目录
    create_val_directories()
    
    # 获取所有脚本
    scripts = get_all_scripts()
    print(f"找到 {len(scripts)} 个生成脚本")
    
    # 逐个运行脚本
    for i, script_path in enumerate(scripts, 1):
        print(f"\n[{i}/{len(scripts)}] 处理脚本...")
        run_script(script_path, max_images=10)
    
    # 合并标签文件
    merge_labels()
    
    # 统计结果
    print("\n=== 生成完成 ===")
    if os.path.exists(IMAGES_DIR):
        image_files = [f for f in os.listdir(IMAGES_DIR) if f.endswith('.png')]
        print(f"总共生成图片: {len(image_files)} 张")
        print(f"图片保存在: {IMAGES_DIR}")
    
    main_label_file = os.path.join(VAL_DATA_DIR, 'labels copy 2.txt')
    if os.path.exists(main_label_file):
        with open(main_label_file, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
        print(f"标签文件: {main_label_file} ({lines} 行)")

if __name__ == "__main__":
    main()
