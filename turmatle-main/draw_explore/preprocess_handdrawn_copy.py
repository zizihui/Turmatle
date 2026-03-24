# 手绘图形预处理脚本 
import cv2
import numpy as np
import os
import sys

def preprocess_handdrawn_image_optimized(input_path, output_path=None):
    """
    优化版预处理：生成更实的手绘线条
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径
    
    返回:
        处理后的图片路径
    """
    # 读取图片
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError(f"无法读取图片: {input_path}")
    
    print(f"原始图片尺寸: {img.shape}")
    
    # 1. 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print("✓ 灰度化完成")
    
    # 2. 温和去噪（保留更多细节）
    # 使用非局部均值去噪，比双边滤波更好地保留边缘
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)
    print("✓ 温和去噪完成")
    
    # 3. 优化版自适应阈值（生成更实的线条）
    binary = cv2.adaptiveThreshold(
        denoised, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        blockSize=9,   # 调整参数使线条更连续
        C=1           # 减小常数避免断线
    )
    print("✓ 优化二值化完成（线条更实）")
    
    # 4. 精细的形态学操作 - 轻微调整以增强线条连续性
    # 使用稍大的核进行闭运算，填充微小间隙
    kernel_close = np.ones((2, 2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close, iterations=1)
    print("✓ 增强版闭运算完成")
    
    # 轻微开运算：去除孤立噪点但不影响主要线条
    kernel_open = np.ones((1, 1), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_open, iterations=1)
    print("✓ 精细开运算完成")
    
    # 5. 线条处理 - 改为轻微加粗而不是细化
    if should_thicken_lines(binary):
        kernel_dilate = np.ones((2, 2), np.uint8)
        binary = cv2.dilate(binary, kernel_dilate, iterations=1)
        print("✓ 线条轻微加粗完成")
    
    # 6. 确保背景是白色，线条是黑色
    black_pixels = np.sum(binary == 0)
    white_pixels = np.sum(binary == 255)
    if black_pixels > white_pixels:
        binary = cv2.bitwise_not(binary)
        print("✓ 颜色反转完成")
    
    # 7. 智能对比度调整（保护细线条）
    # 使用直方图分析来调整对比度
    binary = smart_contrast_adjustment(binary)
    print("✓ 智能对比度调整完成")
    
    # 8. 高质量尺寸调整
    TARGET_SIZE = 1000
    h, w = binary.shape
    
    # 保持宽高比的同时调整到目标尺寸
    scale_factor = TARGET_SIZE / max(h, w)
    new_w = int(w * scale_factor)
    new_h = int(h * scale_factor)
    
    # 使用高质量插值方法
    resized = cv2.resize(binary, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    
    # 创建目标尺寸的画布并居中放置图像
    canvas = np.ones((TARGET_SIZE, TARGET_SIZE), dtype=np.uint8) * 255
    y_offset = (TARGET_SIZE - new_h) // 2
    x_offset = (TARGET_SIZE - new_w) // 2
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    binary = canvas
    print(f"✓ 高质量尺寸调整: {h}x{w} -> {TARGET_SIZE}x{TARGET_SIZE}")
    
    # 8.5 新增：最终线条增强
    binary = enhance_line_connectivity(binary)
    print("✓ 最终线条增强完成")
    
    # 9. 最终质量检查
    binary = final_quality_check(binary)
    print("✓ 最终质量检查完成")
    
    # 10. 保存处理后的图片
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_optimized{ext}"
    
    cv2.imwrite(output_path, binary)
    print(f"✓ 保存优化后的图片: {output_path}")
    
    return output_path

def should_thicken_lines(binary_img, thinness_threshold=3):
    """
    判断是否需要加粗线条（替换原来的细化判断）
    基于线条平均厚度决定是否进行加粗
    """
    # 计算线条的平均厚度（简化方法）
    edges = cv2.Canny(binary_img, 50, 150)
    line_thickness = np.sum(binary_img == 0) / (np.sum(edges > 0) + 1e-6)
    
    # 如果线条较细，则进行加粗
    return line_thickness < thinness_threshold

def enhance_line_connectivity(binary_img):
    """
    增强线条连通性，使线条更实
    """
    # 使用形态学梯度增强线条边缘
    kernel = np.ones((2, 2), np.uint8)
    gradient = cv2.morphologyEx(binary_img, cv2.MORPH_GRADIENT, kernel)
    
    # 将梯度结果与原图结合，增强线条连续性
    # 这里使用更保守的方法，避免过度加粗
    result = binary_img.copy()
    
    # 只在原线条边缘处进行轻微增强
    edges = cv2.Canny(binary_img, 50, 150)
    result[edges > 0] = 0  # 确保边缘为黑色
    
    return result

def smart_contrast_adjustment(binary_img):
    """
    智能对比度调整，保护细线条不被过度处理
    """
    # 分析直方图，确定合适的阈值
    hist = cv2.calcHist([binary_img], [0], None, [256], [0, 256])
    
    # 找到主要的前景和背景峰值
    foreground_intensity = np.argmax(hist[:128])  # 黑色区域
    background_intensity = np.argmax(hist[128:]) + 128  # 白色区域
    
    # 如果对比度已经很好，不做过多处理
    if background_intensity - foreground_intensity > 200:
        return binary_img
    
    # 适度增强对比度
    alpha = 1.2  # 对比度增强系数
    beta = -10   # 亮度调整
    
    adjusted = cv2.convertScaleAbs(binary_img, alpha=alpha, beta=beta)
    _, result = cv2.threshold(adjusted, 200, 255, cv2.THRESH_BINARY)
    
    return result

def final_quality_check(binary_img):
    """
    最终质量检查和处理
    """
    # 去除可能的小噪点（面积很小的连通区域）
    n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        cv2.bitwise_not(binary_img), connectivity=8
    )
    
    # 如果噪点不多，直接返回
    if n_labels <= 2:
        return binary_img
    
    # 去除小面积区域
    min_area = 50  # 最小面积阈值
    clean_img = binary_img.copy()
    
    for i in range(1, n_labels):  # 跳过背景
        if stats[i, cv2.CC_STAT_AREA] < min_area:
            # 填充小区域为背景色（白色）
            clean_img[labels == i] = 255
    
    return clean_img

def compare_results(original_path, processed_path, optimized_path):
    """
    比较原图、原处理结果和优化结果
    """
    original = cv2.imread(original_path)
    processed = cv2.imread(processed_path)
    optimized = cv2.imread(optimized_path)
    
    # 可以在这里添加可视化比较代码
    print("\n" + "="*60)
    print("📊 处理结果对比")
    print("="*60)
    print(f"原图尺寸: {original.shape}")
    print(f"原处理结果尺寸: {processed.shape}")
    print(f"优化结果尺寸: {optimized.shape}")
    
    # 计算线条厚度的变化
    orig_black = np.sum(original == 0)
    proc_black = np.sum(processed == 0)
    opt_black = np.sum(optimized == 0)
    
    print(f"原图黑色像素: {orig_black}")
    print(f"原处理黑色像素: {proc_black} (变化: {((proc_black-orig_black)/orig_black*100):+.1f}%)")
    print(f"优化处理黑色像素: {opt_black} (变化: {((opt_black-orig_black)/orig_black*100):+.1f}%)")

def main_optimized():
    """批量处理 images/ 目录下的所有图片，输出为 {name}_p.png"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')

    if not os.path.exists(images_dir):
        print(f"错误: 目录不存在 {images_dir}")
        sys.exit(1)

    input_exts = ('.jpg', '.jpeg', '.png', '.bmp')
    input_files = sorted([
        f for f in os.listdir(images_dir)
        if os.path.splitext(f)[1].lower() in input_exts and '_p' not in f
    ])

    if not input_files:
        print(f"在 {images_dir} 中未找到待处理的图片")
        sys.exit(0)

    print(f"找到 {len(input_files)} 张待处理图片\n")

    for filename in input_files:
        input_path = os.path.join(images_dir, filename)
        base, _ = os.path.splitext(filename)
        output_path = os.path.join(images_dir, f"{base}_p.png")

        print(f"\n{'='*60}")
        print(f"处理: {filename} -> {base}_p.png")
        print(f"{'='*60}\n")

        try:
            preprocess_handdrawn_image_optimized(input_path, output_path)
            print(f"✅ 完成: {output_path}")
        except Exception as e:
            print(f"❌ 处理失败 {filename}: {e}")

    print(f"\n{'='*60}")
    print(f"全部处理完成！共 {len(input_files)} 张")
    print(f"{'='*60}")

if __name__ == "__main__":
    main_optimized()