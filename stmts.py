import operator
import re

# expressions occuring in a cfg

class expr(object):
	__slots__ = ()
	def __str__(self): abstract
	def variables(self): abstract

class var_expr(expr):
	__slots__ = ('var',)
	def __init__(self, var): self.var = var
	def __str__(self): return self.var
	def __eq__(self, other):
		return type(self) == type(other) and self.var == other.var
	def variables(self):
		return frozenset((self.var,))

class literal_expr(expr):
	__slots__ = ('value',)
	def __init__(self, value): self.value = value
	def __str__(self): return repr(self.value)
	def __eq__(self, other):
		return type(self) == type(other) and self.value == other.value
	def variables(self):
		return frozenset()

class call_expr(expr):
	__slots__ = ('fn', 'operands')
	def __init__(self, fn, operands):
		self.fn = fn
		self.operands = tuple(operands)
	def __str__(self):
		return '%s(%s)' % (self.fn, ', '.join(str(o) for o in self.operands))
	def __eq__(self, other):
		return type(self) == type(other) and self.fn == other.fn and self.operands == other.operands
	def variables(self):
		return reduce(operator.or_, (op.variables() for op in self.operands), frozenset())

class tuple_expr(expr):
	__slots__ = ('items',)
	def __init__(self, items):
		self.items = tuple(items)
	def __str__(self):
		return '(%s)' % ', '.join(str(o) for o in self.items)
	def __eq__(self, other):
		return type(self) == type(other) and len(self.items) == len(other.items) and self.items == other.items
	def variables(self):
		return reduce(operator.or_, (it.variables() for it in self.items), frozenset())

class rvsdg_loop_expr(expr):
	__slots__ = ('region', 'label', 'operands')
	
	def __init__(self, region, label, operands):
		assert all(isinstance(e, expr) for e in operands)
		self.region = region
		self.label = label
		self.operands = operands
	def __str__(self):
		return '%s<%s>(%s)' % (self.label, self.region, ', '.join(str(o) for o in self.operands))
	def variables(self):
		return reduce(operator.or_, (op.variables() for op in self.operands), frozenset())

# statements occuring in a cfg

class stmt(object):
	__slots__ = ()
	def __str__(self): abstract
	def __ne__(self, other): return not self == other

class null_stmt(stmt):
	__slots__ = ()
	def __str__(self): return 'null'
	def __eq__(self, other): return type(self) == type(other)

class let_stmt(stmt):
	__slots__ = ('vars', 'expr')
	
	def __init__(self, vars, expr):
		self.vars = tuple(vars)
		self.expr = expr
	
	def __str__(self):
		return 'let %s := %s' % (', '.join(v for v in self.vars), str(self.expr))
	
	def __eq__(self, other):
		return type(self) == type(other) and self.vars == other.vars and self.expr == other.expr

class branch_stmt(stmt):
	__slots__ = ('expr',)
	
	def __init__(self, e):
		assert isinstance(e, expr), type(e)
		self.expr = e
	
	def __str__(self):
		return 'branch %s' % str(self.expr)
	
	def __eq__(self, other):
		return type(self) == type(other) and self.expr == other.expr

# parsing of stuff

identifier_pattern = re.compile('^[a-zA-Z_][a-zA-Z_0-9]*$')
literal_pattern = re.compile('^(-?[0-9]+)$')
call_pattern = re.compile('^([a-zA-Z_][a-zA-Z_0-9]*) *\\((.*)\\)')

def parse_expr(string):
	string = string.strip()
	m = identifier_pattern.match(string)
	if m:
		return var_expr(string)
	m = literal_pattern.match(string)
	if m:
		return literal_expr(int(string))
	m = call_pattern.match(string)
	if m:
		fn = m.group(1)
		ops = parse_expr(m.group(2))
		if isinstance(ops, tuple_expr):
			return call_expr(fn, ops.items)
		else:
			return call_expr(fn, (ops,))
	
	items = []
	current = ''
	n = 0
	for c in string:
		if c == ',' and n == 0:
			items.append(current.strip())
			current = ''
		else:
			if c == '(': n += 1
			elif c == ')': n -= 1
			current += c
	items.append(current.strip())
	assert len(items ) > 1
	return tuple_expr(parse_expr(i) for i in items)

def parse_stmt(string):
	string = string.strip()
	if string == 'null':
		return null_stmt()
	elif string.startswith('let'):
		return parse_let_stmt(string[3:].strip())
	elif string.startswith('branch '):
		return branch_stmt(parse_expr(string[6:].strip()))
	else:
		assert False

def parse_let_stmt(string):
	lhs, rhs = string.split(':=')
	vars = [v.strip() for v in lhs.strip().split(',')]
	assert all(identifier_pattern.match(v) for v in vars), vars
	expr = parse_expr(rhs)
	return let_stmt(vars, expr)
