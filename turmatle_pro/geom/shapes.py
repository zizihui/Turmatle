from geom.base import Geom, Point
import turtle
import math

class Line(Geom):
    def __init__(
        self,
        start: Point,
        end: Point,
        speed: float = 1,
        pensize: float = 5,
        arrow: bool = False,
        color: str = "black",
        text: str = None,
    ) -> None:
        super().__init__()
        self.start = start
        self.end = end
        self.turtle = turtle.Turtle()
        self.turtle.speed(speed)
        self.pensize = pensize
        self.turtle.pensize(pensize)
        self.turtle.hideturtle()
        self.arrow = arrow
        self.color = color
        self.turtle.color(self.color)
        self.text = text

    def show(self):
        self.turtle.color(self.color)
        self.turtle.pensize(self.pensize)

        x1, y1 = self.start.get_screen_coords()
        x2, y2 = self.end.get_screen_coords()
        self.turtle.penup()
        self.turtle.goto(x1, y1)
        self.turtle.pendown()
        self.turtle.goto(x2, y2)
        self.turtle.penup()
        if self.arrow:
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            self.turtle.setheading(angle)
            self.turtle.stamp()
        if self.text:
            self.turtle.write(
                self.text, 
                font=("Arial", self.fontsize, "normal"), 
                align="right"
            )

    def _scale(self, factor: float):
        """按线段中点缩放"""
        cx = (self.start.x + self.end.x) / 2
        cy = (self.start.y + self.end.y) / 2
        self.start.x = cx + (self.start.x - cx) * factor
        self.start.y = cy + (self.start.y - cy) * factor
        self.end.x = cx + (self.end.x - cx) * factor
        self.end.y = cy + (self.end.y - cy) * factor

    def _snapshot(self):
        return {
            "start": (self.start.x, self.start.y),
            "end": (self.end.x, self.end.y),
            "color": self.color,
            "pensize": self.pensize,
        }

    def _restore(self, state):
        self.start.x, self.start.y = state["start"]
        self.end.x, self.end.y = state["end"]
        self.color = state["color"]
        self.pensize = state["pensize"]

    def clear(self):
        self.turtle.clear()


class Function(Geom):
    def __init__(self, func, x_start=-2, x_end=2, steps=100, 
                 color="blue", pensize=5, text=None, text_pos=None,
                 fill=False, fill_color="lightgray",y_limit=10):  # 添加fill选项
        super().__init__()
        self.func = func
        self.x_start = x_start
        self.x_end = x_end
        self.steps = steps
        self.color = color
        self.pensize = pensize
        self.text = text
        self.text_pos = text_pos if text_pos else (self.x_end, self.func(self.x_end))
        self.fill_color = fill_color
        self.fill = fill  # 是否填充
        self.y_limit = y_limit
        
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.pensize(pensize)
        self.turtle.hideturtle()

    def fill_area(self):
        """填充函数与X轴之间的区域"""
        if not self.fill:  # 如果不需要填充，直接返回
            return
            
        # 关闭动画效果
        screen = self.turtle.getscreen()
        screen.tracer(0)
        
        self.turtle.color(self.fill_color)
        self.turtle.penup()
        
        # 移动到起始点的x轴位置
        start_point = Point(self.x_start, 0)
        start_x, start_y = start_point.get_screen_coords()
            
        self.turtle.goto(start_x, start_y)
        
        self.turtle.begin_fill()
        
        # 画到函数起点
        first_y = self.func(self.x_start)
        # 增加一个小空白
        if first_y > 0:
            first_y = first_y - 0.01
        else:
            first_y = first_y + 0.01
                            
        first_point = Point(self.x_start, first_y)
        fx, fy = first_point.get_screen_coords()
        self.turtle.goto(fx, fy)
                
        # 绘制函数曲线
        dx = (self.x_end - self.x_start) / self.steps
        for i in range(self.steps + 1):
            x = self.x_start + i * dx
            try:
                y = self.func(x)
                # 增加一个小空白
                if y > 0:
                    y = y - 0.01
                else:
                    y = y + 0.01    
                                    
                point = Point(x, y)
                screen_x, screen_y = point.get_screen_coords()            
                self.turtle.goto(screen_x, screen_y)
            except:
                continue
        
        # 画回x轴
        end_point = Point(self.x_end, 0)
        end_x, end_y = end_point.get_screen_coords()
        self.turtle.goto(end_x, end_y)
        
        # 回到起点
        self.turtle.goto(start_x, start_y)
        
        self.turtle.end_fill()
        
        # 重新启用动画效果
        screen.tracer(1)
        screen.update()
        
    def show(self):
        # 画函数曲线
        self.turtle.color(self.color)
        self.turtle.penup()

        dx = (self.x_end - self.x_start) / self.steps

        last_screen_y = None

        for i in range(self.steps + 1):
            x = self.x_start + i * dx
            try:
                y = self.func(x)
            except:
                self.turtle.penup()
                last_screen_y = None
                continue

            # ① 数学层面：y 过大直接断笔
            if abs(y) > self.y_limit:
                self.turtle.penup()
                last_screen_y = None
                continue

            point = Point(x, y)
            screen_x, screen_y = point.get_screen_coords()

            # ② 图形层面：防止跨屏连线
            if last_screen_y is not None:
                if abs(screen_y - last_screen_y) > 200:
                    self.turtle.penup()

            self.turtle.goto(screen_x, screen_y)
            self.turtle.pendown()

            last_screen_y = screen_y

        # 写函数标签 
        if self.text:
            self.turtle.penup()

            tx, ty = self.text_pos

            # 逻辑上仍是 f(x_end)，显示时 clamp
            try:
                y = ty
                if abs(y) > self.y_limit:
                    y = self.y_limit if y > 0 else -self.y_limit
            except:
                y = self.y_limit

            text_point = Point(tx, y)
            text_x, text_y = text_point.get_screen_coords()

            self.turtle.goto(text_x, text_y)
            self.turtle.write(
                self.text,
                font=("Arial", self.fontsize, "normal"),
                align="left"
            )

        # 最后填充
        self.fill_area()

        
    def clear(self):
        self.turtle.clear()

