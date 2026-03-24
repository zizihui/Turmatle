#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型对比脚本 - 预训练模型 vs 微调模型
Compare Pre-trained Model vs Fine-tuned Model
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# ============================================================================
# 📊 数据输入区域 - 直接在这里修改数据
# ============================================================================

# 每个类别的数据：类别名称: [总数, 预训练模型错误数, 微调模型错误数]
category_comparison = {
    'Circle + Rect': [60, 7, 7],
    'Circle + Triangle': [70, 2, 2],
    'Line + Circle': [20, 4, 1],
    'Line + Rect': [20, 4, 9],
    'Line + Triangle': [20, 11, 7],
    'Triangle + Rect': [30, 10, 4],
    'Two Circles': [30, 30, 23],
    'Two Lines': [30, 30, 10],
    'Two Horizontal or Vertical Lines': [30, 30, 7],
    'Two Rects': [20, 20, 6],
    'Two Triangles': [40, 40, 18],
}

OUTPUT_DIR = 'visualization_compare'

# ============================================================================
# 计算统计数据
# ============================================================================

def calculate_comparison_stats(data):
    """计算对比统计数据"""
    stats = {}
    
    pretrain_total = 0
    pretrain_correct = 0
    pretrain_wrong = 0
    
    finetune_total = 0
    finetune_correct = 0
    finetune_wrong = 0
    
    for category, (total, pretrain_errors, finetune_errors) in data.items():
        pretrain_correct_count = total - pretrain_errors
        finetune_correct_count = total - finetune_errors
        
        pretrain_acc = (pretrain_correct_count / total * 100) if total > 0 else 0
        finetune_acc = (finetune_correct_count / total * 100) if total > 0 else 0
        
        improvement = finetune_acc - pretrain_acc
        
        stats[category] = {
            'total': total,
            'pretrain_correct': pretrain_correct_count,
            'pretrain_wrong': pretrain_errors,
            'pretrain_accuracy': pretrain_acc,
            'finetune_correct': finetune_correct_count,
            'finetune_wrong': finetune_errors,
            'finetune_accuracy': finetune_acc,
            'improvement': improvement
        }
        
        pretrain_total += total
        pretrain_correct += pretrain_correct_count
        pretrain_wrong += pretrain_errors
        
        finetune_total += total
        finetune_correct += finetune_correct_count
        finetune_wrong += finetune_errors
    
    overall_pretrain_acc = (pretrain_correct / pretrain_total * 100) if pretrain_total > 0 else 0
    overall_finetune_acc = (finetune_correct / finetune_total * 100) if finetune_total > 0 else 0
    overall_improvement = overall_finetune_acc - overall_pretrain_acc
    
    return stats, {
        'pretrain': {'total': pretrain_total, 'correct': pretrain_correct, 'wrong': pretrain_wrong, 'accuracy': overall_pretrain_acc},
        'finetune': {'total': finetune_total, 'correct': finetune_correct, 'wrong': finetune_wrong, 'accuracy': overall_finetune_acc},
        'improvement': overall_improvement
    }


def print_comparison_stats(stats, overall):
    """打印对比统计结果"""
    print("\n" + "=" * 120)
    print("Model Comparison: Pre-trained vs Fine-tuned")
    print("=" * 120)
    
    print(f"\n{'Category':<30} {'Total':<8} {'Pretrain Acc':<15} {'Finetune Acc':<15} {'Improvement':<12}")
    print("-" * 120)
    
    # 按改进程度排序
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['improvement'], reverse=True)
    
    for category, data in sorted_stats:
        improvement_str = f"{data['improvement']:+.1f}%"
        print(f"{category:<30} "
              f"{data['total']:<8} "
              f"{data['pretrain_accuracy']:>6.1f}%{'':<7} "
              f"{data['finetune_accuracy']:>6.1f}%{'':<7} "
              f"{improvement_str:>11}")
    
    print("-" * 120)
    print(f"{'Overall':<30} "
          f"{overall['pretrain']['total']:<8} "
          f"{overall['pretrain']['accuracy']:>6.1f}%{'':<7} "
          f"{overall['finetune']['accuracy']:>6.1f}%{'':<7} "
          f"{overall['improvement']:+.1f}%{'':<6}")
    print("=" * 120)


