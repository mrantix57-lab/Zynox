import colorsys


class Rainbow:
    def __init__(self, lo=0.52, hi=0.98, step=0.006, s=0.85, v=0.95):
        self.lo, self.hi = lo, hi
        self.hue = lo
        self.step = step
        self.s, self.v = s, v

    def tick(self):
        self.hue += self.step
        if self.hue > self.hi:
            self.hue = self.lo
        return self

    def color(self, s=None, v=None):
        r, g, b = colorsys.hsv_to_rgb(self.hue, s if s is not None else self.s,
                                      v if v is not None else self.v)
        return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))

    def dark(self):
        return self.color(s=0.55, v=0.22)