class LinearFunction(Geom):
    def __init__(self, k,               # 斜率k
                 b,                     # 截距b
                 x_range=(-1, 1),       # 自变量x范围
                 color="black",         # 线条颜色
                 pensize=5,             # 线条粗细
                 text="y=kx+b",         # 文本
                 text_pos=None,         # 文本位置
                 fill=False,            # 是否填充
                 fill_color="lightblue"): #填充颜色

        super().__init__()
        self.k = k
        self.b = b
        self.x_start, self.x_end = x_range
        self.color = color
        self.pensize = pensize
        self.text = text
        self.text_pos = text_pos if text_pos else (self.x_end, self.k * self.x_end + self.b)
        self.fill = fill
        self.fill_color = fill_color

        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.speed(0)
        self.turtle.pensize(pensize)

    # 数学属性 
    def f(self, x):
        return self.k * x + self.b

    def x_intercept(self):
        if self.k == 0:
            return None
        return -self.b / self.k

    def y_intercept(self):
        return self.b

    # 绘制直线
    def show(self):
        self.turtle.color(self.color)
        self.turtle.penup()

        p1 = Point(self.x_start, self.f(self.x_start))
        p2 = Point(self.x_end, self.f(self.x_end))

        x1, y1 = p1.get_screen_coords()
        x2, y2 = p2.get_screen_coords()

        self.turtle.goto(x1, y1)
        self.turtle.pendown()
        self.turtle.goto(x2, y2)

        # 标注
        if self.text:
            self.turtle.penup()
            self.turtle.goto(x2, y2)
            self.turtle.write(
                self.text,
                font=("Arial", self.fontsize, "normal"),
                align="left"
            )

        if self.fill:
            self.fill_with_axes()

    # 填充：与 x、y 轴围成面积
    def fill_with_axes(self):
        xi = self.x_intercept()
        yi = self.y_intercept()
        # 只要能形成有限三角形即可
        if xi is None or xi == 0 or yi == 0:
            return
            
        screen = self.turtle.getscreen()
        screen.tracer(0)
        
        self.turtle.color(self.fill_color)
        self.turtle.penup()

        p0 = Point(0, 0).get_screen_coords()
        p1 = Point(xi, 0).get_screen_coords()
        p2 = Point(0, yi).get_screen_coords()
        
        self.turtle.goto(p0)
        self.turtle.begin_fill()
        self.turtle.goto(p1)
        self.turtle.goto(p2)
        self.turtle.goto(p0)
        self.turtle.end_fill()

        screen.tracer(1)
        screen.update()

    # 计算围成面积
    def area_with_axes(self):
        xi = self.x_intercept()
        yi = self.y_intercept()
        if xi is None or xi == 0 or yi == 0:
            return 0

        return abs(xi * yi) / 2

    def clear(self):
        self.turtle.clear()

