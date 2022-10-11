import math
import latexify

@latexify.with_latex
def sinc(x):
    if x == 0:
        return 1
    else:
        return math.sin(x) / x

sinc(1)
