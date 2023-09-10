import something
import somethingelse as otherelse
from somewhere import otherthing
from over import the as rainbow
import seethree

var = "hello"
var2 = var.split()
var3 = "bye"


def func(arg):
    print(arg)
    print(var2)


class clas():
    def clasfunc(arg):
        print(arg)


inst = clas()
inst.clasfunc(var3)


def dep2(arg):
    print(arg)
    seethree.dep1(var)