class QuadraticFunction(Geom):
    def __init__(self,
                 a,                  # 二次函数系数a
                 b=None,             # 二次函数系数b，b=None表示顶点式
                 c=None,             # 二次函数系数c，c=None表示顶点式
                 *,
                 h=None,             # 二次函数顶点坐标h,h=None表示标准式 
                 k=None,             # 二次函数顶点坐标k,k=None表示标准式
                 form="standard",    # 二次函数形式，standard表示标准式，vertex表示顶点式
                 x_range=(-1, 1),    # 自变量x范围
                 color="black",      # 函数颜色
                 pensize=4,          # 线条粗细
                 show_axis=True,     # 是否显示对称轴
                 axis_color="gray",  # 对称轴颜色
                 show_vertex=True,   # 是否显示顶点
                 vertex_color="red", # 顶点颜色
                 text=None,           #文本内容
                 text_pos=None):     #文本位置

        super().__init__()

        # 解析式处理 
        if form == "standard":
            if b is None or c is None:
                raise ValueError("标准式需要 a, b, c")
            self.a = a
            self.b = b
            self.c = c

        elif form == "vertex":
            if h is None or k is None:
                raise ValueError("顶点式需要 a, h, k")
            self.a = a
            self.b = -2 * a * h
            self.c = a * h * h + k

        else:
            raise ValueError("form 必须是 'standard' 或 'vertex'")

        self.x_start, self.x_end = x_range
        self.color = color
        self.pensize = pensize
        self.show_axis = show_axis
        self.axis_color = axis_color
        self.show_vertex = show_vertex
        self.vertex_color = vertex_color
        self.text = text
        self.text_pos = text_pos if text_pos is not None else (self.x_end, self.f(self.x_end))


        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.speed(0)
        self.turtle.pensize(pensize)

    # 数学属性
    def f(self, x):
        return self.a * x * x + self.b * x + self.c

    def axis_of_symmetry(self):
        return -self.b / (2 * self.a)

    def vertex(self):
        xv = self.axis_of_symmetry()
        yv = self.f(xv)
        return xv, yv

    # 绘制函数 
    def show(self):
        self.turtle.color(self.color)
        self.turtle.penup()

        step = (self.x_end - self.x_start) / 200
        x = self.x_start

        p = Point(x, self.f(x))
        self.turtle.goto(*p.get_screen_coords())
        self.turtle.pendown()

        while x <= self.x_end:
            y = self.f(x)
            self.turtle.goto(*Point(x, y).get_screen_coords())
            x += step

        if self.show_axis:
            self.draw_axis()

        if self.show_vertex:
            self.draw_vertex()

        if self.text:
            self.turtle.penup()
            p = Point(*self.text_pos)
            self.turtle.goto(*p.get_screen_coords())
            self.turtle.write(
            self.text,
            font=("Arial", self.fontsize, "normal"),
            align="left")

    def draw_dashed_vertical_line(self, x, y_min, y_max,
                              dash_len=0.05,
                              gap_len=0.05):

        self.turtle.penup()
        self.turtle.color(self.axis_color)
        
        y = y_min
        while y < y_max:
            p1 = Point(x, y)
            p2 = Point(x, min(y + dash_len, y_max))

            self.turtle.goto(*p1.get_screen_coords())
            self.turtle.pendown()
            self.turtle.goto(*p2.get_screen_coords())
            self.turtle.penup()
        
            y += dash_len + gap_len

    # 对称轴
    def draw_axis(self):
        x0 = self.axis_of_symmetry()

        # 给对称轴一个“高度”，避免 y_min == y_max
        y_values = [self.f(x) for x in [self.x_start, self.x_end, x0]]
        y_center = self.f(x0)

        y_min = min(y_values) - 0.5
        y_max = max(y_values) + 0.5

        self.draw_dashed_vertical_line(
            x=x0,
            y_min=y_min,
            y_max=y_max,
            dash_len=0.08,
            gap_len=0.05
            )

    # 顶点 
    def draw_vertex(self):
        xv, yv = self.vertex()
        self.turtle.penup()
        self.turtle.color(self.vertex_color)
        self.turtle.goto(*Point(xv, yv).get_screen_coords())
        self.turtle.dot(7)

    def clear(self):
        self.turtle.clear()


