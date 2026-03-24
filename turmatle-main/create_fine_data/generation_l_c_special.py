"""生成微调数据集-特殊双图形中的线段和圆"""
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
from geom.shapes import Line, Circle

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas_finetuning/datas_l_c_special/images_l_c_special')
LABEL_FILE = os.path.join(project_root, 'datas_finetuning/datas_l_c_special/labels_l_c_special.txt')
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

def line_desc(idx, start, end):
    return f'line{idx} = Line(Point({start[0]:.1f},{start[1]:.1f}), Point({end[0]:.1f},{end[1]:.1f}))'

def circle_desc(idx, center, radius):
    return f'circle{idx} = Circle(Point({center[0]:.1f},{center[1]:.1f}), {radius:.1f})'

def is_point_in_bounds(point):
    """检查点是否在画布范围内"""
    return -4.9 <= point[0] <= 4.9 and -4.9 <= point[1] <= 4.9

def generate_line_endpoints_on_circle():
    """生成线段的两个端点都在圆上（弦）"""
    while True:
        max_r = 5.0 - 0.5
        radius = round(random.uniform(1.0, max_r), 1)  # 最小半径改为1.0
        center_x = round(random.uniform(-4.9 + radius, 4.9 - radius), 1)
        center_y = round(random.uniform(-4.9 + radius, 4.9 - radius), 1)
        
        # 在圆上选择两个点作为线段端点
        # 先生成角度
        angle1 = random.uniform(0, 2*math.pi)
        angle2 = random.uniform(0, 2*math.pi)
        
        # 确保两个角度差距足够大，避免生成太短的线段
        while abs(angle1 - angle2) < 1.0:
            angle2 = random.uniform(0, 2*math.pi)
        
        # 计算端点坐标
        x1 = round(center_x + radius * math.cos(angle1), 1)
        y1 = round(center_y + radius * math.sin(angle1), 1)
        x2 = round(center_x + radius * math.cos(angle2), 1)
        y2 = round(center_y + radius * math.sin(angle2), 1)
        
        # 检查所有点是否在边界内
        if (is_point_in_bounds((x1, y1)) and is_point_in_bounds((x2, y2))):
            
            # 验证线段长度不为0（避免退化线段）
            line_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if line_length < 1.5:  # 确保线段长度至少为1.5
                continue  # 重新生成
            # 验证圆心到线段端点的距离等于半径
            dist1 = math.sqrt((x1 - center_x)**2 + (y1 - center_y)**2)
            dist2 = math.sqrt((x2 - center_x)**2 + (y2 - center_y)**2)
            if abs(dist1 - radius) < 1e-10 and abs(dist2 - radius) < 1e-10:
                return (center_x, center_y), radius, (x1, y1), (x2, y2)

def generate_tangent_line_to_circle():
    """生成与圆相切的线段"""
    while True:
        max_r = 3.0
        radius = round(random.uniform(1.0, max_r), 1)  # 最小半径改为1.0
        center_x = round(random.uniform(-4.9 + radius, 4.9 - radius), 1)
        center_y = round(random.uniform(-4.9 + radius, 4.9 - radius), 1)
        
        # 随机选择切点的角度
        tangent_angle = random.uniform(0, 2*math.pi)
        
        # 计算切点坐标
        tangent_x = center_x + radius * math.cos(tangent_angle)
        tangent_y = center_y + radius * math.sin(tangent_angle)
               
        # 计算切线方向（垂直于半径方向）
        # 半径方向向量: (cos(tangent_angle), sin(tangent_angle))
        # 切线方向向量: (-sin(tangent_angle), cos(tangent_angle))
        tangent_dx = -math.sin(tangent_angle)
        tangent_dy = math.cos(tangent_angle)
        
        # 在切点两侧生成线段端点
        line_length = round(random.uniform(1.5, 6.5), 1)
        half_length = line_length / 2
        
        # 计算线段的两个端点
        x1 = round(tangent_x - half_length * tangent_dx, 1)
        y1 = round(tangent_y - half_length * tangent_dy, 1)
        x2 = round(tangent_x + half_length * tangent_dx, 1)
        y2 = round(tangent_y + half_length * tangent_dy, 1)
        
        # 检查所有相关点是否在边界内
        if (is_point_in_bounds((x1, y1)) and 
            is_point_in_bounds((x2, y2))):
            
            # 验证圆心到线段的距离等于半径
            # 使用点到直线距离公式：|ax + by + c| / sqrt(a² + b²)
            # 其中直线方程为：(y2-y1)x - (x2-x1)y + (x2-x1)y1 - (y2-y1)x1 = 0
            a = y2 - y1
            b = -(x2 - x1)
            c = (x2 - x1) * y1 - (y2 - y1) * x1
            
            # 圆心到线段的距离
            distance = abs(a * center_x + b * center_y + c) / math.sqrt(a**2 + b**2)
            
            if abs(distance - radius) < 1e-10:
                return (center_x, center_y), radius, (x1, y1), (x2, y2)

