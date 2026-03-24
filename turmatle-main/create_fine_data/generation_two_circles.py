"""生成微调数据集-特殊双图形中的两个圆"""
import os
import sys
import random
import turtle
import math
import ctypes
from PIL import Image

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from geom.base import Geom, Point
from geom.shapes import Circle

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas_finetuning/datas_two_circles/images_two_c')
LABEL_FILE = os.path.join(project_root, 'datas_finetuning/datas_two_circles/labels_two_c.txt')
os.makedirs(IMG_DIR, exist_ok=True)

def set_dpi_awareness():
    """确保Windows下的窗口大小一致性"""
    if sys.platform != 'win32':
        return
    try:
        # Windows 8.1+ (每显示器DPI感知)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            # Windows Vista/7
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

def circle_desc(idx, center, radius):
    """生成圆的描述"""
    return f'circle{idx} = Circle(Point({center[0]:.1f},{center[1]:.1f}), {radius:.1f})'

def calculate_distance(p1, p2):
    """计算两点之间的距离"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def is_circle_in_bounds(center, radius):
    """检查圆是否完全在画布边界内"""
    x, y = center
    return (-4.9 + radius <= x <= 4.9 - radius and 
            -4.9 + radius <= y <= 4.9 - radius)

def generate_containing_circles():
    """生成包含关系的两个圆（大圆包含小圆）"""
    while True:
        # 生成大圆（1位小数）
        large_radius = round(random.uniform(2.0, 4.5), 1)  # 大圆半径
        large_center_x = round(random.uniform(-4.9 + large_radius, 4.9 - large_radius), 1)
        large_center_y = round(random.uniform(-4.9 + large_radius, 4.9 - large_radius), 1)
        large_center = (large_center_x, large_center_y)
        
        # 生成小圆，确保完全在大圆内部（1位小数）
        small_radius = round(random.uniform(0.5, 3.0), 1)  # 小圆半径，确保有足够空间
        
        # 小圆圆心的可移动范围
        max_distance_from_large_center = large_radius - small_radius - 0.5  # 留出安全边距
        
        if max_distance_from_large_center > 0:
            # 在大圆内随机生成小圆圆心
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, max_distance_from_large_center)
            
            small_center_x = round(large_center_x + distance * math.cos(angle), 1)
            small_center_y = round(large_center_y + distance * math.sin(angle), 1)
            small_center = (small_center_x, small_center_y)
            
            # 验证包含关系：距离 + 小圆半径 < 大圆半径-0.5
            actual_distance = calculate_distance(large_center, small_center)
            if (actual_distance + small_radius < large_radius - 0.5 and  # 安全边距
                is_circle_in_bounds(small_center, small_radius)):
                return large_center, large_radius, small_center, small_radius

def generate_intersecting_circles():
    """生成相交关系的两个圆"""
    while True:
        # 生成第一个圆（1位小数）
        radius1 = round(random.uniform(1.0, 4.0), 1)
        center1_x = round(random.uniform(-4.9 + radius1, 4.9 - radius1), 1)
        center1_y = round(random.uniform(-4.9 + radius1, 4.9 - radius1), 1)
        center1 = (center1_x, center1_y)
        
        # 生成第二个圆（1位小数）
        radius2 = round(random.uniform(0.5, 4.5), 1)
        
        # 计算相交的距离范围：|r1 - r2|+0.5 ≤ d ≤ r1 + r2-0.5   
        min_distance = abs(radius1 - radius2) + 0.5  # 确保相交，不相切
        max_distance = radius1 + radius2 - 0.5       # 确保相交，不分离
        
        if min_distance < max_distance:
            # 随机选择距离
            target_distance = random.uniform(min_distance, max_distance)
            
            # 随机选择方向
            angle = random.uniform(0, 2 * math.pi)
            center2_x = round(center1_x + target_distance * math.cos(angle), 1)
            center2_y = round(center1_y + target_distance * math.sin(angle), 1)
            center2 = (center2_x, center2_y)
            
            # 检查第二个圆是否在边界内
            if is_circle_in_bounds(center2, radius2):
                # 验证相交关系
                actual_distance = calculate_distance(center1, center2)
                if abs(radius1 - radius2) + 0.5 <= actual_distance <= radius1 + radius2 - 0.5:
                    return center1, radius1, center2, radius2

def generate_tangent_circles():
    """生成相切关系的两个圆"""
    while True:
        # 生成第一个圆（1位小数）
        radius1 = round(random.uniform(0.5, 4.5), 1)
        center1_x = round(random.uniform(-4.9 + radius1, 4.9 - radius1), 1)
        center1_y = round(random.uniform(-4.9 + radius1, 4.9 - radius1), 1)
        center1 = (center1_x, center1_y)
        
        # 生成第二个圆（1位小数）
        radius2 = round(random.uniform(1.0, 3.0), 1)
        
        # 随机选择外切或内切
        tangent_type = random.choice(['external', 'internal'])
        
        if tangent_type == 'external':
            # 外切：距离 = r1 + r2
            target_distance = radius1 + radius2
        else:
            # 内切：距离 = |r1 - r2|，且确保不是同心圆
            if abs(radius1 - radius2) > 0.1:  # 避免同心圆
                target_distance = abs(radius1 - radius2)
            else:
                continue  # 重新生成
        
        # 随机选择方向
        angle = random.uniform(0, 2 * math.pi)
        center2_x = round(center1_x + target_distance * math.cos(angle), 1)
        center2_y = round(center1_y + target_distance * math.sin(angle), 1)
        center2 = (center2_x, center2_y)
        
        # 检查第二个圆是否在边界内
        if is_circle_in_bounds(center2, radius2):
            # 验证相切关系（允许小误差）
            actual_distance = calculate_distance(center1, center2)
            expected_distance = target_distance
            
            if abs(actual_distance - expected_distance) <= 1e-10:  # 允许小误差1e-10
                return center1, radius1, center2, radius2

def gen_two_circles(img_idx, generation_type):
    """生成两个圆的图像"""
    Geom.set_defaults(origin_x=0, origin_y=0, scale=100, speed=0, pensize=5)
    turtle.clearscreen()
    screen = turtle.Screen()
    # 强制Tk缩放为1.0（禁用额外的DPI缩放）
    try:
        tk_obj = getattr(screen, '_root', None)
        if tk_obj is not None:
            tk_obj.tk.call('tk', 'scaling', 1.0)
        else:
            tk_fallback = screen.cv._rootwindow
            tk_fallback.tk.call('tk', 'scaling', 1.0)
    except Exception:
        pass
    screen.setup(WIDTH, HEIGHT)
    screen.tracer(0)
    
    # 根据类型生成两个圆
    if generation_type == "containing":
        center1, radius1, center2, radius2 = generate_containing_circles()
    elif generation_type == "intersecting":
        center1, radius1, center2, radius2 = generate_intersecting_circles()
    else:  # tangent
        center1, radius1, center2, radius2 = generate_tangent_circles()
    
    # 创建并显示两个圆
    circle1 = Circle(Point(center1[0], center1[1]), radius1)
    circle2 = Circle(Point(center2[0], center2[1]), radius2)
    
    circle1.show()
    circle2.show()
    
    screen.update()
    
    # 保存图像
    ps_path = os.path.join(IMG_DIR, f'two_c{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'two_c{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())  # 自动去除白边
    img = img.resize((WIDTH, HEIGHT))  # 强制拉伸到目标尺寸
    img.save(png_path)
    os.remove(ps_path)
    
    # 生成描述
    descs = [
        circle_desc(1, center1, radius1),
        circle_desc(2, center2, radius2)
    ]
    
    return png_path, descs

def get_next_img_idx(img_dir):
    """获取下一个图像索引"""
    if not os.path.exists(img_dir):
        return 1
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('two_c') and f.endswith('.png'):
            try:
                num = int(f[5:-4])  # 去掉'two_c'前缀和'.png'后缀
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def main():
    """主函数"""
    # 设置DPI感知
    set_dpi_awareness()
    
    # 每种类型生成2500个样本
    samples_per_type = 2500
    start_img_idx = get_next_img_idx(IMG_DIR)
    
    generation_types = [
        ("containing", "一个圆包含另一个圆"),
        ("intersecting", "两个圆相交"),
        ("tangent", "两个圆相切")
    ]
    
    print(f"开始生成两圆组合，总共{len(generation_types) * samples_per_type}张图像...")
    print(f"输出目录: {IMG_DIR}")
    print(f"标签文件: {LABEL_FILE}")
    
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        img_idx = start_img_idx
        
        for gen_type, description in generation_types:
            print(f"正在生成: {description} ({samples_per_type}个样本)")
            
            for j in range(samples_per_type):
                img_path, descs = gen_two_circles(img_idx, gen_type)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                img_idx += 1
                
                if (j + 1) % 100 == 0:
                    print(f"  已完成 {j + 1}/{samples_per_type}")
    
    print(f'两圆生成完成！总共生成了 {len(generation_types) * samples_per_type} 个样本')
    print(f'图像保存在: {IMG_DIR}')
    print(f'标签保存在: {LABEL_FILE}')

if __name__ == "__main__":
    main()