class Rect(Geom):
    def __init__(
        self,
        bottom_left: Point,       # 左下顶点
        top_right: Point,         # 右上顶点
        pivot: str = "center",    # 旋转中心：'center', 'bottom_left', 'bottom_right', 'top_left', 'top_right'
        rotation_deg: float = 0,  # 旋转的角度大小（度数）
        direction: int = 1,       # 旋转方向：1 逆时针，-1 顺时针
        color="blue",
        pensize=4,
        fill_color="lightgray",
        fill=False,
        text=None,
        text_pos=None
    ):
        super().__init__()
        self.bottom_left = bottom_left
        self.top_right = top_right
        self.pivot = pivot
        self.rotation_deg = rotation_deg
        self.direction = direction
        self.color = color
        self.pensize = pensize
        self.fill_color = fill_color
        self.fill = fill
        self.text = text
        # 如果没有指定文本位置，默认放在矩形右上角
        self.text_pos = text_pos if text_pos else (
            top_right.x,
            top_right.y
        )
        
        # 创建背景turtle用于填充
        self.bg_turtle = turtle.Turtle()
        self.bg_turtle.hideturtle()
        self.bg_turtle.speed(0)
        
        # 创建前景turtle用于画线
        self.fg_turtle = turtle.Turtle()
        self.fg_turtle.hideturtle()
        self.fg_turtle.speed(0)
        self.fg_turtle.pensize(pensize)

    def _rotate_point(self, p: Point, center: Point, angle_deg: float) -> Point:
        """将点 p 围绕 center 逆时针旋转 angle_deg（数学坐标系下）"""
        if angle_deg == 0:
            return Point(p.x, p.y)
        theta = math.radians(angle_deg)
        dx = p.x - center.x
        dy = p.y - center.y
        x_new = center.x + dx * math.cos(theta) - dy * math.sin(theta)
        y_new = center.y + dx * math.sin(theta) + dy * math.cos(theta)
        return Point(x_new, y_new)

    def _get_pivot(self, bl: Point, tr: Point, br: Point, tl: Point) -> Point:
        """根据 pivot 字符串返回旋转中心点"""
        if self.pivot == "bottom_left":
            return bl
        elif self.pivot == "bottom_right":
            return br
        elif self.pivot == "top_left":
            return tl
        elif self.pivot == "top_right":
            return tr
        # 默认使用中心点
        cx = (bl.x + tr.x) / 2
        cy = (bl.y + tr.y) / 2
        return Point(cx, cy)

    def fill_area(self):
        """填充矩形区域"""
        if not self.fill:
            return
            
        screen = self.bg_turtle.getscreen()
        screen.tracer(0)
        
        self.bg_turtle.clear()
        self.bg_turtle.color(self.fill_color)
        self.bg_turtle.penup()

        # 计算矩形四个顶点（数学坐标系）
        bl = self.bottom_left
        tr = self.top_right
        br = Point(tr.x, bl.y)
        tl = Point(bl.x, tr.y)

        # 计算旋转中心
        center = self._get_pivot(bl, tr, br, tl)

        angle = self.direction * self.rotation_deg
        bl_r = self._rotate_point(bl, center, angle)
        tl_r = self._rotate_point(tl, center, angle)
        tr_r = self._rotate_point(tr, center, angle)
        br_r = self._rotate_point(br, center, angle)

        # 转为屏幕坐标
        bl_x, bl_y = bl_r.get_screen_coords()
        tl_x, tl_y = tl_r.get_screen_coords()
        tr_x, tr_y = tr_r.get_screen_coords()
        br_x, br_y = br_r.get_screen_coords()
        
        # 开始填充
        self.bg_turtle.goto(bl_x, bl_y)
        self.bg_turtle.begin_fill()
        
        # 按顺序绘制四个顶点
        self.bg_turtle.goto(tl_x, tl_y)
        self.bg_turtle.goto(tr_x, tr_y)
        self.bg_turtle.goto(br_x, br_y)
        self.bg_turtle.goto(bl_x, bl_y)
        
        self.bg_turtle.end_fill()
        screen.update()
        screen.tracer(1)

    def _scale(self, factor: float):
        """按矩形中心缩放"""
        # 原矩形四角
        bl = self.bottom_left
        tr = self.top_right

        # 计算中心点
        cx = (bl.x + tr.x) / 2
        cy = (bl.y + tr.y) / 2

        # 缩放顶点
        self.bottom_left.x = cx + (bl.x - cx) * factor
        self.bottom_left.y = cy + (bl.y - cy) * factor
        self.top_right.x = cx + (tr.x - cx) * factor
        self.top_right.y = cy + (tr.y - cy) * factor

        # 缩放文本位置
        if hasattr(self, "text_pos") and self.text_pos:
            tx, ty = self.text_pos
            self.text_pos = (
                cx + (tx - cx) * factor,
                cy + (ty - cy) * factor
            )

    def show(self):
        # 先在背景填充
        self.fill_area()
        
        # 在前景画边框
        screen = self.fg_turtle.getscreen()
        screen.tracer(0)
        
        self.fg_turtle.color(self.color)
        self.fg_turtle.penup()
        
        # 获取四个顶点的屏幕坐标
        bl = self.bottom_left
        tr = self.top_right
        br = Point(tr.x, bl.y)
        tl = Point(bl.x, tr.y)

        # 计算旋转中心
        center = self._get_pivot(bl, tr, br, tl)

        angle = self.direction * self.rotation_deg
        bl_r = self._rotate_point(bl, center, angle)
        tl_r = self._rotate_point(tl, center, angle)
        tr_r = self._rotate_point(tr, center, angle)
        br_r = self._rotate_point(br, center, angle)

        bl_x, bl_y = bl_r.get_screen_coords()
        tl_x, tl_y = tl_r.get_screen_coords()
        tr_x, tr_y = tr_r.get_screen_coords()
        br_x, br_y = br_r.get_screen_coords()
        
        # 画矩形边框
        self.fg_turtle.goto(bl_x, bl_y)
        self.fg_turtle.pendown()
        self.fg_turtle.goto(tl_x, tl_y)
        self.fg_turtle.goto(tr_x, tr_y)
        self.fg_turtle.goto(br_x, br_y)
        self.fg_turtle.goto(bl_x, bl_y)
        self.fg_turtle.penup()
        
        # 添加文本标签
        if self.text:
            # 文本位置也跟随矩形一起旋转（绕中心）
            base_text_point = Point(self.text_pos[0], self.text_pos[1])
            angle = self.direction * self.rotation_deg
            text_point = self._rotate_point(base_text_point, center, angle)
            text_x, text_y = text_point.get_screen_coords()
            self.fg_turtle.goto(text_x, text_y)
            self.fg_turtle.write(
                self.text, 
                font=("Arial", self.fontsize, "normal"), 
                align="left"
            )
        
        screen.update()
        screen.tracer(1)

    def clear(self):
        """清除所有绘制内容"""
        self.bg_turtle.clear()
        self.fg_turtle.clear()


