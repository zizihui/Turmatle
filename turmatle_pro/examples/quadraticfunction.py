import sys
import os

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 现在导入应该可以工作了
from geom import Geom, Point, Line, Function, Rect, Text, QuadraticFunction, LinearFunction
from geom.effects import Flash, Outline, Scale, Indicate
import math
import turtle
from PIL import Image

def main():
    Geom.setup_canvas(1000, 1000)   # DPI 感知 + 1000×1000 画布
    # 设置全局默认值
    Geom.set_defaults(origin_x=0, origin_y=0, scale=100, fontsize=25)

    WIDTH, HEIGHT = 1000, 1000
    IMG_DIR = os.path.join(project_root, 'examples/images')
    os.makedirs(IMG_DIR, exist_ok=True) # 创建images目录

    #是否启用动画
    turtle.tracer(False)
    # 创建坐标轴
    x_axis = Line(Point(-4, 0), Point(4, 0), 
                speed=0, pensize=3, 
                color="gray", text="x",
                arrow=True)
    y_axis = Line(Point(0, -4), Point(0, 4), 
                speed=0, pensize=3,
                color="gray", text="y",
                arrow=True)

    # 显示坐标轴
    x_axis.show()
    y_axis.show()

    # 二次函数标准式
    f1 = QuadraticFunction(
        a=1,                        # 二次函数系数a
        b=-0.5,                     # 二次函数系数b
        c=1.0,                     # 二次函数系数c
        form="standard",            # 标准式
        x_range=(-0.8, 2),            # 自变量x范围
        color="blue",               # 函数颜色
        pensize=5,                  # 线条粗细
        show_axis=True,            # 是否画对称轴
        axis_color="gray",          # 对称轴颜色
        show_vertex=True,          # 是否画顶点
        vertex_color="red",         # 顶点颜色
        text="y=x²-0.5x+1.0",       # 文本内容
        text_pos=None               # 文本位置，默认右端点
        )
    
    
    f2 = QuadraticFunction(
        a=-1,                        # 二次函数系数a
        h=-1,                        # 二次函数对称轴h
        k=-2,                       # 二次函数系数k
        form="vertex",              # 顶点式    
        x_range=(-4, 0),          # 自变量x范围
        color="green",              # 函数颜色
        pensize=4,                  # 线条粗细
        show_axis=True,            # 是否画对称轴
        axis_color="gray",          # 对称轴颜色
        show_vertex=True,          # 是否画顶点
        vertex_color="red",         # 顶点颜色
        text="y=(x-1)²-2",          # 文本内容
        text_pos=None               # 文本位置，默认右端点
        )
  
    f2.show()
    f1.show()

    f1_axis_label=Text(position=Point(f1.axis_of_symmetry()+0.2,f1.vertex()[1] + 2.0), 
    text=f"x={f1.axis_of_symmetry()}", 
    color="blue")

    f1_vertex_label=Text(position=Point(f1.vertex()[0], f1.vertex()[1]-0.5), 
    text=f"({f1.vertex()[0]}, {f1.vertex()[1]})", 
    color="blue")

    f2_axis_label=Text(position=Point(f2.axis_of_symmetry()+0.2, f2.vertex()[1]-2.0), 
    text=f"x={f2.axis_of_symmetry()}", 
    color="green")

    f2_vertex_label=Text(position=Point(f2.vertex()[0], f2.vertex()[1]+0.5), 
    text=f"({f2.vertex()[0]}, {f2.vertex()[1]})", 
    color="green")

    f1_axis_label.show()
    f1_vertex_label.show()
    f2_axis_label.show()
    f2_vertex_label.show()

    screen = turtle.Screen()
    screen.update()  # 更新画面
    
    # 保存图像
    ps_path = os.path.join(IMG_DIR, 'quadraticfunction.ps')
    png_path = os.path.join(IMG_DIR, 'quadraticfunction.png')
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
