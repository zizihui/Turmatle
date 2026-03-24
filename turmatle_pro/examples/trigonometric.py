import sys
import os

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 现在导入应该可以工作了
from geom import Geom, Point, Line, Function, Rect, Text
from geom.effects import Flash, Outline, Scale, Indicate
import math
import turtle
from PIL import Image


def main():
    Geom.setup_canvas(1000, 1000)   # DPI 感知 + 1000×1000 画布
    # 设置全局默认值
    Geom.set_defaults(origin_x=-1, origin_y=-0.5, scale=80, fontsize=25)
    
    WIDTH, HEIGHT = 1000, 1000
    IMG_DIR = os.path.join(project_root, 'examples/images')
    os.makedirs(IMG_DIR, exist_ok=True) # 创建images目录

    # 创建坐标轴
    x_axis = Line(Point(-5, 0), Point(8, 0), 
                speed=0, pensize=3, 
                color="gray", text="x",
                arrow=True)
    y_axis = Line(Point(0, -3), Point(0, 3), 
                speed=0, pensize=3,
                color="gray", text="y",
                arrow=True)

    # 显示坐标轴
    x_axis.show()
    y_axis.show()

    # 绘制被积函数
    sin_func = Function(
        math.sin,
        x_start=-math.pi, 
        x_end=3/2*math.pi,
        color="black", 
        pensize=5,
        text="y=sin(x)",
        fill=False,
        fill_color="azure"
        #text_pos=(0, 1)  # 在 (0,1) 位置显示文本
    )

    cos_func = Function(
        math.cos,
        x_start=-1/2*math.pi, 
        x_end=3/2*math.pi,
        color="red", 
        pensize=5,
        text="y=cos(x)",
        fill=False,
        fill_color="azure"
        #text_pos=(0, 1)  # 在 (0,1) 位置显示文本
    )

    tan_func = Function(
        math.tan,
        x_start=-1/2*math.pi, 
        x_end=3/2*math.pi,
        color="blue", 
        pensize=5,
        text="y=tan(x)",
        fill=False,
        fill_color="azure",
        text_pos=(3/2*math.pi,2),  # 在 (0,1) 位置显示文本
        y_limit=5
    )

    sin_func.show()
    sin_func.play(Flash())
    cos_func.show()
    tan_func.show()
    screen = turtle.Screen()
    screen.update()  # 更新画面

    # 保存图像
    ps_path = os.path.join(IMG_DIR, 'trigonometric.ps')
    png_path = os.path.join(IMG_DIR, 'trigonometric.png')
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
