#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建模型预测对比可视化网格（左侧竖排导航栏 + 紧凑布局）
Compare predictions: Ground Truth vs Pre-trained vs Fine-tuned
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import os
import matplotlib

# 设置字体（支持中文）
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# ============================================================================
# 📊 配置数据
# ============================================================================
rows_config = [
    ('Line + Circle', 'lc_special2'),
    ('Triangle + Rectangle', 'tr_special16'),
    ('Two Horizontal/Vertical Lines', 'two_l_xy8'),
    ('Two Rectangles', 'two_r17'),
    ('Two Lines', 'two_l18'),
    ('Line + Triangle', 'lt_special18'),
    ('Two Triangles', 'two_t4'),
    ('Two Circles', 'two_c21'),
]

column_titles = ['Ground Truth', 'Pre-trained Model', 'Fine-tuned Model']
OUTPUT_FILE = 'model_comparison_grid_leftnav_vertical.png'

# ============================================================================
# 🖼️ 创建对比网格
# ============================================================================
def create_comparison_grid():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    n_rows = len(rows_config)
    n_cols = 3

    # 紧凑布局
    fig = plt.figure(figsize=(13, 3.3 * n_rows))

    gs = fig.add_gridspec(
        n_rows, n_cols + 1,
        width_ratios=[0.6, 3, 3, 3],   # 左栏略窄
        hspace=0.03, wspace=0.03,     # 左右间距更小
        left=0.03, right=0.97, top=0.96, bottom=0.04
    )

    # 添加顶部列标题
    for col_idx, title in enumerate(column_titles):
        ax = fig.add_subplot(gs[0, col_idx + 1])
        ax.text(
            0.5, 1.08, title,           # 标题更靠近图片
            ha='center', va='center',
            fontsize=15, fontweight='bold',
            transform=ax.transAxes
        )
        ax.axis('off')

    # 绘制每一行
    for row_idx, (category_label, image_prefix) in enumerate(rows_config):
        files = [
            f'{image_prefix}.png',
            f'{image_prefix}_predict_p.png',
            f'{image_prefix}_predict_f.png'
        ]

        # 左侧竖排导航栏
        ax_label = fig.add_subplot(gs[row_idx, 0])
        ax_label.text(
            1.0, 0.5, category_label,
            ha='right', va='center',
            fontsize=11, fontweight='bold',
            rotation=90,           # 竖排文字
            transform=ax_label.transAxes
        )
        ax_label.axis('off')
        

        # 每个模型的图像
        for j, img_file in enumerate(files):
            ax = fig.add_subplot(gs[row_idx, j + 1])
            if os.path.exists(img_file):
                try:
                    img = Image.open(img_file)
                    ax.imshow(img)
                except Exception as e:
                    ax.text(0.5, 0.5, f'Error\n{img_file}', ha='center', va='center', fontsize=9)
                    print(f"⚠️ Error loading {img_file}: {e}")
            else:
                ax.text(0.5, 0.5, f'Missing\n{img_file}', ha='center', va='center', color='red', fontsize=9)
                print(f"⚠️ File not found: {img_file}")

            ax.axis('off')
            # 边框
            rect = patches.Rectangle(
                (0, 0), 1, 1,
                linewidth=1.2, edgecolor='black', facecolor='none',
                transform=ax.transAxes
            )
            ax.add_patch(rect)

    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Comparison grid saved to: {OUTPUT_FILE}")
    plt.close()

# ============================================================================
# 🧭 主函数
# ============================================================================
def main():
    print("📊 Creating vertical navigation comparison visualization...")
    print(f"📁 Working directory: {os.getcwd()}")
    create_comparison_grid()
    print(f"\n🎉 Visualization complete! Saved as {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
