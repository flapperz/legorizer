class Brick():
    def __init__(self,w,h):
        self.w = w
        self.h = h
        self.area = w*h

    def __str__(self):
        return "wide = {}, height = {}, area = {}".format(self.w, self.h, self.area)

    def __repr__(self):
        return "Brick {}x{}".format(self.w, self.h)
    
    def __eq__(self, other):
        return self.w == other.w and self.h == other.h
    
    def GetBoundary(self, x, y):
        ''' beginx, endx, beginy, endy'''
        return int( x - self.w/2 + 0.5 ), int( x + self.w/2 + 0.5 ), int( y - self.h/2 + 0.5 ), int( y + self.h/2 + 0.5 )