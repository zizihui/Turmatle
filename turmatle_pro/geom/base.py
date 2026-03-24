import turtle
import math
import sys

class Geom:
    # 设置类变量作为默认值
    default_origin_x = 0
    default_origin_y = 0
    default_scale = 100
    default_fontsize = 25

    @classmethod
    def set_defaults(cls, origin_x=0, origin_y=0, scale=100, fontsize=25):
        cls.default_origin_x = origin_x
        cls.default_origin_y = origin_y
        cls.default_scale = scale
        cls.default_fontsize = fontsize

    @staticmethod
    def setup_canvas(width=1000, height=1000):
        """初始化画布：DPI 感知 + 窗口大小 + Tk 缩放，与 Turmatle Engine 保持一致"""
        # Windows DPI 感知
        if sys.platform == 'win32':
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception:
                try:
                    import ctypes
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass

        turtle.clearscreen()
        screen = turtle.Screen()

        # 禁用 Tk 额外的 DPI 缩放
        try:
            tk_obj = getattr(screen, '_root', None)
            if tk_obj is not None:
                tk_obj.tk.call('tk', 'scaling', 1.0)
            else:
                tk_fallback = screen.cv._rootwindow
                tk_fallback.tk.call('tk', 'scaling', 1.0)
        except Exception:
            pass

        screen.setup(width, height)
        screen.tracer(0)
        return screen

    def __init__(
        self,
        origin_x: float = None,
        origin_y: float = None,
        scale: float = None,
        fontsize: int = None,
    ) -> None:    
        self.origin_x = self.default_origin_x if origin_x is None else origin_x
        self.origin_y = self.default_origin_y if origin_y is None else origin_y
        self.scale = self.default_scale if scale is None else scale
        self.fontsize = self.default_fontsize if fontsize is None else fontsize

    def play(self, *effects):
        """对当前对象依次施加效果"""
        for eff in effects:
            eff.apply(self)

    def _snapshot(self):
        """自动捕获视觉属性，子类也可覆盖扩展"""
        snap = {}
        for attr in ("color", "pensize", "fill_color", "fontsize"):
            if hasattr(self, attr):
                snap[attr] = getattr(self, attr)
        return snap
    
    def _restore(self, state: dict):
        for k, v in state.items():
            setattr(self, k, v)
        
    def _scale(self, factor: float):
        """数学意义下的缩放（子类实现）"""
        pass

class Point(Geom):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

    def get_screen_coords(self):
        screen_x = (self.x + self.origin_x) * self.scale
        screen_y = (self.y + self.origin_y) * self.scale
        return screen_x, screen_y

    def __repr__(self):
        return f'Point({self.x}, {self.y})'
