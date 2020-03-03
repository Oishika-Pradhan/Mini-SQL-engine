import parse_metadata
import parse_csv
import table
import sql_parser
import os
import operator as op
from pyparsing import ParseResults as ppr

def satisfy(row, cond):
	[lcol, oper, rcol] = cond
	lcol = row[lcol] if type(lcol) != str else int(lcol)
	rcol = row[rcol] if type(rcol) != str else int(rcol)
	return oper(lcol, rcol)

def formatCond(contents, cond):
	ops = {'<': op.lt, 'lt': op.lt, '<=': op.le, 'le': op.le, '=': op.eq, 'eq': op.eq, '!=': op.ne, 'ne': op.ne, '>': op.gt, 'gt': op.gt, '>=': op.ge, 'ge': op.ge}
	prefix = ''
	if cond[0][0] == '+':
		cond[0] = cond[0][1:]
	elif cond[0][0] == '-':
		cond[0] = cond[0][1:]
		prefix = '-'
	if not cond[0].isdigit():
		if contents.count(cond[0]) == 1:
			cond[0] = contents.index(cond[0])
		else:
			return False
	else:
		cond[0] = prefix+cond[0]

	prefix = ''
	if cond[2][0] == '+':
		cond[2] = cond[2][1:]
	elif cond[2][0] == '-':
		cond[2] = cond[2][1:]
		prefix = '-'
	if not cond[2].isdigit():
		if contents.count(cond[2]) == 1:
			cond[2] = contents.index(cond[2])
		else:
			return False
	else:
		cond[2] = prefix+cond[2]

	cond[1] = ops[cond[1]]
	return True

def handleSelect(stmt):
	contents = None
	result = True

	for t in stmt.tables:
		tableExists = parse_metadata.getMetadata(t)
		if not tableExists:
			print "Error: Table '"+t+"' doesn't exist!"
			return False
		tableData = table.Table(t)
		if contents is None:
			contents = tableData.getContents()
		else:
			contents.cross(tableData.getContents())

	def handleWhere(contents, cond1, more=False, cond2=None):
		newRows = []
		if not formatCond(contents, cond1):
			print "Error: Ambiguous/Unidentified column name(s) in first condition"
			return False
		if more:
			more = {'and': op.and_, 'or': op.or_}[more]
			if not formatCond(contents, cond2):
				print "Error: Ambiguous/Unidentified column name(s) in second condition"
				return False
			contents.rows = filter(lambda r: more(satisfy(r, cond1), satisfy(r, cond2)), contents.rows)
		else:
			contents.rows = filter(lambda r: satisfy(r, cond1), contents.rows)
		return True

	stmt.where = stmt.where[0]
	if stmt.where != '':
		result = False
		stmt.where = stmt.where[1]
		if len(stmt.where) is 1:
			result = handleWhere(contents, stmt.where[0])
		else:
			result = handleWhere(contents, stmt.where[0], stmt.where[1], stmt.where[2])

	def handleSelCols(contents, cols):

		if cols is '*':
			return contents

		def functionCall(contents, func, col):
			func = func.lower()
			div = 1
			if func == 'avg':
				div = float(len(contents))
				func = 'sum'
			if func in ['min', 'max', 'sum']:
				f = {'min': min, 'max': max, 'sum': op.add}[func]
				tot = None
				for c in contents:
					if tot is None:
						tot = c[col]
					else:
						tot = f(tot, c[col])
				tot /= div
				return tot
			else:
				print 'Error: Unidentified function call!'
			return False

		def distinctCall(contents, col):
			x = {}
			for row in contents:
				x[row[col]] = 0
			return list(x)

		distinct = 0
		aggregate = 0
		for col in cols:
			if type(col) is ppr:
				if col[0] == 'distinct':
					distinct += 1
				else:
					aggregate += 1
		others = len(cols) - distinct - aggregate

		if distinct == 0 and aggregate == 0:
			filteredRows = table.TableContent()
			for i, col in enumerate(cols):
				if contents.count(col) != 1:
					print 'Error: Ambiguous/Unidentified column name(s) in select!'
					return False
				else:
					filteredRows.addColumn(col)
					cols[i] = contents.index(col)
			for r in contents.rows:
				tmp = [r[i] for i in cols]
				filteredRows.addRow(tmp)
			return filteredRows
		elif distinct == 0 and others == 0:
			filteredRows = table.TableContent()
			answers = []
			for col in cols:
				if contents.count(col[2]) != 1:
					print 'Error: Ambiguous/Unidentified column name(s) in select!'
					return False
				else:
					filteredRows.addColumn(''.join(col))
					result = functionCall(contents.rows, col[0], contents.index(col[2]))
					if not result:
						return False
					answers.append(result)
			filteredRows.addRow(answers)
			return filteredRows
		elif distinct == 1 and others == 0 and aggregate == 0:
			filteredRows = table.TableContent()
			col = cols[0]
			if contents.count(col[2]) != 1:
				print 'Error: Ambiguous/Unidentified column name(s) in select!'
				return False
			else:
				filteredRows.addColumn(''.join(col))
				for i in distinctCall(contents.rows, contents.index(col[2])):
					filteredRows.addRow([i])
			return filteredRows
		else:
			print 'Error: Unknown column selection!'
			return False

	contents = handleSelCols(contents, stmt.columns)
	if not contents:
		result = False

	if result:
		contents.show()
		return True
	return False

