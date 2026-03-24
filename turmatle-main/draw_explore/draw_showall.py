import sys
import os
import ctypes
from PIL import Image

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 现在导入应该可以工作了
from geom import Geom, Point, Line, Rect, Circle, Triangle
import math
import turtle

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'draw_explore/predict')
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


def main():
    # 设置DPI感知
    set_dpi_awareness()

    # 设置全局默认值
    Geom.set_defaults(origin_x=0, origin_y=0, scale=100, speed = 0, pensize = 5)

    #画布大小
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
    print("逻辑画布大小（单位：turtle坐标）:", screen.screensize())
    print("窗口像素宽度:", screen.window_width())
    print("窗口像素高度:", screen.window_height())
    screen.tracer(0)  # 关闭动画效果

    #绘画命令
    circle1=Circle(Point(4.1,3.2), 0.3)
    triangle1=Triangle(Point(-3.8,-3.8), Point(2.5,-4.0), Point(4.0,-3.9))

    
    # 显示所有元素
    Geom.show_all()
    screen.update()

    # 保存图像（按序号递增保存，不覆盖历史文件）

    existing = [f for f in os.listdir(IMG_DIR) if f.startswith('images_draw_predict_') and f.endswith('.png')]
    def extract_index(name):
        try:
            base = os.path.splitext(name)[0]  # images_all_0001
            idx_str = base.split('_')[-1]
            return int(idx_str)
        except Exception:
            return 0
    next_idx = 1
    if existing:
        next_idx = max(extract_index(f) for f in existing) + 1

    png_filename = f"images_draw_predict_{next_idx:04d}.png"
    ps_filename = f"images_draw_predict_{next_idx:04d}.ps"
    ps_path = os.path.join(IMG_DIR, ps_filename)
    png_path = os.path.join(IMG_DIR, png_filename)
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    
    # 使用PIL处理图像
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())  # 自动去除白边
    img = img.resize((WIDTH, HEIGHT))  # 强制拉伸到目标尺寸
    img.save(png_path)
    os.remove(ps_path)  # 删除中间的ps文件
    
    print(f"图像已保存到: {png_path}")

    turtle.done()

if __name__ == "__main__":
    main() 