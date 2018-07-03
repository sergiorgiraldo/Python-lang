import csv
print("BEGIN")
with open('C:\\Users\\sgiraldo\\Downloads\\ArqAndrea20180618.txt') as crmFile:
    csvReader = csv.reader(crmFile, delimiter=';')
    for row in csvReader:       
        if csvReader.line_num == 1: 
            fields = len(row)
            print("Number of fields expected: %s" % (fields))
        if len(row) != fields:
            print("Number of fields should be %s: line %s" % (fields,str(row)))
    print("Number of lines: %s" % csvReader.line_num)
    print("END")            