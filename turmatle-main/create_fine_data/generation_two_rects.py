"""生成微调数据集-特殊双图形中的两个矩形"""
import os
import sys
import random
import turtle
import ctypes
from PIL import Image

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from geom.base import Geom, Point
from geom.shapes import Rect

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas_finetuning/datas_two_rects/images_two_r')
LABEL_FILE = os.path.join(project_root, 'datas_finetuning/datas_two_rects/labels_two_r.txt')
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

def rect_desc(idx, bottom_left, top_right):
    """生成矩形描述"""
    return f'rect{idx} = Rect(Point({bottom_left[0]:.1f},{bottom_left[1]:.1f}), Point({top_right[0]:.1f},{top_right[1]:.1f}))'

def is_rect_in_bounds(x1, y1, x2, y2):
    """检查矩形是否完全在画布边界内"""
    return (-4.9 <= x1 <= 4.9 and -4.9 <= y1 <= 4.9 and 
            -4.9 <= x2 <= 4.9 and -4.9 <= y2 <= 4.9)

def generate_containing_rects():
    """生成包含关系的两个矩形（大矩形包含小矩形）"""
    while True:
        # 生成大矩形
        large_x1 = round(random.uniform(-4.9, 3), 1)
        large_y1 = round(random.uniform(-4.9, 3), 1)
        large_x2 = round(random.uniform(large_x1 + 2.0, 4.9), 1)  # 确保大矩形有足够大小
        large_y2 = round(random.uniform(large_y1 + 2.0, 4.9), 1)
        
        # 确保大矩形在边界内
        if not is_rect_in_bounds(large_x1, large_y1, large_x2, large_y2):
            continue
            
        # 在大矩形内部生成小矩形
        # 留出安全边距
        margin = 0.5
        small_x1_min = large_x1 + margin
        small_y1_min = large_y1 + margin
        small_x2_max = large_x2 - margin
        small_y2_max = large_y2 - margin
        
        # 确保有足够空间生成小矩形
        if (small_x2_max - small_x1_min > 0.5 and 
            small_y2_max - small_y1_min > 0.5):
            
            # 统一最小尺寸标准为0.5
            min_size = 0.5
            
            # 生成小矩形的左下角
            small_x1 = round(random.uniform(small_x1_min, small_x2_max - min_size), 1)
            small_y1 = round(random.uniform(small_y1_min, small_y2_max - min_size), 1)
            
            # 生成小矩形的右上角，确保在大矩形内
            small_x2 = round(random.uniform(small_x1 + min_size, small_x2_max), 1)
            small_y2 = round(random.uniform(small_y1 + min_size, small_y2_max), 1)
            #small_x2 = round(random.uniform(small_x1 + min_size, min(small_x1 + 2.0, small_x2_max)), 1)
            #small_y2 = round(random.uniform(small_y1 + min_size, min(small_y1 + 2.0, small_y2_max)), 1)
            
            # 验证小矩形完全在大矩形内
            if (large_x1 < small_x1 < small_x2 < large_x2 and
                large_y1 < small_y1 < small_y2 < large_y2):
                return (large_x1, large_y1), (large_x2, large_y2), (small_x1, small_y1), (small_x2, small_y2)

def generate_random_rects():
    """生成两个随机矩形"""
    while True:
        # 生成第一个矩形
        x1_1 = round(random.uniform(-4.9, 4.0), 1)
        y1_1 = round(random.uniform(-4.9, 4.0), 1)
        x2_1 = round(random.uniform(x1_1 + 0.5, 4.9), 1)
        y2_1 = round(random.uniform(y1_1 + 0.5, 4.9), 1)
        
        # 生成第二个矩形
        x1_2 = round(random.uniform(-4.9, 4.0), 1)
        y1_2 = round(random.uniform(-4.9, 4.0), 1)
        x2_2 = round(random.uniform(x1_2 + 0.5, 4.9), 1)
        y2_2 = round(random.uniform(y1_2 + 0.5, 4.9), 1)
        
        # 检查两个矩形都在边界内
        if (is_rect_in_bounds(x1_1, y1_1, x2_1, y2_1) and
            is_rect_in_bounds(x1_2, y1_2, x2_2, y2_2)):
            return (x1_1, y1_1), (x2_1, y2_1), (x1_2, y1_2), (x2_2, y2_2)

def gen_two_rects(img_idx, generation_type):
    """生成两个矩形的图像"""
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
    
    # 根据类型生成两个矩形
    if generation_type == "containing":
        rect1_bl, rect1_tr, rect2_bl, rect2_tr = generate_containing_rects()
    else:  # random
        rect1_bl, rect1_tr, rect2_bl, rect2_tr = generate_random_rects()
    
    # 创建并显示两个矩形
    rect1 = Rect(Point(rect1_bl[0], rect1_bl[1]), Point(rect1_tr[0], rect1_tr[1]))
    rect2 = Rect(Point(rect2_bl[0], rect2_bl[1]), Point(rect2_tr[0], rect2_tr[1]))
    
    rect1.show()
    rect2.show()
    
    screen.update()
    
    # 保存图像
    ps_path = os.path.join(IMG_DIR, f'two_r{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'two_r{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())  # 自动去除白边
    img = img.resize((WIDTH, HEIGHT))  # 强制拉伸到目标尺寸
    img.save(png_path)
    os.remove(ps_path)
    
    # 生成描述
    descs = [
        rect_desc(1, rect1_bl, rect1_tr),
        rect_desc(2, rect2_bl, rect2_tr)
    ]
    
    return png_path, descs

def get_next_img_idx(img_dir):
    """获取下一个图像索引"""
    if not os.path.exists(img_dir):
        return 1
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('two_r') and f.endswith('.png'):
            try:
                num = int(f[5:-4])  # 去掉'tr'前缀和'.png'后缀
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def main():
    # 设置DPI感知
    set_dpi_awareness()
    
    """主函数"""
    # 每种类型生成3000个样本
    samples_per_type = 3000
    start_img_idx = get_next_img_idx(IMG_DIR)
    
    generation_types = [
        ("containing", "包含关系的两个矩形"),
        ("random", "随机的两个矩形")
    ]
    
    print(f"开始生成两矩形组合，总共{len(generation_types) * samples_per_type}张图像...")
    print(f"输出目录: {IMG_DIR}")
    print(f"标签文件: {LABEL_FILE}")
    
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        img_idx = start_img_idx
        
        for gen_type, description in generation_types:
            print(f"正在生成: {description} ({samples_per_type}个样本)")
            
            for j in range(samples_per_type):
                img_path, descs = gen_two_rects(img_idx, gen_type)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                img_idx += 1
                
                if (j + 1) % 100 == 0:
                    print(f"  已完成 {j + 1}/{samples_per_type}")
    
    print(f'两矩形生成完成！总共生成了 {len(generation_types) * samples_per_type} 个样本')
    print(f'图像保存在: {IMG_DIR}')
    print(f'标签保存在: {LABEL_FILE}')

if __name__ == "__main__":
    main()