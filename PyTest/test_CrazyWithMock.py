from sum import sum2

def test_CrazySum_Mocked(mocker): #pip install pytest-mock
    def realSum(x,y):
        return (x+y)

    mocker.patch(
        "sum.crazy", realSum
    )
    actual = sum2(5,6)
    expected = 11
    assert expected == actual