class Circle(Geom):
    def __init__(
        self,
        center: Point,               # 圆心
        radius: float,               # 半径
        color="blue",
        pensize=5,
        fill_color="lightgray",
        fill=False,
        text=None,
        text_pos=None,  
        show_center=False,           # 是否画圆心点
        center_label=None,           # 圆心标注，如 "O"
        show_radius=False,           # 是否画半径
        radius_endpoint_label=None,  # 半径端点（圆周上）标注，如 "A"
        radius_angle=0,              # 半径方向（度数，0 为向右）
        show_tangent=False,          # 是否画切线
        tangent_angle=0,             # 切点所在角度（度）
        tangent_length=None,         # 切线半长（数学坐标），None 表示自动
        tangent_label=None,           # 切线标注
        tangent_point_label=None,    # 切点标注，如 "P"
    ):
        super().__init__()
        self.center = center
        self.radius = radius
        self.color = color
        self.pensize = pensize
        self.fill_color = fill_color
        self.fill = fill
        self.text = text
        #如果没有指定文本位置，默认在半径右侧
        self.text_pos = text_pos if text_pos else (
            center.x + radius, 
            center.y
        )
        self.show_center = show_center
        self.center_label = center_label
        self.show_radius = show_radius
        self.radius_endpoint_label = radius_endpoint_label
        self.radius_angle = radius_angle
        self.show_tangent = show_tangent        
        self.tangent_angle = tangent_angle
        self.tangent_length = tangent_length
        self.tangent_label = tangent_label
        self.tangent_point_label = tangent_point_label

        self.bg_turtle = turtle.Turtle()
        self.bg_turtle.hideturtle()
        self.bg_turtle.speed(0)

        self.fg_turtle = turtle.Turtle()
        self.fg_turtle.hideturtle()
        self.fg_turtle.speed(0)
        self.fg_turtle.pensize(pensize)

    def fill_area(self):
        """填充圆形区域"""
        if not self.fill:
            return

        screen = self.bg_turtle.getscreen()
        screen.tracer(0)

        self.bg_turtle.clear()
        self.bg_turtle.color(self.fill_color)
        self.bg_turtle.penup()

        cx, cy = self.center.get_screen_coords()
        r_screen = self.radius * self.scale

        # turtle.circle 的圆心在 turtle 左侧；heading=0 时左侧为北，故起点应在圆心正下方
        self.bg_turtle.goto(cx, cy - r_screen)
        self.bg_turtle.setheading(0)
        self.bg_turtle.pendown()
        self.bg_turtle.begin_fill()
        self.bg_turtle.circle(r_screen)
        self.bg_turtle.end_fill()
        self.bg_turtle.penup()

        screen.update()
        screen.tracer(1)

    def show(self):
        self.fill_area()

        screen = self.fg_turtle.getscreen()
        screen.tracer(0)

        self.fg_turtle.color(self.color)
        self.fg_turtle.penup()

        cx, cy = self.center.get_screen_coords()
        r_screen = self.radius * self.scale

        # turtle.circle 的圆心在 turtle 左侧；heading=0 时左侧为北，故起点应在圆心正下方
        self.fg_turtle.goto(cx, cy - r_screen)
        self.fg_turtle.setheading(0)
        self.fg_turtle.pendown()
        self.fg_turtle.circle(r_screen)
        self.fg_turtle.penup()

        if self.text:
            tx, ty = Point(self.text_pos[0], self.text_pos[1]).get_screen_coords()
            self.fg_turtle.goto(tx, ty)
            self.fg_turtle.write(
                self.text,
                font=("Arial", self.fontsize, "normal"),
                align="left"
            )

        # 画半径（圆心 O 到圆周上一点 A）
        if self.show_radius:
            theta = math.radians(self.radius_angle)
            ax = self.center.x + self.radius * math.cos(theta)
            ay = self.center.y + self.radius * math.sin(theta)
            ax_s, ay_s = Point(ax, ay).get_screen_coords()
            self.fg_turtle.color(self.color)
            self.fg_turtle.goto(cx, cy)
            self.fg_turtle.pendown()
            self.fg_turtle.goto(ax_s, ay_s)
            self.fg_turtle.penup()
            if self.radius_endpoint_label:
                offset = self.fontsize * 0.4
                self.fg_turtle.goto(ax_s + offset, ay_s + offset)
                self.fg_turtle.write(
                    self.radius_endpoint_label,
                    font=("Arial", self.fontsize, "normal"),
                    align="center"
                )

        # 画圆心点
        if self.show_center:
            self.fg_turtle.goto(cx, cy)
            self.fg_turtle.dot(max(4, self.pensize * 2))
            if self.center_label:
                offset = self.fontsize * 0.8
                self.fg_turtle.goto(cx - offset, cy - offset)
                self.fg_turtle.write(
                    self.center_label,
                    font=("Arial", self.fontsize, "normal"),
                    align="center"
                )

        # 画切线
        if self.show_tangent:
            theta = math.radians(self.tangent_angle)

            # 切点 P（数学坐标）
            px = self.center.x + self.radius * math.cos(theta)
            py = self.center.y + self.radius * math.sin(theta)

            # 切线方向（垂直于半径）
            phi = theta + math.pi / 2
           
            L = self.tangent_length if self.tangent_length else self.radius * 1.5
           
            x1 = px + L * math.cos(phi)
            y1 = py + L * math.sin(phi)
            x2 = px - L * math.cos(phi)
            y2 = py - L * math.sin(phi)

            p1x, p1y = Point(x1, y1).get_screen_coords()
            p2x, p2y = Point(x2, y2).get_screen_coords()
            px_s, py_s = Point(px, py).get_screen_coords()
            
            self.fg_turtle.color(self.color)
            self.fg_turtle.goto(p1x, p1y)
            self.fg_turtle.pendown()
            self.fg_turtle.goto(p2x, p2y)
            self.fg_turtle.penup()

        #标注切点
        if self.tangent_point_label:
            self.fg_turtle.goto(px_s, py_s)
            self.fg_turtle.dot(max(4, self.pensize * 2))
            offset = self.fontsize * 0.3
            self.fg_turtle.goto(px_s + offset, py_s + offset)
            self.fg_turtle.write(
                self.tangent_point_label,
                font=("Arial", self.fontsize, "normal"),
                align="center"
            )
        
        #标注直线
        if self.tangent_label:
            d1 = (p1x - cx)**2 + (p1y - cy)**2
            d2 = (p2x - cx)**2 + (p2y - cy)**2

            if d1 > d2:
                tailx, taily = p1x, p1y
                sign = 1
            else:
                tailx, taily = p2x, p2y
                sign = -1

            offset = self.fontsize * 0.8
            dx = sign * offset * math.cos(phi)
            dy = sign * offset * math.sin(phi)

            self.fg_turtle.goto(tailx + dx, taily + dy)
            self.fg_turtle.write(
                self.tangent_label,
                font=("Arial", self.fontsize, "normal"),
                align="center"
            )


        screen.update()
        screen.tracer(1)

    def _scale(self, factor: float):
        """按圆心缩放"""
        self.radius *= factor
        if hasattr(self, "text_pos") and self.text_pos:
            cx, cy = self.center.x, self.center.y
            tx, ty = self.text_pos
            self.text_pos = (
                cx + (tx - cx) * factor,
                cy + (ty - cy) * factor,
            )

    def _snapshot(self):
        return {
            "radius": self.radius,
            "text_pos": self.text_pos,
            "color": self.color,
            "pensize": self.pensize,
        }

    def _restore(self, state):
        self.radius = state["radius"]
        self.text_pos = state["text_pos"]
        self.color = state["color"]
        self.pensize = state["pensize"]

    def clear(self):
        self.bg_turtle.clear()
        self.fg_turtle.clear()

