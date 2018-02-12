import unittest

import stmts

class TestStatements(unittest.TestCase):
	__slots__ = ()
	
	def test_expr_parse(self):
		e = stmts.parse_expr('a')
		self.assertEquals(stmts.var_expr('a'), e)
		
		e = stmts.parse_expr('1')
		self.assertEquals(stmts.literal_expr(1), e)
		
		e = stmts.parse_expr('f(x)')
		self.assertEquals(stmts.call_expr('f', (stmts.var_expr('x'),)), e)
		
		e = stmts.parse_expr('a, f(x)')
		self.assertEquals(stmts.tuple_expr((stmts.var_expr('a'), stmts.parse_expr('f(x)'))), e)
	
	def test_stmt_parse(self):
		s = stmts.parse_stmt('null')
		self.assertEquals(stmts.null_stmt(), s)
		
		s = stmts.parse_stmt('let a := 1')
		self.assertEquals(stmts.let_stmt(('a',), stmts.parse_expr('1')), s)
		
		s = stmts.parse_stmt('let a, b := f(x), 1')
		self.assertEquals(stmts.let_stmt(('a', 'b'), stmts.parse_expr('f(x), 1')), s)
		
		s = stmts.parse_stmt('branch 1')
		self.assertEquals(stmts.branch_stmt(stmts.parse_expr('1')), s)

if __name__ == '__main__':
	unittest.main()
