import time

class Effect:
    def apply(self, geom):
        raise NotImplementedError


# 闪烁（Flash）
class Flash(Effect):
    def __init__(self, times=2, duration=1):
        """
        times: 闪烁次数
        duration: 每次闪烁持续时间（on + off 可拆分）
        """
        self.times = times
        self.on = duration / 2
        self.off = duration / 4

    def apply(self, geom):
        # 找一个 screen
        screen = None
        for attr in ("fg_turtle", "bg_turtle", "turtle"):
            if hasattr(geom, attr):
                screen = getattr(geom, attr).getscreen()
                break

        if screen is None:
            return

        screen.tracer(0)

        for _ in range(self.times):
            # 关
            geom.clear()
            screen.update()
            time.sleep(self.off)

            # 开
            geom.show()
            screen.tracer(0)
            screen.update()
            time.sleep(self.on)

        screen.tracer(1)
        screen.update()


# 描边 / 高亮（Outline）
class Outline(Effect):
    def __init__(self, color="red", pensize_boost=8, duration=1):
        self.color = color
        self.pensize_boost = pensize_boost
        self.duration = duration

    def apply(self, geom):
        state = geom._snapshot()

        # 获取 screen，用于 tracer 控制
        screen = None
        for attr in ("fg_turtle", "bg_turtle", "turtle"):
            if hasattr(geom, attr):
                screen = getattr(geom, attr).getscreen()
                break

        # 是否有独立前景 turtle
        has_fg = hasattr(geom, "fg_turtle")
        orig_fill = getattr(geom, "fill", None)

        if screen:
            screen.tracer(0)

        # 帧1：原始形状
        geom.clear()
        geom.show()
        if screen:
            screen.tracer(0)
            screen.update()
        time.sleep(self.duration / 2)

        # 帧2：描边高亮（只刷前景描边，填充不动）
        if hasattr(geom, "color"):
            geom.color = self.color
        if hasattr(geom, "pensize"):
            geom.pensize += self.pensize_boost

        if has_fg:
            geom.fg_turtle.clear()
            geom.fill = False
            geom.show()
            geom.fill = orig_fill
        else:
            geom.clear()
            geom.show()
        if screen:
            screen.tracer(0)
            screen.update()
        time.sleep(self.duration / 2)

        # 帧3：恢复原状态（同样只刷前景）
        geom._restore(state)
        if has_fg:
            geom.fg_turtle.clear()
            geom.fill = False
            geom.show()
            geom.fill = orig_fill
        else:
            geom.clear()
            geom.show()
        if screen:
            screen.update()
            screen.tracer(1)


# 缩放强调（Scale）
class Scale(Effect):
    def __init__(self, factor=1.2, duration=1):
        self.factor = factor
        self.duration = duration

    def apply(self, geom):
        if not hasattr(geom, "_scale"):
            return

        screen = None
        for attr in ("fg_turtle", "bg_turtle", "turtle"):
            if hasattr(geom, attr):
                screen = getattr(geom, attr).getscreen()
                break

        if screen:
            screen.tracer(0)

        # 先画原始大小
        geom.clear()
        geom.show()
        if screen:
            screen.tracer(0)
            screen.update()
        time.sleep(self.duration / 2)

        # 放大
        geom._scale(self.factor)
        geom.clear()
        geom.show()
        if screen:
            screen.tracer(0)
            screen.update()
        time.sleep(self.duration / 2)

        # 恢复原大小
        geom._scale(1 / self.factor)
        geom.clear()
        geom.show()
        if screen:
            screen.update()
            screen.tracer(1)

# 组合强调（Indicate）
class Indicate(Effect):
    """
    Manim 风格 Indicate：
    - 先显示原始形状
    - 放大
    - 描边
    - 闪一下
    """
    def __init__(
        self,
        scale_factor=1.2,
        color="orange",
        pensize_boost=8,
        duration=1
    ):
        self.scale = Scale(scale_factor, duration)
        self.outline = Outline(color, pensize_boost, duration)
        self.flash = Flash(times=2, duration=duration)

    def apply(self, geom):
        screen = None
        for attr in ("fg_turtle", "bg_turtle", "turtle"):
            if hasattr(geom, attr):
                screen = getattr(geom, attr).getscreen()
                break

        # ---------- 先显示原始形状 ----------
        if screen:
            screen.tracer(0)
        geom.clear()
        geom.show()
        if screen:
            screen.tracer(0)
            screen.update()
        time.sleep(self.scale.duration / 2)
        if screen:
            screen.tracer(1)

        # ---------- 放大 ----------
        self.scale.apply(geom)

        # ---------- 描边 ----------
        self.outline.apply(geom)

        # ---------- 闪烁 ----------
        self.flash.apply(geom)
