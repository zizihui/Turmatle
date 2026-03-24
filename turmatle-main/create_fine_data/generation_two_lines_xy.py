"""生成微调数据集-特殊双图形中的两条水平/垂直线段"""
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
from geom.shapes import Line

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas_finetuning/datas_two_lines_xy/images_two_l_xy')
LABEL_FILE = os.path.join(project_root, 'datas_finetuning/datas_two_lines_xy/labels_two_l_xy.txt')
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
    """生成线条描述"""
    return f'line{idx} = Line(Point({start[0]:.1f},{start[1]:.1f}), Point({end[0]:.1f},{end[1]:.1f}))'

def are_collinear_xy(line1_start, line1_end, line2_start, line2_end):
    """检查两条水平/垂直线是否共线（重叠）"""
    # 判断两条线的类型
    line1_horizontal = (line1_start[1] == line1_end[1])
    line2_horizontal = (line2_start[1] == line2_end[1])
    
    # 如果两条线类型不同，不可能共线
    if line1_horizontal != line2_horizontal:
        return False
    
    if line1_horizontal:  # 都是水平线
        # 必须在同一y坐标上
        if line1_start[1] != line2_start[1]:
            return False
        # 检查x轴范围是否重叠
        x1_min, x1_max = min(line1_start[0], line1_end[0]), max(line1_start[0], line1_end[0])
        x2_min, x2_max = min(line2_start[0], line2_end[0]), max(line2_start[0], line2_end[0])
        return not (x1_max < x2_min or x2_max < x1_min)  # 有重叠则为True
    else:  # 都是垂直线
        # 必须在同一x坐标上
        if line1_start[0] != line2_start[0]:
            return False
        # 检查y轴范围是否重叠
        y1_min, y1_max = min(line1_start[1], line1_end[1]), max(line1_start[1], line1_end[1])
        y2_min, y2_max = min(line2_start[1], line2_end[1]), max(line2_start[1], line2_end[1])
        return not (y1_max < y2_min or y2_max < y1_min)  # 有重叠则为True

def point_on_line_segment(line_start, line_end, t):
    """在线段上按比例t（0到1）生成一个点（1位小数）"""
    x = round(line_start[0] + t * (line_end[0] - line_start[0]), 1)
    y = round(line_start[1] + t * (line_end[1] - line_start[1]), 1)
    return (x, y)

