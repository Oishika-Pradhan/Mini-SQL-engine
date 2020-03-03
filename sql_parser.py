from pyparsing import Literal, CaselessLiteral, Word, Upcase, delimitedList, Optional, \
		Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, quotedString, \
		ZeroOrMore, restOfLine, Keyword


def parse(str):
	if str.endswith(";") == False:
		print "Syntax Error!"
		return False
	else:
		try:
			return simpleSQL.parseString(str)
		except ParseException, err:
			print " "*(13 + err.loc) + "^"
			print "Syntax Error!"
			return False


# define SQL tokens
selectToken = Keyword("select", caseless=True)
fromToken   = Keyword("from", caseless=True)
createTableToken = Keyword("create table", caseless=True)
integerToken = Keyword("integer", caseless=True) | Keyword("int", caseless=True)
insertIntoToken = Keyword("insert into", caseless=True)
valuesToken = Keyword("values", caseless=True)
deleteFromToken = Keyword("delete from", caseless=True)
truncateToken = Keyword("truncate table", caseless=True)
dropToken = Keyword("drop table", caseless=True)
showTablesToken = Keyword("show tables", caseless=True)


ident          = Word( alphas, alphanums + "_$" ).setName("identifier")
columnName     = Upcase( delimitedList( ident, ".", combine=True ) )
functionCall   = Group( ident + '(' + columnName + ')')
columnNameList = Group( delimitedList( functionCall | columnName) )
tableName      = Upcase( delimitedList( ident, ".", combine=True ) )
tableNameList  = Group( delimitedList( tableName ) )
field          = Group( ident + integerToken )
fieldList      = Group( delimitedList(field) )

and_ = Keyword("and", caseless=True)
or_ = Keyword("or", caseless=True)

binop = oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
arithSign = Word("+-",exact=1)
intNum = Combine( Optional(arithSign) + Word( nums ) )
intNumList = Group( delimitedList(intNum) )

columnRval = intNum | columnName
whereCondition = Group(columnRval + binop + columnRval)
whereExpression = Group(whereCondition + Optional( (and_ | or_) + whereCondition))

# define the grammar
selectStmt      =  ( selectToken.setResultsName( "statementtype" ) +
									 ( '*' | columnNameList ).setResultsName( "columns" ) +
									 fromToken +
									 tableNameList.setResultsName( "tables" ) +
									 Optional( Group( CaselessLiteral("where") + whereExpression ), "" ).setResultsName("where") )

createStmt      =  ( createTableToken.setResultsName( "statementtype" ) +
									 ident.setResultsName("tablename") +
									 '(' +
									 fieldList.setResultsName("fieldlist") +
									 ')')

insertStmt      =  ( insertIntoToken.setResultsName( "statementtype" ) +
									 ident.setResultsName("tablename") +
									 valuesToken +
									 '(' +
									 intNumList.setResultsName("tablevalues") +
									 ')' )

deleteStmt      =  ( deleteFromToken.setResultsName("statementtype") +
									 ident.setResultsName("tablename") +
									 CaselessLiteral("where") +
									 whereExpression.setResultsName("where") )

truncateStmt    =  ( truncateToken.setResultsName("statementtype") +
									 ident.setResultsName("tablename") )

dropStmt        =  ( dropToken.setResultsName("statementtype") +
									 ident.setResultsName("tablename") )

showStmt        =  ( showTablesToken.setResultsName("statementtype") )

simpleSQL = selectStmt | createStmt | insertStmt | deleteStmt | truncateStmt | dropStmt | showStmt


# TESTS

def test( str ):
		print str,"->"
		try:
				tokens = simpleSQL.parseString( str )
				print tokens.statementtype
				if tokens.statementtype == "select":
					print "tokens.columns =", tokens.columns
					print "tokens.tables =",  tokens.tables
					print "tokens.where =", tokens.where
				elif tokens.statementtype == 'create table':
					print "tokens.tablename =", tokens.tablename
					print "tokens.fieldlist =", tokens.fieldlist
				elif tokens.statementtype == 'insert into':
					print "tokens.tablename =", tokens.tablename
					print "tokens.tablevalues =", tokens.tablevalues
				elif tokens.statementtype == "delete from":
					print "tokens.tablename =", tokens.tablename
					print "tokens.where =", tokens.where
				elif tokens.statementtype == "truncate table":
					print "tokens.tablename =", tokens.tablename
				elif tokens.statementtype == "drop table":
					print "tokens.tablename =", tokens.tablename
				return tokens
		except ParseException, err:
				print " "*err.loc + "^\n" + err.msg
				print err
		print

def manualtests():
	print
	test('Select min(r1), r2 from t1 where c1 = d1 and c2 = d2')
	print
	test('create taBle table3(c1 integer, c2 integer)')
	print
	test('insert into emp values(1, 2, 3, 4)')
	print
	test('delete from emp where id = 10')
	print
	test('truncate table emp')
	print
	test('drop table emp')
	print

if __name__ == '__main__':
	manualtests()
	while True:
		x = test(raw_input())
