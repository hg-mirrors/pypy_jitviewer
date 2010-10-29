
import re

def f():
    i = 0
    while i < 1003:
        i += 1

f()

def inner(i):
    return i + 1

def inlined_call():
    i = 0
    while i < 1003:
        i = inner(i)

inlined_call()

def bridge():
    s = 0
    i = 0
    while i < 3000:
        if i % 2:
            s += 1
        else:
            s += 2
        i += 1
    return s

bridge()

def inlined_str_stuff():
    s = [str(i) for i in range(3000)]
    for elem in s:
        re.search('3', elem)

inlined_str_stuff()
