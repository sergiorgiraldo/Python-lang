import numpy as np


def p(what):
    print(what, "\n")


a = np.zeros(10)
p("zeroes vector 10")
p(a)

b = np.zeros((3, 2))
p("zeroes 3X2")
p(b)

c = np.ones(10)
p("ones vector 10")
p(c)

d = np.ones((3, 2))
p("ones 3X2")
p(d)

e = np.full((5, 2), 'a')  # matrix 5 lines, 2 columns, all values 'a'
p(e)

f = np.eye(3)  # identity matrix
p(f)

g = np.random.random((2,2))
p(g)
p(g[1])  # second row
p(g[:,1])  # second column

a1 = np.arange(10, 31, 1)
a2 = np.full(21, 3)
a3 = np.multiply(a1, a2)
a4 = np.divide(a1, a2)
a5 = a1 * a2
p(a1)
p(len(a1))
p(a2)
p(len(a2))
p(a3)
p(a4)
p(a5)
p(np.sum(a1))
p(np.mean(a1))
p(np.std(a1))
xx = np.array([[1, 2], [3, 4]])
p(np.ndarray.flatten(xx))

