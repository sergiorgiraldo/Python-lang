#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('foo.sqlite.db')
print('Opened database successfully')

conn.execute('insert into DEPTO (name) values ("john doe") ' )
conn.commit()
print('Insert executed sucessfully')

cursor = conn.execute("SELECT id, name from DEPTO")
for row in cursor:
   print("ID = ", row[0])
   print("NAME = ", row[1])

print('Operation done successfully')
conn.close()
