import sys

LAST_GROUP_COL = 7

for line in sys.stdin:
  columns = [column.strip() for column in line.split('\t')]
  newColumns = columns[:LAST_GROUP_COL]
  newColumns.append('X')
  newColumns.extend(columns[LAST_GROUP_COL:])
  print('\t'.join(newColumns))