class Triangle(Geom):
    def __init__(
        self,
        p1: Point = None,
        p2: Point = None,
        p3: Point = None,
        sides=None,                  # (a,b,c) 或 (a,b)
        angle: float = None,         # 两边夹角（度）
        pivot="center",              # 旋转中心："center" / "p1" / "p2" / "p3" / Point
        rotation_deg: float = 0,     # 旋转角度（度）
        direction: int = 1,          # 1 逆时针，-1 顺时针
        color="black",
        pensize=5,
        fill=False,
        fill_color="lightgray",
        text=None,
        text_pos=None
    ):
        super().__init__()

        self.pivot = pivot
        self.rotation_deg = rotation_deg
        self.direction = direction
        self.color = color
        self.pensize = pensize
        self.fill = fill
        self.fill_color = fill_color
        self.text = text

        # ---------- 构造三角形 ----------
        if p1 and p2 and p3:
            self.p1, self.p2, self.p3 = p1, p2, p3

        elif sides and len(sides) == 3:
            self._build_from_three_sides(*sides)

        elif sides and angle:
            self._build_from_two_sides_angle(sides[0], sides[1], angle)

        else:
            raise ValueError("Triangle 构造参数不合法")

        # ---------- 文本位置 ----------
        self.text_pos = text_pos if text_pos else self._compute_text_pos_right_edge()

        # ---------- 边长 ----------
        self.a = self._dist(self.p2, self.p3)
        self.b = self._dist(self.p1, self.p3)
        self.c = self._dist(self.p1, self.p2)

        # ---------- 类型判断 ----------
        self.is_right = self._is_right()
        self.is_isosceles = self._is_isosceles()
        self.is_equilateral = self._is_equilateral()

        # ---------- turtle ----------
        self.bg_turtle = turtle.Turtle()
        self.bg_turtle.hideturtle()
        self.bg_turtle.speed(0)

        self.fg_turtle = turtle.Turtle()
        self.fg_turtle.hideturtle()
        self.fg_turtle.speed(0)
        self.fg_turtle.pensize(self.pensize)

    # 构造方法
    def _build_from_three_sides(self, a, b, c):
        A = Point(0, 0)
        B = Point(c, 0)

        cos_C = (a*a + b*b - c*c) / (2*a*b)
        cos_C = max(min(cos_C, 1), -1)

        Cx = b * cos_C
        Cy = math.sqrt(max(b*b - Cx*Cx, 0))

        C = Point(Cx, Cy)
        self.p1, self.p2, self.p3 = A, B, C

    def _build_from_two_sides_angle(self, a, b, angle_deg):
        A = Point(0, 0)
        B = Point(a, 0)

        theta = math.radians(angle_deg)
        C = Point(
            b * math.cos(theta),
            b * math.sin(theta)
        )

        self.p1, self.p2, self.p3 = A, B, C

    # 旋转相关
    def _rotate_point(self, p: Point, center: Point, angle_deg: float) -> Point:
        if angle_deg == 0:
            return Point(p.x, p.y)

        theta = math.radians(angle_deg)
        dx = p.x - center.x
        dy = p.y - center.y

        return Point(
            center.x + dx * math.cos(theta) - dy * math.sin(theta),
            center.y + dx * math.sin(theta) + dy * math.cos(theta)
        )

    def _get_pivot(self) -> Point:
        if isinstance(self.pivot, Point):
            return self.pivot

        if self.pivot == "p1":
            return self.p1
        if self.pivot == "p2":
            return self.p2
        if self.pivot == "p3":
            return self.p3

        # 默认重心
        cx = (self.p1.x + self.p2.x + self.p3.x) / 3
        cy = (self.p1.y + self.p2.y + self.p3.y) / 3
        return Point(cx, cy)

    def _get_rotated_points(self):
        center = self._get_pivot()
        angle = self.direction * self.rotation_deg

        return (
            self._rotate_point(self.p1, center, angle),
            self._rotate_point(self.p2, center, angle),
            self._rotate_point(self.p3, center, angle),
        )

    # ==================================================
    # 文本位置（最右边外法向）
    # ==================================================
    def _compute_text_pos_right_edge(self, offset=0.3):
        edges = [
            (self.p1, self.p2),
            (self.p2, self.p3),
            (self.p3, self.p1),
        ]

        A, B = max(edges, key=lambda e: (e[0].x + e[1].x) / 2)

        mx = (A.x + B.x) / 2
        my = (A.y + B.y) / 2

        dx = B.x - A.x
        dy = B.y - A.y

        nx, ny = dy, -dx
        length = math.hypot(nx, ny)
        nx /= length
        ny /= length

        return (mx + nx * offset, my + ny * offset)

    # ==================================================
    # 几何判断
    # ==================================================
    def _is_right(self, eps=1e-6):
        sides = sorted([self.a, self.b, self.c])
        return abs(sides[0]**2 + sides[1]**2 - sides[2]**2) < eps

    def _is_isosceles(self, eps=1e-6):
        return (
            abs(self.a - self.b) < eps or
            abs(self.b - self.c) < eps or
            abs(self.a - self.c) < eps
        )

    def _is_equilateral(self, eps=1e-6):
        return abs(self.a - self.b) < eps and abs(self.b - self.c) < eps

    def _dist(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    # ==================================================
    # 填充
    # ==================================================
    def fill_area(self):
        if not self.fill:
            return

        screen = self.bg_turtle.getscreen()
        screen.tracer(0)

        self.bg_turtle.clear()
        self.bg_turtle.color(self.fill_color)
        self.bg_turtle.penup()

        p1, p2, p3 = self._get_rotated_points()

        for i, p in enumerate([p1, p2, p3, p1]):
            x, y = p.get_screen_coords()
            self.bg_turtle.goto(x, y)
            if i == 0:
                self.bg_turtle.begin_fill()

        self.bg_turtle.end_fill()
        screen.update()
        screen.tracer(1)

    def _scale(self, factor: float):
        """按重心缩放三角形"""
        # 计算重心
        cx = (self.p1.x + self.p2.x + self.p3.x) / 3
        cy = (self.p1.y + self.p2.y + self.p3.y) / 3

        # 缩放三角形顶点
        for p in [self.p1, self.p2, self.p3]:
            p.x = cx + (p.x - cx) * factor
            p.y = cy + (p.y - cy) * factor

        # 缩放文本位置
        if hasattr(self, "text_pos") and self.text_pos:
            tx, ty = self.text_pos
            self.text_pos = (
                cx + (tx - cx) * factor,
                cy + (ty - cy) * factor
            )

        # 缩放后更新边长
        self.a = self._dist(self.p2, self.p3)
        self.b = self._dist(self.p1, self.p3)
        self.c = self._dist(self.p1, self.p2)

    # 显示
    def show(self):
        self.fill_area()

        screen = self.fg_turtle.getscreen()
        screen.tracer(0)

        self.fg_turtle.clear()
        self.fg_turtle.color(self.color)
        self.fg_turtle.penup()

        p1, p2, p3 = self._get_rotated_points()

        for p in [p1, p2, p3, p1]:
            x, y = p.get_screen_coords()
            self.fg_turtle.goto(x, y)
            self.fg_turtle.pendown()

        self.fg_turtle.penup()

        # 文本（随旋转）
        if self.text:
            base = Point(*self.text_pos)
            center = self._get_pivot()
            angle = self.direction * self.rotation_deg
            tp = self._rotate_point(base, center, angle)

            x, y = tp.get_screen_coords()
            self.fg_turtle.goto(x, y)
            self.fg_turtle.write(
                self.text,
                font=("Arial", self.fontsize, "normal"),
                align="center"
            )

        screen.update()
        screen.tracer(1)

    def clear(self):
        self.bg_turtle.clear()
        self.fg_turtle.clear()
