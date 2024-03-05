from math import factorial
nums = [13,10,35,24,76]
a = [abs(i - int(str(i)[::-1])) for i in nums]
print(a)
b = []
res = 0
for i in a:
    x = a.count(i)
    if i in b or x == 1:
        continue
    elif x == 2:
        b.append(i)
        res+=1
    else:
        b.append(i)
        res += factorial(x)//(factorial(x-2)*2)
    print(b)
print(res)