def handleCreate(stmt):
	table = stmt.tablename
	tableExists = parse_metadata.getMetadata(table)
	if tableExists:
		print "Error: Table '"+table+"' already exists!"
		return False
	parse_csv.truncate(table)
	attrs = map(lambda x: x[0], stmt.fieldlist)
	parse_metadata.putMetadata(table, attrs)
	return True

def handleInsert(stmt):
	table = stmt.tablename
	tableExists = parse_metadata.getMetadata(table)
	if not tableExists:
		print "Error: Table '"+table+"' doesn't exist!"
		return False
	if len(stmt.tablevalues) != len(tableExists):
		print "Error: Must have exactly",len(tableExists),"values!"
		return False
	parse_csv.putRow(table, stmt.tablevalues)
	return True

def handleDelete(stmt):
	t = stmt.tablename
	tableExists = parse_metadata.getMetadata(t)
	if not tableExists:
		print "Error: Table '"+t+"' doesn't exist!"
		return False
	tableData = table.Table(t)
	contents = tableData.getContents()
	stmt.where = stmt.where[0]
	print stmt.where
	if not formatCond(contents, stmt.where):
		print "Error: Ambiguous/Unidentified column name(s)"
		return False
	tableData.contents.rows = []
	newContents = tableData.contents
	print contents.rows
	for r in contents.rows:
		if not satisfy(r, stmt.where):
			newContents.addRow(r)
	tableData.writeContents()
	return True


def handleTruncate(stmt):
	table = stmt.tablename
	tableExists = parse_metadata.getMetadata(table)
	if not tableExists:
		print "Error: Table '"+table+"' doesn't exist!"
		return False
	parse_csv.truncate(table)
	return True

def handleDrop(stmt):
	# Drops table even if it has data
	table = stmt.tablename.upper()
	tableExists = parse_metadata.getMetadata(table)
	if not tableExists:
		print "Error: Table '"+table+"' doesn't exist!"
		return False
	parse_csv.remove(table)
	tables = parse_metadata.getTables()
	with open('metadata.txt', 'w') as metadata:
		metadata.truncate()
	for tab in tables:
		if tab != table:
			parse_metadata.putMetadata(tab, tables[tab])
	return True

def handleShow(stmt):
	tables = parse_metadata.getTables()
	if not tables:
		return False
	for table in tables:
		print table
	return True

def main():
	def handleStr(line):
		statement = sql_parser.parse(line)
		if not statement:
			return
		statement_type = statement.statementtype
		function = None
		if statement_type == 'select':
			function = handleSelect
		elif statement_type == 'create table':
			function = handleCreate
		elif statement_type == 'insert into':
			function = handleInsert
		elif statement_type == 'delete from':
			function = handleDelete
		elif statement_type == 'truncate table':
			function = handleTruncate
		elif statement_type == 'drop table':
			function = handleDrop
		elif statement_type == 'show tables':
			function = handleShow
		else:
			print "Error: Unrecognized statement!"
			return False
		result = function(statement)
		return result

	while True:
		print "SQLEngine >>",
		try:
			inp = raw_input()
		except:
			print "\nBye"
			return
		try:
			handleStr(inp)
		except e:
			print "Error: The system got confused :/"

if __name__ == '__main__':
	main()
