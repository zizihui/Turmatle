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
        a=-1,                        # 二次函数系数a
        b=0.5,                     # 二次函数系数b
        c=1.5,                     # 二次函数系数c
        form="standard",            # 标准式
        x_range=(-1.5, 2),            # 自变量x范围
        color="blue",               # 函数颜色
        pensize=5,                  # 线条粗细
        show_axis=True,            # 是否画对称轴
        axis_color="black",          # 对称轴颜色
        show_vertex=True,          # 是否画顶点
        vertex_color="red",         # 顶点颜色
        text="y=ax²+bx+c(a<0)",       # 文本内容
        text_pos=None               # 文本位置，默认右端点
        )
    o_label = Text( 
        position=Point(-0.2,-0.2),      # 文本位置
        text="O",                    # 文本内容
        color="black",               # 文本颜色
        fontsize=None,              # 字体大小，不指定即为Geom默认
        align="center",             # 对齐方式'left', 'center', 'right'
        bold=False,                 # 是否加粗
        italic=False,               # 是否斜体
    )
    f1.show()
    o_label.show()

    f1_axis_label=Text(position=Point(f1.axis_of_symmetry()+0.2,f1.vertex()[1] + 0.5), 
    text="x=-b/2a", 
    color="black")

    f1_axis_label.show()



    screen = turtle.Screen()
    screen.update()  # 更新画面
    
    # 保存图像
    ps_path = os.path.join(IMG_DIR, 'quadraticfunction_copy.ps')
    png_path = os.path.join(IMG_DIR, 'quadraticfunction_copy.png')
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
