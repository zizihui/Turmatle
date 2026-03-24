#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化预训练模型和微调模型的准确率对比
"""

import os
import re
import argparse
import matplotlib.pyplot as plt
import matplotlib
from typing import Dict, Tuple

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False


def parse_accuracy_file(file_path: str) -> Dict[str, float]:
    """
    解析准确率结果文件
    返回: {
        'total': 总数,
        'correct': 正确数,
        'wrong': 错误数,
        'missing': 缺失数,
        'accuracy': 准确率
    }
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取数据
    total_match = re.search(r'总图片数:\s*(\d+)', content)
    correct_match = re.search(r'✅\s*正确:\s*(\d+)\s*\(([^)]+)%\)', content)
    wrong_match = re.search(r'❌\s*错误:\s*(\d+)\s*\(([^)]+)%\)', content)
    missing_match = re.search(r'⚠️\s*缺失:\s*(\d+)\s*\(([^)]+)%\)', content)
    accuracy_match = re.search(r'🎯\s*准确率:\s*([^%]+)%', content)
    
    result = {
        'total': int(total_match.group(1)) if total_match else 0,
        'correct': int(correct_match.group(1)) if correct_match else 0,
        'correct_pct': float(correct_match.group(2)) if correct_match else 0.0,
        'wrong': int(wrong_match.group(1)) if wrong_match else 0,
        'wrong_pct': float(wrong_match.group(2)) if wrong_match else 0.0,
        'missing': int(missing_match.group(1)) if missing_match else 0,
        'missing_pct': float(missing_match.group(2)) if missing_match else 0.0,
        'accuracy': float(accuracy_match.group(1)) if accuracy_match else 0.0,
    }
    
    return result


