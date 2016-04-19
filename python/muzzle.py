import itertools

v = [1,2,3,4,5,6,7,8,9]

class TwoNumber:
    def __init__(self, a, b):
        self.t = a
        self.s = b
        
    @property
    def val(self):
        return self.t * 10 + self.s
        
        
class OneNumber:
    def __init__(self, a):
        self.s = a
        
    @property
    def val(self):
        return self.s
        
def test(l):
    a = TwoNumber(l[0], l[1])
    b = OneNumber(l[2]) 
    c = TwoNumber (l[3], l[4])
    d = TwoNumber (l[5], l[6])
    e = TwoNumber (l[7], l[8])
    
    if a.val * b.val == c.val and c.val + d.val == e.val:
        return True
    return False
    
def main():
    for t in list(itertools.permutations(v, 9)):
        if test(t):
            print t
            return
