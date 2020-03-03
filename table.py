### Definition of a Table class. COntains all metadata about the class.
import parse_csv
import parse_metadata

class TableContent:

	def __init__(self):
		self.columns = []
		self.rows = []

	def addColumn(self, column):
		self.columns.append(column)

	def addRow(self, row):
		self.rows.append(row[:])

	def count(self, col):
		toMatch = self.columns
		if len(col.split('.')) == 1:
			toMatch = map(lambda x: x.split('.')[1], toMatch)
		count = 0
		for c in toMatch:
			if c == col:
				count += 1
		return count

	def index(self, col):
		toMatch = self.columns
		if len(col.split('.')) == 1:
			toMatch = map(lambda x: x.split('.')[1], toMatch)
		for i, c in enumerate(toMatch):
			if c == col:
				return i
		return -1

	def show(self):
		print ','.join(self.columns)
		for row in self.rows:
			print ','.join(map(lambda x: str(x), row))

	def cross(self, tc2):
		tmp = []
		for r1 in self.rows:
			for r2 in tc2.rows:
				tmp.append(r1 + r2)
		self.rows = tmp
		self.columns.extend(tc2.columns)

	def clone(self):
		tmp = TableContent()
		tmp.columns = self.columns[:]
		tmp.rows = []
		for row in self.rows:
			tmp.rows.append(row[:])
		return tmp

class Table:

	def __init__(self, name, loadData = True):
		self.name = name
		self.attrs = parse_metadata.getMetadata(name)
		if loadData and self.attrs:
			self.loadContents()

	def loadContents(self):
		self.contents = TableContent()
		self.contents.columns.extend(map(lambda x: self.name + '.' + x, self.attrs))
		for row in parse_csv.getData(self.name):
			self.contents.addRow(row)

	def writeContents(self):
		parse_csv.putData(self.name, self.contents.rows)

	def getContents(self):
		return self.contents.clone()

	def show(self):
		print self.name
		self.contents.show()
