
from reportlab.lib.units import mm, inch
from reportlab.lib.utils import ImageReader

from PIL import Image

def to_inches(*lengths):
    return [i * inch for i in lengths]

def to_mm(*lengths):
    return [i * mm for i in lengths]

def scale_with_max(sizes, max_sizes, order=(1, 0)):
    for i in order:
        ok = True
        answer = [size * max_sizes[i] / sizes[i] for size in sizes]
        for observed, maximum in zip(answer, max_sizes):
            if observed > maximum:
                ok = False
            if ok:
                return answer

def test_scale_with_max():
    assert scale_with_max([1, 1], [2, 2]) == [2, 2]
    assert scale_with_max([1, 1], [2, 1]) == [1, 1]
    assert scale_with_max([123, 456], [123, 456/2]) == [123/2, 456/2]


def image_size_raw(filepath, max_height, max_width):
    with Image.open(filepath) as im:
        return scale_with_max(im.size, (max_width, max_height))

def image_size_to_inches(filepath, max_height_inches, max_width_inches):
    with Image.open(filepath) as im:
        return scale_with_max(im.size, to_inches(max_width, max_height))

class LogoProvider(object):
    def __init__(self, filepath, min_value, max_value, iterations=8):
        self.current_scale = 0
        self.filepath = filepath
        self.min_value = min_value
        self.max_value = max_value
        self.iterations = iterations
        self.current_iteration = 0.0
        if self.iterations == 1:
            self.step = 0
        else:
            self.step = float(self.max_value - self.min_value) / (self.iterations - 1)
        self.cache = dict()
        if filepath is not None:
            self.image = Image.open(filepath)

    def get_next_scale(self):
        answer = self.min_value + (self.step * self.current_iteration)
        self.current_iteration += 1
        self.current_iteration %= self.iterations
        return answer

    def get_image(self):
        # return self.image.point(lambda x: min(255, x * self.get_next_scale()))
        self.current_scale = self.get_next_scale()
        if self.current_iteration not in self.cache:
            # print "Calculating image for iteration {}".format(self.current_iteration)
            answer = self.image.copy()
            answer.putalpha(int(self.current_scale))
            self.cache[self.current_iteration] = answer
        return self.cache[self.current_iteration]

    def get_image_reader(self):
        return ImageReader(self.get_image())

    def image_size_raw(self, max_width, max_height):
        return scale_with_max(self.image.size, (max_width, max_height))

def test_logo_provider():
    lp = LogoProvider(None, 4, 8, iterations=9)
    assert lp.get_next_scale() == 4
    assert lp.get_next_scale() == 4.5
    assert lp.get_next_scale() == 5
    assert lp.get_next_scale() == 5.5
    assert lp.get_next_scale() == 6
    assert lp.get_next_scale() == 6.5
    assert lp.get_next_scale() == 7
    assert lp.get_next_scale() == 7.5
    assert lp.get_next_scale() == 8
    assert lp.get_next_scale() == 4
    assert lp.get_next_scale() == 4.5
    assert lp.get_next_scale() == 5
    assert lp.get_next_scale() == 5.5
    assert lp.get_next_scale() == 6
    assert lp.get_next_scale() == 6.5
    assert lp.get_next_scale() == 7
    assert lp.get_next_scale() == 7.5
    assert lp.get_next_scale() == 8
    assert lp.get_next_scale() == 4
