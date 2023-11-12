import codewars_test as test
from solution import calculator

@test.describe("Fixed Tests")
def fixed_tests():
    @test.it('Simple Test Cases')
    def simple_test():
        test.assert_equals(calculator(6, 2, '+'),8)
        test.assert_equals(calculator(4, 3, '-'),1)
        test.assert_equals(calculator(5, 5, '*'),25)
        test.assert_equals(calculator(5, 4, '/'),1.25)
        test.assert_equals(calculator(6, 2, '&'),"unknown value");