def gen_line_circle_relation(img_idx, relation_type):
    """生成线段与圆的特定关系图像"""
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
    
    descs = []
    
    if relation_type == "endpoints_on_circle":
        # 生成线段端点在圆上的情况
        center, radius, line_start, line_end = generate_line_endpoints_on_circle()
        
        # 先画圆
        circle = Circle(Point(center[0], center[1]), radius)
        circle.show()
        descs.append(circle_desc(1, center, radius))
        
        # 再画线段
        line = Line(Point(line_start[0], line_start[1]), Point(line_end[0], line_end[1]))
        line.show()
        descs.append(line_desc(1, line_start, line_end))
        
    elif relation_type == "tangent_to_circle":
        # 生成线段与圆相切的情况
        center, radius, line_start, line_end = generate_tangent_line_to_circle()
        
        # 先画圆
        circle = Circle(Point(center[0], center[1]), radius)
        circle.show()
        descs.append(circle_desc(1, center, radius))
        
        # 再画线段
        line = Line(Point(line_start[0], line_start[1]), Point(line_end[0], line_end[1]))
        line.show()
        descs.append(line_desc(1, line_start, line_end))
    
    screen.update()
    
    # 保存图像
    ps_path = os.path.join(IMG_DIR, f'lc_special{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'lc_special{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())  # 自动去除白边
    img = img.resize((WIDTH, HEIGHT))  # 强制拉伸到目标尺寸
    img.save(png_path)
    os.remove(ps_path)
    
    return png_path, descs

def get_next_img_idx(img_dir):
    """获取下一个图像索引"""
    if not os.path.exists(img_dir):
        return 1
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('lc_special') and f.endswith('.png'):
            try:
                num = int(f[10:-4])  # 去掉'lc_special'前缀和'.png'后缀
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def main():
    # 设置DPI感知
    set_dpi_awareness()
    """主函数"""
    # 每种关系生成900个样本
    samples_per_type = 900
    start_img_idx = get_next_img_idx(IMG_DIR)
    
    relation_types = [
        ("endpoints_on_circle", "线段端点在圆上"),
        ("tangent_to_circle", "线段与圆相切")
    ]
    
    print(f"开始生成线段与圆的关系数据，总共{len(relation_types) * samples_per_type}张图像...")
    print(f"输出目录: {IMG_DIR}")
    print(f"标签文件: {LABEL_FILE}")
    
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        img_idx = start_img_idx
        
        for relation_type, description in relation_types:
            print(f"正在生成: {description} ({samples_per_type}个样本)")
            
            for j in range(samples_per_type):
                img_path, descs = gen_line_circle_relation(img_idx, relation_type)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                img_idx += 1
                
                if (j + 1) % 100 == 0:
                    print(f"  已完成 {j + 1}/{samples_per_type}")
    
    print(f'线段与圆关系生成完成！总共生成了 {len(relation_types) * samples_per_type} 个样本')
    print(f'图像保存在: {IMG_DIR}')
    print(f'标签保存在: {LABEL_FILE}')

if __name__ == "__main__":
    main()