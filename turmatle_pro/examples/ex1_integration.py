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
    Geom.set_defaults(origin_x=-1, origin_y=-0.5, scale=150, fontsize=25)

    WIDTH, HEIGHT = 1000, 1000
    IMG_DIR = os.path.join(project_root, 'examples/images')
    os.makedirs(IMG_DIR, exist_ok=True) # 创建images目录

    # 创建坐标轴
    x_axis = Line(Point(-2, 0), Point(3.5, 0), 
                speed=0, pensize=3, 
                color="gray", text="x",
                arrow=True)
    y_axis = Line(Point(0, -2), Point(0, 2), 
                speed=0, pensize=3,
                color="gray", text="y",
                arrow=True)

    # 显示坐标轴
    x_axis.show()
    y_axis.show()

    # 绘制被积函数
    sin_func = Function(
        math.sin,               # 函数名
        x_start=-1/2*math.pi,              # 自变量起始点
        x_end=math.pi,      # 自变量终点
        color="black",          # 函数颜色
        pensize=5,              # 线条粗细
        text="sin(x)",          # 文本内容
        fill=True,              # 是否填充
        fill_color="azure",      # 填充颜色
        #text_pos=(0, 1)        # 文本位置，默认自变量右端点，在 (0,1) 位置显示文本
        y_limit=10              # 防止y爆炸
    )
    sin_func.show()

    # 计算黎曼和
    N = 100                      # 区间分成 N 份
    
    dx = (sin_func.x_end - sin_func.x_start) / N        
    
    S = 0
    for i in range(N):
        x_l = sin_func.x_start + i*dx
        x_r = sin_func.x_start + (i+1)*dx 
        x_i = x_l
        y_i = math.sin(x_i)
        A_i = y_i * (x_r - x_l)
        S = S + A_i
        
        rect1 = Rect(
            bottom_left=Point(x_l, 0),
            top_right=Point(x_r, y_i),
            color="blue",
            pensize=1,
            fill_color="lightblue",
            fill=True
        )
        rect1.show()
    
    if 'text' in locals():
        text.clear()
        
    text = Text(
        position=Point(0.6, 1.1),
        text=f'S({N}) = {S:.2f}',
        color="green",
        align="center",
        bold=True,
        italic=True
    )        
    text.show()
    text.play(Outline())
    
    screen = turtle.Screen()
    screen.update()  # 更新画面
    
    # 保存图像
    ps_path = os.path.join(IMG_DIR, 'ex1_integration.ps')
    png_path = os.path.join(IMG_DIR, 'ex1_integration.png')
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
