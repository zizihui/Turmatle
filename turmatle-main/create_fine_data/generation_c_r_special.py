"""生成微调数据集-特殊双图形中的圆和矩形"""
import os
import sys
import random
import turtle
import math
from PIL import Image
import ctypes

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from geom.base import Geom, Point
from geom.shapes import Circle, Rect

WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas_finetuning/datas_c_r_special/images_c_r_special')
LABEL_FILE = os.path.join(project_root, 'datas_finetuning/datas_c_r_special/labels_c_r_special.txt')
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
    return f'circle{idx} = Circle(Point({center[0]:.1f},{center[1]:.1f}), {radius:.1f})'

def rect_desc(idx, bottom_left, top_right):
    return f'rect{idx} = Rect(Point({bottom_left[0]:.1f},{bottom_left[1]:.1f}), Point({top_right[0]:.1f},{top_right[1]:.1f}))'

def get_next_img_idx(img_dir):
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('cr_special') and f.endswith('.png'):
            try:
                num = int(f[10:-4])
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def calculate_distance(p1, p2):
    """计算两点间距离"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def point_to_line_distance(point, line_p1, line_p2):
    """计算点到直线的距离"""
    x0, y0 = point
    x1, y1 = line_p1
    x2, y2 = line_p2
    
    # 使用点到直线距离公式：|ax + by + c| / sqrt(a² + b²)
    # 其中直线方程为：(y2-y1)x - (x2-x1)y + (x2-x1)y1 - (y2-y1)x1 = 0
    a = y2 - y1
    b = -(x2 - x1)
    c = (x2 - x1) * y1 - (y2 - y1) * x1
    
    distance = abs(a * x0 + b * y0 + c) / math.sqrt(a**2 + b**2)
    return distance

def is_point_on_circle(point, center, radius):
    """判断点是否在圆上（使用点到圆心的距离）"""
    return abs(calculate_distance(point, center) - radius) <= 5e-3

def generate_circle_containing_rect(case_type):
    """
    生成圆包含矩形的情况
    case_type: 0 - 矩形四点不在圆上且距离大于0.5, 1 - 矩形四点都在圆上
    """
    attempt = 0
    while True:
        attempt += 1
        # 随机生成圆心和半径
        cx = round(random.uniform(-2.0, 2.0), 1)
        cy = round(random.uniform(-2.0, 2.0), 1)
        center = (cx, cy)
        
        # 计算最大可能半径（确保圆在画布内）
        max_r = min(4.9 - abs(cx), 4.9 - abs(cy))
        r = round(random.uniform(1.0, max_r), 1)
        
        if case_type == 0:  # 第一种情况：矩形四点不在圆上，且四点到圆距离大于0.5
            # 生成一个矩形在圆内，并与边界保持一定距离
            max_size = r * 1.8  # 最大可能的矩形尺寸
            width = round(random.uniform(max_size * 0.3, max_size * 0.9), 1)
            height = round(random.uniform(max_size * 0.3, max_size * 0.9), 1)
            
            # 随机生成矩形中心点（在圆内均匀分布）
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, r * 0.4)
            rect_cx = cx + dist * math.cos(angle)
            rect_cy = cy + dist * math.sin(angle)
            
            # 计算矩形的顶点
            bl_x = round(rect_cx - width/2, 1)
            bl_y = round(rect_cy - height/2, 1)
            tr_x = round(rect_cx + width/2, 1)
            tr_y = round(rect_cy + height/2, 1)
            
            # 检查所有顶点是否都在圆内，且距离大于0.5
            corners = [(bl_x, bl_y), (bl_x, tr_y), (tr_x, bl_y), (tr_x, tr_y)]
            if all(calculate_distance(p, center) < r - 0.5 for p in corners):
                return center, r, (bl_x, bl_y), (tr_x, tr_y)
                
        elif case_type == 1:  # 第二种情况：矩形的四个点都在圆上
            # 先确定矩形的几何参数，再计算对应的圆
            # 生成随机角度来确定矩形的方向（0到π/4之间）
            angle = random.uniform(0, math.pi/4)
            
            # 生成矩形的半宽和半高（确保矩形不会太大）
            max_half_size = min(max_r * 0.6, 2.0)  # 限制最大尺寸
            half_width = round(random.uniform(0.5, max_half_size), 1)
            half_height = round(random.uniform(0.5, max_half_size), 1)
            
            # 计算矩形的四个顶点（相对于矩形中心）
            # 矩形中心就是圆心
            rect_center = center
            
            # 计算矩形的四个顶点坐标
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            # 矩形的四个顶点（相对于矩形中心）
            dx1 = half_width * cos_a - half_height * sin_a
            dy1 = half_width * sin_a + half_height * cos_a
            dx2 = -half_width * cos_a - half_height * sin_a
            dy2 = -half_width * sin_a + half_height * cos_a
            dx3 = -half_width * cos_a + half_height * sin_a
            dy3 = -half_width * sin_a - half_height * cos_a
            dx4 = half_width * cos_a + half_height * sin_a
            dy4 = half_width * sin_a - half_height * cos_a
            
            # 计算实际顶点坐标
            x1 = round(rect_center[0] + dx1, 1)
            y1 = round(rect_center[1] + dy1, 1)
            x2 = round(rect_center[0] + dx2, 1)
            y2 = round(rect_center[1] + dy2, 1)
            x3 = round(rect_center[0] + dx3, 1)
            y3 = round(rect_center[1] + dy3, 1)
            x4 = round(rect_center[0] + dx4, 1)
            y4 = round(rect_center[1] + dy4, 1)
            
            # 计算矩形的边界框
            bl_x = min(x1, x2, x3, x4)
            bl_y = min(y1, y2, y3, y4)
            tr_x = max(x1, x2, x3, x4)
            tr_y = max(y1, y2, y3, y4)
            
            # 计算矩形的对角线长度，这应该等于圆的直径
            diagonal = math.sqrt((tr_x - bl_x)**2 + (tr_y - bl_y)**2)
            required_radius = diagonal / 2
            
            # 检查计算出的半径是否合理
            if 0.8 <= required_radius <= max_r:
                # 更新半径为计算出的值
                r = round(required_radius, 1)
                
                # 验证所有顶点是否都在圆上
                corners = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
                if all(is_point_on_circle(p, center, r) for p in corners):
                    print(f"圆包含矩形（case_type={case_type}）生成成功，尝试了{attempt}次，半径={r}")
                    return center, r, (bl_x, bl_y), (tr_x, tr_y)

def generate_rect_containing_circle(case_type):
    """
    生成矩形包含圆的情况
    case_type: 0 - 圆完全在矩形内且距离大于0.5, 1 - 圆与两边相切, 2 - 圆与三边相切, 3 - 圆与四边相切
    """
    attempt = 0
    while True:
        attempt += 1
        # 生成矩形
        bl_x = round(random.uniform(-4.5, 1.5), 1)
        bl_y = round(random.uniform(-4.5, 1.5), 1)
        w = round(random.uniform(1.5, 4.5 - bl_x), 1)
        h = round(random.uniform(1.5, 4.5 - bl_y), 1)
        tr_x = round(bl_x + w, 1)
        tr_y = round(bl_y + h, 1)
        
        if case_type == 0:  # 第一种情况：圆完全在矩形内，圆上的点到矩形边长距离大于0.5
            # 半径要小于到边界的最小距离
            max_possible_r = min(w/2, h/2) - 0.5  # 留出0.5安全距离
            if max_possible_r <= 0.5:  # 确保有足够的空间生成圆
                continue
            r = round(random.uniform(0.5, max_possible_r), 1)
            # 确保圆心位置使得圆完全在矩形内且与边界保持0.5安全距离
            cx = round(random.uniform(bl_x + r + 0.5, tr_x - r - 0.5), 1)
            cy = round(random.uniform(bl_y + r + 0.5, tr_y - r - 0.5), 1)
            
            # 验证圆上的点到矩形边距离大于0.5
            sides = [((bl_x, bl_y), (tr_x, bl_y)),  # 下边
                     ((tr_x, bl_y), (tr_x, tr_y)),  # 右边
                     ((tr_x, tr_y), (bl_x, tr_y)),  # 上边
                     ((bl_x, tr_y), (bl_x, bl_y))]  # 左边
            
            # 检查圆上8个点的距离
            angles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
            circle_points = [(cx + r * math.cos(angle), cy + r * math.sin(angle)) for angle in angles]
            
            min_distances = []
            for point in circle_points:
                dists = [point_to_line_distance(point, s[0], s[1]) for s in sides]
                min_distances.append(min(dists))
            
            if all(d > 0.5 for d in min_distances):
                print(f"矩形包含圆（case_type={case_type}）生成成功，尝试了{attempt}次")
                return (bl_x, bl_y), (tr_x, tr_y), (cx, cy), r
                
        elif case_type == 1:  # 第二种情况：圆与矩形的任意两边相切
            # 根据矩形的长宽比决定相切方式
            if w > h:  # 宽矩形，选择对角相切或上下相切
                tangent_type = random.choice([0, 2])
            elif w < h:  # 高矩形，选择对角相切或左右相切
                tangent_type = random.choice([0, 1])
            else:  # 如果w=h重新生成
                continue
            
            
            if tangent_type == 0:  # 对角相切
                 # 半径要小于到边界的最小距离，留出0.5安全距离
                max_possible_r = min(w/2, h/2) - 0.5
                if max_possible_r <= 0.5:  # 确保有足够的空间生成圆
                    continue
                r = round(random.uniform(0.5, max_possible_r), 1)
                # 随机选择四个角落之一：0-左下，1-左上，2-右下，3-右上
                corner_type = random.choice([0, 1, 2, 3])
                
                if corner_type == 0:  # 左下角：左边和下边相切
                    cx = round(bl_x + r, 1)  # 与左边相切
                    cy = round(bl_y + r, 1)  # 与下边相切
                    
                    # 验证圆心到相切的两边的距离与半径做差小于等于1e-10
                    sides = [((bl_x, bl_y), (tr_x, bl_y)),  # 下边
                             ((tr_x, bl_y), (tr_x, tr_y)),  # 右边
                             ((tr_x, tr_y), (bl_x, tr_y)),  # 上边
                             ((bl_x, tr_y), (bl_x, bl_y))]  # 左边
                    
                    left_dist = point_to_line_distance((cx, cy), sides[3][0], sides[3][1])
                    bottom_dist = point_to_line_distance((cx, cy), sides[0][0], sides[0][1])
                    
                    if abs(left_dist - r) <= 1e-10 and abs(bottom_dist - r) <= 1e-10:
                        # 验证圆上的点到其余两边距离大于0.5
                        angles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
                        circle_points = [(cx + r * math.cos(angle), cy + r * math.sin(angle)) for angle in angles]
                        
                        right_distances = [point_to_line_distance(point, sides[1][0], sides[1][1]) for point in circle_points]
                        top_distances = [point_to_line_distance(point, sides[2][0], sides[2][1]) for point in circle_points]
                        
                        if all(d > 0.5 for d in right_distances) and all(d > 0.5 for d in top_distances):
                            print(f"矩形包含圆（case_type={case_type}）生成成功，尝试了{attempt}次")
                            return (bl_x, bl_y), (tr_x, tr_y), (cx, cy), r
                            
                elif corner_type == 1:  # 左上角：左边和上边相切
                    cx = round(bl_x + r, 1)  # 与左边相切
                    cy = round(tr_y - r, 1)  # 与上边相切
                    
                    # 验证圆心到相切的两边的距离与半径做差小于等于1e-10
                    sides = [((bl_x, bl_y), (tr_x, bl_y)),  # 下边
                             ((tr_x, bl_y), (tr_x, tr_y)),  # 右边
                             ((tr_x, tr_y), (bl_x, tr_y)),  # 上边
                             ((bl_x, tr_y), (bl_x, bl_y))]  # 左边
                    
                    left_dist = point_to_line_distance((cx, cy), sides[3][0], sides[3][1])
                    top_dist = point_to_line_distance((cx, cy), sides[2][0], sides[2][1])
                    
                    if abs(left_dist - r) <= 1e-10 and abs(top_dist - r) <= 1e-10:
                        # 验证圆上的点到其余两边距离大于0.5
                        angles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
                        circle_points = [(cx + r * math.cos(angle), cy + r * math.sin(angle)) for angle in angles]
                        
                        right_distances = [point_to_line_distance(point, sides[1][0], sides[1][1]) for point in circle_points]
                        bottom_distances = [point_to_line_distance(point, sides[0][0], sides[0][1]) for point in circle_points]
                        
                        if all(d > 0.5 for d in right_distances) and all(d > 0.5 for d in bottom_distances):
                            print(f"矩形包含圆（case_type={case_type}）生成成功，尝试了{attempt}次")
                            return (bl_x, bl_y), (tr_x, tr_y), (cx, cy), r
                            
                elif corner_type == 2:  # 右下角：右边和下边相切
                    cx = round(tr_x - r, 1)  # 与右边相切
                    cy = round(bl_y + r, 1)  # 与下边相切
                    
                    # 验证圆心到相切的两边的距离与半径做差小于等于1e-10
                    sides = [((bl_x, bl_y), (tr_x, bl_y)),  # 下边
                             ((tr_x, bl_y), (tr_x, tr_y)),  # 右边
                             ((tr_x, tr_y), (bl_x, tr_y)),  # 上边
                             ((bl_x, tr_y), (bl_x, bl_y))]  # 左边
                    
                    right_dist = point_to_line_distance((cx, cy), sides[1][0], sides[1][1])
                    bottom_dist = point_to_line_distance((cx, cy), sides[0][0], sides[0][1])
                    
                    if abs(right_dist - r) <= 1e-10 and abs(bottom_dist - r) <= 1e-10:
                        # 验证圆上的点到其余两边距离大于0.5
                        angles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
                        circle_points = [(cx + r * math.cos(angle), cy + r * math.sin(angle)) for angle in angles]
                        
                        left_distances = [point_to_line_distance(point, sides[3][0], sides[3][1]) for point in circle_points]
                        top_distances = [point_to_line_distance(point, sides[2][0], sides[2][1]) for point in circle_points]
                        
                        if all(d > 0.5 for d in left_distances) and all(d > 0.5 for d in top_distances):
                            print(f"矩形包含圆（case_type={case_type}）生成成功，尝试了{attempt}次")
                            return (bl_x, bl_y), (tr_x, tr_y), (cx, cy), r
                            
                else:  # corner_type == 3, 右上角：右边和上边相切
                    cx = round(tr_x - r, 1)  # 与右边相切
                    cy = round(tr_y - r, 1)  # 与上边相切
                    
                    # 验证圆心到相切的两边的距离与半径做差小于等于1e-10
                    sides = [((bl_x, bl_y), (tr_x, bl_y)),  # 下边
                             ((tr_x, bl_y), (tr_x, tr_y)),  # 右边
                             ((tr_x, tr_y), (bl_x, tr_y)),  # 上边
                             ((bl_x, tr_y), (bl_x, bl_y))]  # 左边
                    
                    right_dist = point_to_line_distance((cx, cy), sides[1][0], sides[1][1])
                    top_dist = point_to_line_distance((cx, cy), sides[2][0], sides[2][1])
                    
                    if abs(right_dist - r) <= 1e-10 and abs(top_dist - r) <= 1e-10:
                        # 验证圆上的点到其余两边距离大于0.5
                        angles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
                        circle_points = [(cx + r * math.cos(angle), cy + r * math.sin(angle)) for angle in angles]
                        
                        left_distances = [point_to_line_distance(point, sides[3][0], sides[3][1]) for point in circle_points]
                        bottom_distances = [point_to_line_distance(point, sides[0][0], sides[0][1]) for point in circle_points]
                        
                        if all(d > 0.5 for d in left_distances) and all(d > 0.5 for d in bottom_distances):
                            print(f"矩形包含圆（case_type={case_type}）生成成功，尝试了{attempt}次")
                            return (bl_x, bl_y), (tr_x, tr_y), (cx, cy), r
                            
            elif tangent_type == 1:  # 左右相切
                r = w/2
                
                cx = bl_x + r  # x坐标，与左边相切
                cy = round(random.uniform(bl_y + r + 0.5, tr_y - r - 0.5), 1)  
                
                # 验证圆心到相切的两边的距离与半径做差小于等于1e-10
                sides = [((bl_x, bl_y), (tr_x, bl_y)),  # 下边
                         ((tr_x, bl_y), (tr_x, tr_y)),  # 右边
                         ((tr_x, tr_y), (bl_x, tr_y)),  # 上边
                         ((bl_x, tr_y), (bl_x, bl_y))]  # 左边
                
                left_dist = point_to_line_distance((cx, cy), sides[3][0], sides[3][1])
                right_dist = point_to_line_distance((cx, cy), sides[1][0], sides[1][1])
                
                # 只验证左右两边相切
                if abs(left_dist - r) <= 1e-10 and abs(right_dist - r) <= 1e-10:
                    # 验证圆上的点到上下两边距离大于0.5
                    angles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
                    circle_points = [(cx + r * math.cos(angle), cy + r * math.sin(angle)) for angle in angles]
                    
                    top_distances = [point_to_line_distance(point, sides[2][0], sides[2][1]) for point in circle_points]
                    bottom_distances = [point_to_line_distance(point, sides[0][0], sides[0][1]) for point in circle_points]
                    
                    if all(d > 0.5 for d in top_distances) and all(d > 0.5 for d in bottom_distances):
                        print(f"矩形包含圆（case_type={case_type}）生成成功，尝试了{attempt}次")
                        return (bl_x, bl_y), (tr_x, tr_y), (cx, cy), r
                        
            else:  # tangent_type == 2, 上下相切
                r = h/2  # 半径等于高度的一半
                cx = round(random.uniform(bl_x + r + 0.5, tr_x - r - 0.5), 1)
                cy = bl_y + r  # y坐标，与下边相切
                
                # 验证圆心到相切的两边的距离与半径做差小于等于1e-10
                sides = [((bl_x, bl_y), (tr_x, bl_y)),  # 下边
                         ((tr_x, bl_y), (tr_x, tr_y)),  # 右边
                         ((tr_x, tr_y), (bl_x, tr_y)),  # 上边
                         ((bl_x, tr_y), (bl_x, bl_y))]  # 左边
                
                bottom_dist = point_to_line_distance((cx, cy), sides[0][0], sides[0][1])
                top_dist = point_to_line_distance((cx, cy), sides[2][0], sides[2][1])
                
                # 只验证上下两边相切
                if abs(bottom_dist - r) <= 1e-10 and abs(top_dist - r) <= 1e-10:
                    # 验证圆上的点到左右两边距离大于0.5
                    angles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
                    circle_points = [(cx + r * math.cos(angle), cy + r * math.sin(angle)) for angle in angles]
                    
                    left_distances = [point_to_line_distance(point, sides[3][0], sides[3][1]) for point in circle_points]
                    right_distances = [point_to_line_distance(point, sides[1][0], sides[1][1]) for point in circle_points]
                    
                    if all(d > 0.5 for d in left_distances) and all(d > 0.5 for d in right_distances):
                        print(f"矩形包含圆（case_type={case_type}）生成成功，尝试了{attempt}次")
                        return (bl_x, bl_y), (tr_x, tr_y), (cx, cy), r
                        
        elif case_type == 2:  # 第三种情况：圆与矩形的三边相切
            # 根据矩形的长宽比选择不相切的边
            if w > h:  # 宽矩形，选择不与左边或右边相切
                non_tangent = random.choice(['left', 'right'])
            elif w < h:  # 高矩形，选择不与上边或下边相切
                non_tangent = random.choice(['top', 'bottom'])
            else:  # 如果w=h重新生成
                continue
                
            if non_tangent == 'top':
                r = w/2
                cx = round(bl_x + r, 1)
                cy = round(bl_y + r, 1)

            elif non_tangent == 'right':
                r = h/2
                cx = round(bl_x + r, 1)
                cy = round(bl_y + r, 1)

            elif non_tangent == 'bottom':
                r = w/2
                cx = round(bl_x - r, 1)
                cy = round(tr_y - r, 1)
            else:  # left
                r = h/2
                cx = round(tr_x - r, 1)
                cy = round(tr_y - r, 1)
            
            # 验证圆心到相切的三边的距离与半径做差小于等于1e-10
            sides = [((bl_x, bl_y), (tr_x, bl_y)),  # 下边
                     ((tr_x, bl_y), (tr_x, tr_y)),  # 右边
                     ((tr_x, tr_y), (bl_x, tr_y)),  # 上边
                     ((bl_x, tr_y), (bl_x, bl_y))]  # 左边
            
            # 计算圆心到各边的距离
            dists = [point_to_line_distance((cx, cy), s[0], s[1]) for s in sides]
            
            # 根据不相切的边，验证其他三边相切
            if non_tangent == 'top':
                if (abs(dists[0] - r) <= 1e-10 and  # 下边相切
                    abs(dists[1] - r) <= 1e-10 and  # 右边相切
                    abs(dists[3] - r) <= 1e-10):    # 左边相切
                    # 验证圆上的点到不相切的边距离大于0.5
                    angles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
                    circle_points = [(cx + r * math.cos(angle), cy + r * math.sin(angle)) for angle in angles]
                    top_distances = [point_to_line_distance(point, sides[2][0], sides[2][1]) for point in circle_points]
                    if all(d > 0.5 for d in top_distances):
                        print(f"矩形包含圆（case_type={case_type}）生成成功，尝试了{attempt}次")
                        return (bl_x, bl_y), (tr_x, tr_y), (cx, cy), r
            elif non_tangent == 'right':
                if (abs(dists[0] - r) <= 1e-10 and  # 下边相切
                    abs(dists[2] - r) <= 1e-10 and  # 上边相切
                    abs(dists[3] - r) <= 1e-10):    # 左边相切
                    # 验证圆上的点到不相切的边距离大于0.5
                    angles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
                    circle_points = [(cx + r * math.cos(angle), cy + r * math.sin(angle)) for angle in angles]
                    right_distances = [point_to_line_distance(point, sides[1][0], sides[1][1]) for point in circle_points]
                    if all(d > 0.5 for d in right_distances):
                        print(f"矩形包含圆（case_type={case_type}）生成成功，尝试了{attempt}次")
                        return (bl_x, bl_y), (tr_x, tr_y), (cx, cy), r
            elif non_tangent == 'bottom':
                if (abs(dists[1] - r) <= 1e-10 and  # 右边相切
                    abs(dists[2] - r) <= 1e-10 and  # 上边相切
                    abs(dists[3] - r) <= 1e-10):    # 左边相切
                    # 验证圆上的点到不相切的边距离大于0.5
                    angles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
                    circle_points = [(cx + r * math.cos(angle), cy + r * math.sin(angle)) for angle in angles]
                    bottom_distances = [point_to_line_distance(point, sides[0][0], sides[0][1]) for point in circle_points]
                    if all(d > 0.5 for d in bottom_distances):
                        print(f"矩形包含圆（case_type={case_type}）生成成功，尝试了{attempt}次")
                        return (bl_x, bl_y), (tr_x, tr_y), (cx, cy), r
            else:  # left
                if (abs(dists[0] - r) <= 1e-10 and  # 下边相切
                    abs(dists[1] - r) <= 1e-10 and  # 右边相切
                    abs(dists[2] - r) <= 1e-10):    # 上边相切
                    # 验证圆上的点到不相切的边距离大于0.5
                    angles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
                    circle_points = [(cx + r * math.cos(angle), cy + r * math.sin(angle)) for angle in angles]
                    left_distances = [point_to_line_distance(point, sides[3][0], sides[3][1]) for point in circle_points]
                    if all(d > 0.5 for d in left_distances):
                        print(f"矩形包含圆（case_type={case_type}）生成成功，尝试了{attempt}次")
                        return (bl_x, bl_y), (tr_x, tr_y), (cx, cy), r
                        
        elif case_type == 3:  # 第四种情况：圆与矩形的四边相切，此时矩形为正方形
            # 四边相切要求矩形必须是正方形
            size = min(w, h)  # 取较小的值作为正方形边长
            w = size
            h = size
            
            # 重新计算右上角坐标
            tr_x = round(bl_x + w, 1)
            tr_y = round(bl_y + h, 1)
            
            # 圆心在正方形中心
            cx = round((bl_x + tr_x) / 2, 1)
            cy = round((bl_y + tr_y) / 2, 1)
            
            # 半径是正方形边长的一半
            r = round(w / 2, 1)
            
            # 验证圆心到四边的距离与半径的差小于等于1e-10
            sides = [((bl_x, bl_y), (tr_x, bl_y)),  # 下边
                     ((tr_x, bl_y), (tr_x, tr_y)),  # 右边
                     ((tr_x, tr_y), (bl_x, tr_y)),  # 上边
                     ((bl_x, tr_y), (bl_x, bl_y))]  # 左边
            
            dists = [point_to_line_distance((cx, cy), s[0], s[1]) for s in sides]
            if all(abs(d - r) <= 1e-10 for d in dists):
                print(f"矩形包含圆（case_type={case_type}）生成成功，尝试了{attempt}次")
                return (bl_x, bl_y), (tr_x, tr_y), (cx, cy), r

def gen_one_cr_special(img_idx, case_type, sub_case):
    """生成一个特殊的圆和矩形图像"""
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
    
    if case_type == 'circle_contains_rect':
        center, r, bl, tr = generate_circle_containing_rect(sub_case)
        circle = Circle(Point(*center), r)
        circle.show()
        descs.append(circle_desc(1, center, r))
        rect = Rect(Point(*bl), Point(*tr))
        rect.show()
        descs.append(rect_desc(1, bl, tr))
    elif case_type == 'rect_contains_circle':
        bl, tr, center, r = generate_rect_containing_circle(sub_case)
        rect = Rect(Point(*bl), Point(*tr))
        rect.show()
        descs.append(rect_desc(1, bl, tr))
        circle = Circle(Point(*center), r)
        circle.show()
        descs.append(circle_desc(1, center, r))
    
    screen.update()
    ps_path = os.path.join(IMG_DIR, f'cr_special{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'cr_special{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())
    img = img.resize((WIDTH, HEIGHT))
    img.save(png_path)
    os.remove(ps_path)
    return png_path, descs

def main():
    """主函数"""
    # 设置DPI感知
    set_dpi_awareness()
    
    # 设置样本数量
    samples_per_case = 300  # 每种情况的样本数
    
    start_img_idx = get_next_img_idx(IMG_DIR)
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        img_idx = start_img_idx
        
        print("开始生成圆包含矩形的数据...")
        # 第一类：圆包含矩形
        # 第一种情况：矩形四点不在圆上，且四点到圆距离大于0.5
        for i in range(samples_per_case):
            img_path, descs = gen_one_cr_special(img_idx, 'circle_contains_rect', 0)
            rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
            f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
            img_idx += 1
            if (i + 1) % 100 == 0:
                print(f"完成 {i + 1}/{samples_per_case} 个圆包含矩形（四点不在圆上）的样本")
        
        # 第二种情况：矩形的四个点都在圆上
        for i in range(samples_per_case):
            img_path, descs = gen_one_cr_special(img_idx, 'circle_contains_rect', 1)
            rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
            f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
            img_idx += 1
            if (i + 1) % 100 == 0:
                print(f"完成 {i + 1}/{samples_per_case} 个圆包含矩形（四点都在圆上）的样本")
        
        print("\n开始生成矩形包含圆的数据...")
        # 第二类：矩形包含圆
        # 第一种情况：圆完全在矩形内，圆上的点到矩形边长距离大于0.5
        for i in range(samples_per_case):
            img_path, descs = gen_one_cr_special(img_idx, 'rect_contains_circle', 0)
            rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
            f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
            img_idx += 1
            if (i + 1) % 100 == 0:
                print(f"完成 {i + 1}/{samples_per_case} 个矩形包含圆（完全内部）的样本")
        
        # 第二种情况：圆与矩形的任意两边相切
        for i in range(samples_per_case):
            img_path, descs = gen_one_cr_special(img_idx, 'rect_contains_circle', 1)
            rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
            f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
            img_idx += 1
            if (i + 1) % 100 == 0:
                print(f"完成 {i + 1}/{samples_per_case} 个矩形包含圆（两边相切）的样本")
        
        # 第三种情况：圆与矩形的三边相切
        for i in range(samples_per_case):
            img_path, descs = gen_one_cr_special(img_idx, 'rect_contains_circle', 2)
            rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
            f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
            img_idx += 1
            if (i + 1) % 100 == 0:
                print(f"完成 {i + 1}/{samples_per_case} 个矩形包含圆（三边相切）的样本")
        
        # 第四种情况：圆与矩形的四边相切
        for i in range(samples_per_case):
            img_path, descs = gen_one_cr_special(img_idx, 'rect_contains_circle', 3)
            rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
            f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
            img_idx += 1
            if (i + 1) % 100 == 0:
                print(f"完成 {i + 1}/{samples_per_case} 个矩形包含圆（四边相切）的样本")
    
    print('特殊圆和矩形生成完成！总共生成', samples_per_case * 6, '个样本')

if __name__ == "__main__":
    main() 