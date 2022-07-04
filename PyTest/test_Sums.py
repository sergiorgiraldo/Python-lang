from sum import *

def test_sum():
	x=5
	y=6
	assert sum(x,y)== 11,"test failed"

def test_crazySum():
	x=5
	y=6
	assert sum2(x,y)== -1,"test failed"