import sys
import os

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 现在导入应该可以工作了
from geom import Geom, Point, Line, Function, Rect, Text, LinearFunction
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

    # 绘制一次函数
    line_func1 = LinearFunction(
        k=-1,                   # 斜率
        b=2,                    # 截距
        x_range=(-3, 3),    # 自变量范围
        color="red",            # 线条颜色
        pensize=5,              # 线条粗细
        text="y=-x+2",         # 文本内容
        text_pos = None,        # 文本位置，默认（x_end,f(x_end)）
        fill=True,              # 是否填充
        fill_color="lightblue", # 填充颜色
        )

    # 计算一次函数与x、y轴围城面积    
    area1=line_func1.area_with_axes()  

    # 面积标注
    Text1=Text(position=Point(1.0, 1.0), 
    text=f"S = {area1:.2f}", 
    color="red")
    # 与x、y轴相交标注
    A_label=Text(position=Point(line_func1.x_intercept(), -0.1), 
    text="A", 
    color="black")
    B_label=Text(position=Point(-0.1, line_func1.y_intercept()), 
    text="B", 
    color="black")
       
    # 绘制一次函数
    line_func2 = LinearFunction(
        k=4,
        b=-3,
        x_range=(-3, 3),
        color="green",
        pensize=4,
        text="y=4x-3",
        text_pos = None,
        fill=True,
        fill_color="green",
        )

    area2=line_func2.area_with_axes()
    # 面积标注
    Text2=Text(position=Point(-1.0, -1.0), 
    text=f"S = {area2:.2f}", 
    color="green")
    # 与x、y轴相交标注
    C_label=Text(position=Point(line_func2.x_intercept(), -0.2), 
    text="C", 
    color="black")
    D_label=Text(position=Point( -0.2, line_func2.y_intercept()), 
    text="D", 
    color="black")

    line_func1.show()
    line_func2.show()
    Text1.show()
    Text2.show()
    A_label.show()
    B_label.show()
    C_label.show()
    D_label.show()

    screen = turtle.Screen()
    screen.update()  # 更新画面

    # 保存图像
    ps_path = os.path.join(IMG_DIR, 'linearfunction.ps')
    png_path = os.path.join(IMG_DIR, 'linearfunction.png')
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
