import csv
import os

def truncate(table_name):
	table_name = table_name.lower() + '.csv'
	with open(table_name, 'w') as table:
		table.truncate()

def getData(table_name):
	table_name = table_name.lower() + '.csv'
	with open(table_name) as table:
		table = csv.reader(table)
		rows = []
		for r in table:
			rows.append(map(lambda x: int(x), r))
		return rows

def putData(table_name, data):
	table_name = table_name.lower() + '.csv'
	with open(table_name, 'w') as table:
		table = csv.writer(table)
		for row in data:
			table.writerow(row)

def putRow(table_name, row):
	table_name = table_name.lower() + '.csv'
	with open(table_name, 'a') as table:
		writer = csv.writer(table)
		writer.writerow(row)

def remove(table_name):
	table_name = table_name.lower() + '.csv'
	os.remove(table_name)