def plot_accuracy_comparison(pretrain_data: Dict, finetune_data: Dict, output_dir: str):
    """
    绘制准确率对比图
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 准确率柱状图对比
    fig, ax = plt.subplots(figsize=(10, 6))
    
    models = ['Pre-trained Model', 'Fine-tuned Model']
    accuracies = [pretrain_data['accuracy'], finetune_data['accuracy']]
    colors = ['#81C784', '#64B5F6']  # 淡绿色和淡蓝色
    
    bars = ax.bar(models, accuracies, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # 添加数值标签
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{acc:.2f}%',
                ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('Pre-trained Model vs Fine-tuned Model - Accuracy Comparison', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '1_accuracy_comparison.png'), dpi=300, bbox_inches='tight')
    print(f"✅ 已保存: {os.path.join(output_dir, '1_accuracy_comparison.png')}")
    plt.close()
    
    # 2. 正确/错误/缺失数量堆叠柱状图
    fig, ax = plt.subplots(figsize=(10, 6))
    
    correct_counts = [pretrain_data['correct'], finetune_data['correct']]
    wrong_counts = [pretrain_data['wrong'], finetune_data['wrong']]
    missing_counts = [pretrain_data['missing'], finetune_data['missing']]
    
    x = range(len(models))
    width = 0.5
    
    bars1 = ax.bar(x, correct_counts, width, label='Correct', color='#81C784', alpha=0.8)  # 淡绿色
    bars2 = ax.bar(x, wrong_counts, width, bottom=correct_counts, label='Wrong', color='#EF9A9A', alpha=0.8)  # 淡红色
    bars3 = ax.bar(x, missing_counts, width, 
                   bottom=[c+w for c, w in zip(correct_counts, wrong_counts)],
                   label='Missing', color='#FFD54F', alpha=0.8)  # 淡黄色
    
    # 添加数值标签
    for i, (c, w, m) in enumerate(zip(correct_counts, wrong_counts, missing_counts)):
        # 正确数量
        ax.text(i, c/2, str(c), ha='center', va='center', fontsize=11, fontweight='bold', color='white')
        # 错误数量
        ax.text(i, c + w/2, str(w), ha='center', va='center', fontsize=11, fontweight='bold', color='white')
        # 缺失数量（如果有）
        if m > 0:
            ax.text(i, c + w + m/2, str(m), ha='center', va='center', fontsize=11, fontweight='bold')
    
    ax.set_ylabel('Number of Images', fontsize=12, fontweight='bold')
    ax.set_title('Pre-trained Model vs Fine-tuned Model - Prediction Result Distribution', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '2_result_distribution.png'), dpi=300, bbox_inches='tight')
    print(f"✅ 已保存: {os.path.join(output_dir, '2_result_distribution.png')}")
    plt.close()
    
    # 3. 饼图对比 - 预训练模型
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 预训练模型饼图
    sizes1 = [pretrain_data['correct'], pretrain_data['wrong'], pretrain_data['missing']]
    labels1 = [f"Correct\n{pretrain_data['correct']} ({pretrain_data['correct_pct']:.1f}%)",
               f"Wrong\n{pretrain_data['wrong']} ({pretrain_data['wrong_pct']:.1f}%)",
               f"Missing\n{pretrain_data['missing']} ({pretrain_data['missing_pct']:.1f}%)"]
    colors1 = ['#81C784', '#EF9A9A', '#FFD54F']  # 淡绿、淡红、淡黄
    explode1 = (0.05, 0, 0)
    
    wedges1, texts1, autotexts1 = ax1.pie(sizes1, explode=explode1, labels=labels1, colors=colors1,
                                            autopct='', startangle=90, textprops={'fontsize': 11})
    ax1.set_title(f'Pre-trained Model\nAccuracy: {pretrain_data["accuracy"]:.2f}%', 
                  fontsize=14, fontweight='bold', pad=20)
    
    # 微调模型饼图
    sizes2 = [finetune_data['correct'], finetune_data['wrong'], finetune_data['missing']]
    labels2 = [f"Correct\n{finetune_data['correct']} ({finetune_data['correct_pct']:.1f}%)",
               f"Wrong\n{finetune_data['wrong']} ({finetune_data['wrong_pct']:.1f}%)",
               f"Missing\n{finetune_data['missing']} ({finetune_data['missing_pct']:.1f}%)"]
    colors2 = ['#81C784', '#EF9A9A', '#FFD54F']  # 淡绿、淡红、淡黄
    explode2 = (0.05, 0, 0)
    
    wedges2, texts2, autotexts2 = ax2.pie(sizes2, explode=explode2, labels=labels2, colors=colors2,
                                            autopct='', startangle=90, textprops={'fontsize': 11})
    ax2.set_title(f'Fine-tuned Model\nAccuracy: {finetune_data["accuracy"]:.2f}%', 
                  fontsize=14, fontweight='bold', pad=20)
    
    plt.suptitle('Pre-trained Model vs Fine-tuned Model - Result Distribution Pie Chart', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '3_pie_chart_comparison.png'), dpi=300, bbox_inches='tight')
    print(f"✅ 已保存: {os.path.join(output_dir, '3_pie_chart_comparison.png')}")
    plt.close()
    
    # 4. 准确率差异图
    fig, ax = plt.subplots(figsize=(10, 6))
    
    diff = pretrain_data['accuracy'] - finetune_data['accuracy']
    color = '#81C784' if diff > 0 else '#EF9A9A'  # 淡绿色或淡红色
    
    ax.barh(['Accuracy Difference'], [diff], color=color, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
    
    # 添加数值标签
    ax.text(diff, 0, f'{diff:+.2f}%', ha='left' if diff > 0 else 'right', 
            va='center', fontsize=14, fontweight='bold', 
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='black'))
    
    ax.set_xlabel('Accuracy Difference (Pre-trained - Fine-tuned) %', fontsize=12, fontweight='bold')
    ax.set_title('Pre-trained Model vs Fine-tuned Model - Accuracy Difference', fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # 添加说明文本
    if diff > 0:
        ax.text(0.5, 0.95, f'Pre-trained model is {abs(diff):.2f}% higher', 
                transform=ax.transAxes, ha='center', va='top',
                fontsize=12, bbox=dict(boxstyle='round,pad=0.8', facecolor='#C8E6C9', alpha=0.8))  # 淡绿色背景
    else:
        ax.text(0.5, 0.95, f'Fine-tuned model is {abs(diff):.2f}% higher', 
                transform=ax.transAxes, ha='center', va='top',
                fontsize=12, bbox=dict(boxstyle='round,pad=0.8', facecolor='#FFCDD2', alpha=0.8))  # 淡红色背景
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '4_accuracy_difference.png'), dpi=300, bbox_inches='tight')
    print(f"✅ 已保存: {os.path.join(output_dir, '4_accuracy_difference.png')}")
    plt.close()
    
    # 5. 综合对比雷达图
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='polar')
    
    categories = ['Accuracy', 'Correct Rate', 'Error Rate', 'Missing Rate']
    N = len(categories)
    
    # 数据（注意：错误率和缺失率取反，这样越高越好）
    pretrain_values = [
        pretrain_data['accuracy'],
        pretrain_data['correct_pct'],
        100 - pretrain_data['wrong_pct'],  # 取反
        100 - pretrain_data['missing_pct']  # 取反
    ]
    
    finetune_values = [
        finetune_data['accuracy'],
        finetune_data['correct_pct'],
        100 - finetune_data['wrong_pct'],  # 取反
        100 - finetune_data['missing_pct']  # 取反
    ]
    
    # 计算角度
    angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
    pretrain_values += pretrain_values[:1]
    finetune_values += finetune_values[:1]
    angles += angles[:1]
    
    # 绘制
    ax.plot(angles, pretrain_values, 'o-', linewidth=2, label='Pre-trained Model', color='#81C784')  # 淡绿色
    ax.fill(angles, pretrain_values, alpha=0.25, color='#81C784')
    
    ax.plot(angles, finetune_values, 'o-', linewidth=2, label='Fine-tuned Model', color='#64B5F6')  # 淡蓝色
    ax.fill(angles, finetune_values, alpha=0.25, color='#64B5F6')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
    plt.title('Pre-trained Model vs Fine-tuned Model - Comprehensive Comparison Radar Chart', 
              fontsize=16, fontweight='bold', pad=30)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '5_radar_chart.png'), dpi=300, bbox_inches='tight')
    print(f"✅ 已保存: {os.path.join(output_dir, '5_radar_chart.png')}")
    plt.close()
    
    print("\n" + "=" * 80)
    print("🎉 所有可视化图表已生成完成！")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description='可视化预训练模型和微调模型的准确率对比')
    parser.add_argument('--pretrain-result', type=str, 
                       default='val_model_result/accuracy_copy_result 22.txt',
                       help='预训练模型准确率结果文件')
    parser.add_argument('--finetune-result', type=str, 
                       default='val_finetune_model_result/accuracy_finetune_copy_result 22.txt',
                       help='微调模型准确率结果文件')
    parser.add_argument('--output-dir', type=str, 
                       default='visualization_results_2',
                       help='输出目录')
    
    args = parser.parse_args()
    
    print("📊 开始生成可视化图表...")
    print("-" * 80)
    
    # 检查文件是否存在
    if not os.path.exists(args.pretrain_result):
        print(f"❌ 错误: 预训练模型结果文件不存在: {args.pretrain_result}")
        return
    
    if not os.path.exists(args.finetune_result):
        print(f"❌ 错误: 微调模型结果文件不存在: {args.finetune_result}")
        return
    
    # 解析数据
    print(f"📖 读取预训练模型结果: {args.pretrain_result}")
    pretrain_data = parse_accuracy_file(args.pretrain_result)
    print(f"   准确率: {pretrain_data['accuracy']:.2f}%")
    
    print(f"📖 读取微调模型结果: {args.finetune_result}")
    finetune_data = parse_accuracy_file(args.finetune_result)
    print(f"   准确率: {finetune_data['accuracy']:.2f}%")
    
    print("-" * 80)
    print(f"📁 输出目录: {args.output_dir}")
    print("-" * 80)
    
    # 生成图表
    plot_accuracy_comparison(pretrain_data, finetune_data, args.output_dir)


if __name__ == '__main__':
    main()