def plot_side_by_side_comparison(stats, output_dir):
    """绘制并排对比柱状图 - 竖向"""
    # 按微调模型准确率排序
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['finetune_accuracy'], reverse=True)
    
    categories = [cat for cat, _ in sorted_stats]
    pretrain_accs = [data['pretrain_accuracy'] for _, data in sorted_stats]
    finetune_accs = [data['finetune_accuracy'] for _, data in sorted_stats]
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    x_pos = np.arange(len(categories))
    bar_width = 0.35
    
    # 绘制两组柱状图
    bars1 = ax.bar(x_pos - bar_width/2, pretrain_accs, bar_width, 
                   label='Pre-trained Model', color='#64B5F6', alpha=0.8, edgecolor='black', linewidth=1)
    bars2 = ax.bar(x_pos + bar_width/2, finetune_accs, bar_width, 
                   label='Fine-tuned Model', color='#81C784', alpha=0.8, edgecolor='black', linewidth=1)
    
    # 添加数值标签
    for bar, acc in zip(bars1, pretrain_accs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{acc:.1f}%',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    for bar, acc in zip(bars2, finetune_accs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{acc:.1f}%',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.set_xlabel('Category', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('Accuracy Comparison by Category: Pre-trained vs Fine-tuned Model', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, 110)
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 添加参考线
    ax.axhline(y=70, color='green', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.axhline(y=50, color='orange', linestyle='--', alpha=0.5, linewidth=1.5)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'model_comparison_side_by_side.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def plot_improvement_chart(stats, output_dir):
    """绘制改进程度图"""
    # 按改进程度排序
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['improvement'], reverse=True)
    
    categories = [cat for cat, _ in sorted_stats]
    improvements = [data['improvement'] for _, data in sorted_stats]
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # 根据改进程度设置颜色
    colors = ['#81C784' if imp > 0 else '#EF9A9A' if imp < 0 else '#FFD54F' for imp in improvements]
    bars = ax.barh(categories, improvements, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # 添加数值标签
    for bar, imp in zip(bars, improvements):
        width = bar.get_width()
        x_pos = width + 1 if width >= 0 else width - 1
        h_align = 'left' if width >= 0 else 'right'
        ax.text(x_pos, bar.get_y() + bar.get_height()/2,
                f'{imp:+.1f}%',
                ha=h_align, va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Accuracy Improvement (%)', fontsize=12, fontweight='bold')
    ax.set_title('Fine-tuned Model Improvement by Category', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.axvline(x=0, color='black', linestyle='-', linewidth=2)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'model_improvement.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def plot_overall_comparison_bar(overall, output_dir):
    """绘制整体对比柱状图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    models = ['Pre-trained Model', 'Fine-tuned Model']
    accuracies = [overall['pretrain']['accuracy'], overall['finetune']['accuracy']]
    colors = ['#64B5F6', '#81C784']
    
    bars = ax.bar(models, accuracies, color=colors, alpha=0.8, edgecolor='black', linewidth=2, width=0.6)
    
    # 添加数值标签
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{acc:.2f}%',
                ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # 添加改进箭头
    if overall['improvement'] > 0:
        ax.annotate('', xy=(1, overall['finetune']['accuracy']), 
                   xytext=(0, overall['pretrain']['accuracy']),
                   arrowprops=dict(arrowstyle='->', lw=2, color='green'))
        ax.text(0.5, (overall['pretrain']['accuracy'] + overall['finetune']['accuracy'])/2,
                f'+{overall["improvement"]:.2f}%',
                ha='center', va='center', fontsize=12, fontweight='bold', 
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    ax.set_ylabel('Overall Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('Overall Model Performance Comparison', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, 110)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'overall_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def main():
    """主函数"""
    print("📊 Comparing Pre-trained vs Fine-tuned Models...")
    
    # 创建输出文件夹
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"📁 Output directory: {OUTPUT_DIR}")
    
    # 计算对比统计
    stats, overall = calculate_comparison_stats(category_comparison)
    
    # 打印统计结果
    print_comparison_stats(stats, overall)
    
    # 绘制图表
    print("\n📈 Generating comparison chart...")
    plot_side_by_side_comparison(stats, OUTPUT_DIR)
    
    print(f"\n🎉 Comparison complete!")
    print(f"📁 Chart saved to: {OUTPUT_DIR}/")
    print(f"\n💡 Tip: To update data, edit the 'category_comparison' dictionary at the top of this script.")


if __name__ == '__main__':
    main()

