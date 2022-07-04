import pytest
from arr import supply

@pytest.fixture
def colorsAvailable():
	return ["red","green","white"]

def test_CheckRed(colorsAvailable):
	assert ("red" in colorsAvailable) ,"red not available"

def test_CheckBlack(colorsAvailable):
	assert ("black" in colorsAvailable) ,"black not available"

def test_CheckGreen(colorsAvailable):
	assert ("green" in colorsAvailable) ,"green not available"