#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动运行所有模型预测
先运行微调模型预测，再运行预训练模型预测
"""

import os
import sys
import subprocess
import time
import argparse


def run_script(script_path, script_name, max_images=None, debug=False):
    """运行预测脚本"""
    print("\n" + "=" * 80)
    print(f"🚀 开始运行: {script_name}")
    print("=" * 80)
    
    # 构建命令
    cmd = [sys.executable, script_path]
    
    if max_images:
        cmd.extend(['--max-images', str(max_images)])
    
    if debug:
        cmd.append('--debug')
    
    print(f"📝 执行命令: {' '.join(cmd)}")
    print()
    
    start_time = time.time()
    
    try:
        # 运行脚本
        result = subprocess.run(
            cmd,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ {script_name} 完成! 用时: {elapsed_time:.1f}s")
        return True
        
    except subprocess.CalledProcessError as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ {script_name} 失败! 用时: {elapsed_time:.1f}s")
        print(f"错误码: {e.returncode}")
        return False
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ {script_name} 出错! 用时: {elapsed_time:.1f}s")
        print(f"错误: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='自动运行所有模型预测')
    parser.add_argument('--max-images', type=int, default=None,
                       help='最大预测图片数量 (默认: 全部)')
    parser.add_argument('--quick', action='store_true',
                       help='快速测试模式 (只预测前10张图片)')
    parser.add_argument('--debug', action='store_true',
                       help='调试模式，显示详细的p2t输出信息')
    parser.add_argument('--finetune-only', action='store_true',
                       help='只运行微调模型预测')
    parser.add_argument('--pretrain-only', action='store_true',
                       help='只运行预训练模型预测')
    
    args = parser.parse_args()
    
    # 快速测试模式
    if args.quick:
        args.max_images = 10
        print("🚀 快速测试模式: 只预测前10张图片")
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 定义脚本路径
    finetune_script = os.path.join(project_root, 'val_finetune_model_result', 'batch_predict_finetune.py')
    pretrain_script = os.path.join(project_root, 'val_model_result', 'batch_predict_pretrain.py')
    
    print("\n" + "🎯" * 40)
    print("🎯 批量预测所有模型")
    print("🎯" * 40)
    print(f"📁 项目根目录: {project_root}")
    print(f"📊 最大图片数: {args.max_images or '全部'}")
    print(f"🐛 调试模式: {'开启' if args.debug else '关闭'}")
    
    total_start_time = time.time()
    results = {}
    
    # 运行微调模型预测
    if not args.pretrain_only:
        if os.path.exists(finetune_script):
            results['微调模型'] = run_script(
                finetune_script, 
                '微调模型预测 (new_models_finetuning)', 
                args.max_images, 
                args.debug
            )
        else:
            print(f"\n⚠️  微调模型脚本不存在: {finetune_script}")
            results['微调模型'] = False
    
    # 运行预训练模型预测
    if not args.finetune_only:
        if os.path.exists(pretrain_script):
            results['预训练模型'] = run_script(
                pretrain_script, 
                '预训练模型预测 (new_models)', 
                args.max_images, 
                args.debug
            )
        else:
            print(f"\n⚠️  预训练模型脚本不存在: {pretrain_script}")
            results['预训练模型'] = False
    
    # 总结
    total_elapsed_time = time.time() - total_start_time
    
    print("\n" + "=" * 80)
    print("🎉 所有预测任务完成!")
    print("=" * 80)
    print(f"⏱️  总用时: {total_elapsed_time:.1f}s")
    print()
    print("📊 运行结果:")
    for model_name, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {status} - {model_name}")
    
    print()
    print("📄 输出文件:")
    if '微调模型' in results:
        finetune_output = os.path.join(project_root, 'val_finetune_model_result', 'predict_finetune_labels.txt')
        print(f"  微调模型: {finetune_output}")
    if '预训练模型' in results:
        pretrain_output = os.path.join(project_root, 'val_model_result', 'predict_pretrain_labels.txt')
        print(f"  预训练模型: {pretrain_output}")
    
    # 返回退出码
    if all(results.values()):
        print("\n✅ 所有任务成功完成!")
        sys.exit(0)
    else:
        print("\n⚠️  部分任务失败，请检查错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()

