import math

class Pager:
    
    def __init__(self, total: int, page_num: int, page_size: int):
        self.total = total
        self.page_num = page_num
        self.set_page_size(page_size)

    def set_page_size(self, page_size: int):
        if (self.total < page_size or page_size < 1) and self.total > 0:
            self.page_size = self.total
        else:
            self.page_size = page_size

        if self.total_pages < self.page_num:
            self.page_num = self.total_pages

        if self.page_num < 1:
            self.page_num = 1

    @property
    def lower_bound(self):
        return (self.page_num - 1) * self.page_size

    @property
    def upper_bound(self):
        x = self.page_num * self.page_size
        if self.total < x:
            x = self.total
        return x

    @property
    def total_pages(self):
        v = self.total * 1.00 / self.page_size
        x = math.ceil(v)
        return x