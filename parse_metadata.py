### Metadata manipulation functions

def getTables():
	tables = {}
	with open('metadata.txt') as metadata:
		startNew = False
		name = None
		attrs = []
		for line in metadata.readlines():
			line = line.strip()
			if line == '<begin_table>':
				startNew = True
				name = None
				attrs = []
			elif line == '<end_table>':
				tables[name] = attrs[:]
			elif startNew:
				startNew = False
				name = line.upper()
			else:
				attrs.append(line.upper())
		#if name != None:
		#	raise Exception("Can't parse Metadata! Make sure it is valid.")
	return tables

def putTables(tables):
	with open('metadata.txt', 'w') as metadata:
		for table in tables:
			metadata.write('<begin_table>\n')
			metadata.write(table + '\n')
			for attr in tables[table]:
				metadata.write(attr + '\n')
			metadata.write('<end_table>\n')

def getMetadata(table):
	table = table.lower()
	with open('metadata.txt') as metadata:
		startNew = False
		desc = []
		name = None
		for line in metadata.readlines():
			line = line.strip()
			if line == '<begin_table>':
				startNew = True
				name = None
				desc = []
			elif line == '<end_table>':
				if name.lower() == table:
					return desc
			elif startNew:
				startNew = False
				name = line.upper()
			else:
				desc.append(line.upper())
	return False

def putMetadata(table, desc):
	if getMetadata(table):
		return False
	with open('metadata.txt', 'a') as metadata:
		metadata.write('\n<begin_table>\n')
		metadata.write(table.upper() + '\n')
		for attr in desc:
			metadata.write(attr.upper() + '\n')
		metadata.write('<end_table>')

if __name__ == '__main__':
	try:
		tables = getTables()
		for table_name in tables:
			print table_name + ": " + ', '.join(tables[table_name])
	except Exception as e:
		print e
