import numpy as np

x = 1
y = 2
z = 3

m1 = np.zeros([2,3])

print(m1)

m1 = [[x, y, z];[x,x,x]]
m2 = [x, y, z]

print(m1)

for row in m1:
    if(row == m2):
        print("hi")