def calculate_distance(p1, p2):
    """计算两点之间的距离"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def generate_horizontal_line(min_length=1.0, max_length=8.0):
    """生成水平线端点"""
    while True:
        y = round(random.uniform(-4.9, 4.9), 1)
        x1 = round(random.uniform(-4.9, 4.9), 1)
        x2 = round(random.uniform(-4.9, 4.9), 1)
        # 确保线段长度符合要求
        distance = abs(x2 - x1)
        if min_length <= distance <= max_length:
            return (x1, y), (x2, y)

def generate_vertical_line(min_length=1.0, max_length=8.0):
    """生成垂直线端点"""
    while True:
        x = round(random.uniform(-4.9, 4.9), 1)
        y1 = round(random.uniform(-4.9, 4.9), 1)
        y2 = round(random.uniform(-4.9, 4.9), 1)
        # 确保线段长度符合要求
        distance = abs(y2 - y1)
        if min_length <= distance <= max_length:
            return (x, y1), (x, y2)

def generate_xy_line():
    """随机生成水平线或垂直线"""
    line_type = random.choice(['horizontal', 'vertical'])
    if line_type == 'horizontal':
        return generate_horizontal_line()
    else:
        return generate_vertical_line()

def generate_line_from_point(start_point):
    """从给定点生成一条水平线或垂直线"""
    line_type = random.choice(['horizontal', 'vertical'])
    
    if line_type == 'horizontal':
        # 水平线：y坐标相同，随机生成x坐标
        other_x = round(random.uniform(-4.9, 4.9), 1)
        return start_point, (other_x, start_point[1])
    else:
        # 垂直线：x坐标相同，随机生成y坐标
        other_y = round(random.uniform(-4.9, 4.9), 1)
        return start_point, (start_point[0], other_y)

def generate_shared_endpoint_lines():
    """生成有公共端点且不共线的两条水平/垂直线 - 直接在整个画布内生成"""
    while True:
        # 公共端点 - 直接在整个画布范围内生成
        shared_x = round(random.uniform(-4.9, 4.9), 1)
        shared_y = round(random.uniform(-4.9, 4.9), 1)
        shared_point = (shared_x, shared_y)
        
        # 生成第一条线
        line1_start, line1_end = generate_line_from_point(shared_point)
        
        # 生成第二条线
        line2_start, line2_end = generate_line_from_point(shared_point)
        
        # 确保两条线不共线且长度合适
        if (not are_collinear_xy(line1_start, line1_end, line2_start, line2_end) and
            1.0 <= calculate_distance(line1_start, line1_end) <= 8.0 and
            1.0 <= calculate_distance(line2_start, line2_end) <= 8.0):
            return line1_start, line1_end, line2_start, line2_end

def generate_point_on_line():
    """生成一条线的端点在另一条线上的两条水平/垂直线 - 直接在整个画布内生成"""
    while True:
        # 先生成第一条线（水平或垂直）
        line1_start, line1_end = generate_xy_line()
        
        # 在第一条线上随机选择一个点（不是端点）
        t = random.uniform(0.1, 0.9)  # 避免选择端点
        point_on_line1 = point_on_line_segment(line1_start, line1_end, t)
        
        # 生成第二条线的另一个端点（直接在整个画布范围内，1位小数）
        other_point = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        
        # 根据第二条线类型调整点的坐标
        line2_type = random.choice(['horizontal', 'vertical'])
        if line2_type == 'horizontal':
            # 水平线：y坐标与point_on_line1相同
            other_point = (other_point[0], point_on_line1[1])
        else:
            # 垂直线：x坐标与point_on_line1相同
            other_point = (point_on_line1[0], other_point[1])
        
        # 随机决定哪个端点在第一条线上
        if random.choice([True, False]):
            line2_start, line2_end = point_on_line1, other_point
        else:
            line2_start, line2_end = other_point, point_on_line1
        
        # 检查条件：不共线、长度合适
        if (not are_collinear_xy(line1_start, line1_end, line2_start, line2_end) and
            1.0 <= calculate_distance(line2_start, line2_end) <= 8.0):
            return line1_start, line1_end, line2_start, line2_end

def generate_random_lines():
    """生成两条随机的水平/垂直线"""
    # 第一条线
    line1_start, line1_end = generate_xy_line()
    
    # 第二条线
    line2_start, line2_end = generate_xy_line()
    
    return line1_start, line1_end, line2_start, line2_end

def gen_two_lines_xy(img_idx, generation_type):
    """生成两条水平/垂直线的图像"""
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
    
    # 根据类型生成两条线
    if generation_type == "shared_endpoint":
        line1_start, line1_end, line2_start, line2_end = generate_shared_endpoint_lines()
    elif generation_type == "point_on_line":
        line1_start, line1_end, line2_start, line2_end = generate_point_on_line()
    else:  # random
        line1_start, line1_end, line2_start, line2_end = generate_random_lines()
    
    # 创建并显示两条线
    line1 = Line(Point(line1_start[0], line1_start[1]), Point(line1_end[0], line1_end[1]))
    line2 = Line(Point(line2_start[0], line2_start[1]), Point(line2_end[0], line2_end[1]))
    
    line1.show()
    line2.show()
    
    screen.update()
    
    # 保存图像
    ps_path = os.path.join(IMG_DIR, f'two_l_xy{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'two_l_xy{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())  # 自动去除白边
    img = img.resize((WIDTH, HEIGHT))  # 强制拉伸到目标尺寸
    img.save(png_path)
    os.remove(ps_path)
    
    # 生成描述
    descs = [
        line_desc(1, line1_start, line1_end),
        line_desc(2, line2_start, line2_end)
    ]
    
    return png_path, descs

def get_next_img_idx(img_dir):
    """获取下一个图像索引"""
    if not os.path.exists(img_dir):
        return 1
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('two_l_xy') and f.endswith('.png'):
            try:
                num = int(f[8:-4])  # 去掉'two_l_xy'前缀和'.png'后缀
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def main():
    # 设置DPI感知
    set_dpi_awareness()
    """主函数"""
    # 每种类型生成1000个样本
    samples_per_type = 1000
    start_img_idx = get_next_img_idx(IMG_DIR)
    
    generation_types = [
        ("shared_endpoint", "两条水平/垂直线有公共端点且不共线"),
        ("point_on_line", "一条水平/垂直线的端点在另一条水平/垂直线上且不共线"),
        ("random", "随机生成两条水平/垂直线")
    ]
    
    print(f"开始生成水平/垂直两条线组合，总共{len(generation_types) * samples_per_type}张图像...")
    print(f"输出目录: {IMG_DIR}")
    print(f"标签文件: {LABEL_FILE}")
    
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        img_idx = start_img_idx
        
        for gen_type, description in generation_types:
            print(f"正在生成: {description} ({samples_per_type}个样本)")
            
            for j in range(samples_per_type):
                img_path, descs = gen_two_lines_xy(img_idx, gen_type)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                img_idx += 1
                
                if (j + 1) % 100 == 0:
                    print(f"  已完成 {j + 1}/{samples_per_type}")
    
    print(f'水平/垂直两条线生成完成！总共生成了 {len(generation_types) * samples_per_type} 个样本')
    print(f'图像保存在: {IMG_DIR}')
    print(f'标签保存在: {LABEL_FILE}')

if __name__ == "__main__":
    main()