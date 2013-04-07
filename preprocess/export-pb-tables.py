"""Script that exports PropBank tables generated from Java WordSenseMapper to
SQLite, and a format that can be imported into Derby."""

import sys

def readPropbankToPropbankTable(path):
  table = {}
  tableFile = open(path)
  for line in tableFile:
    columns = [column.strip() for column in line.split('\t')]
    sense = columns[0]
    synonym = columns[1]
    if sense in table:
      table[sense].add(synonym)
    else:
      table[sense] = set([synonym])
  tableList = []
  for sense, synonyms in table.items():
    for synonym in synonyms:
      tableList.append((sense, synonym, 0))
  return tableList

def readPropbankToStringTable(path):
  table = {}
  tableFile = open(path)
  for line in tableFile:
    columns = [column.strip() for column in line.split('\t')]
    propbankSense = columns[0]
    count = int(columns[2])
    verbPhrase = columns[3].replace('_', ' ')
    key = (verbPhrase, propbankSense)
    if key in table:
      table[key] += count
    else:
      table[key] = count
  tableList = []
  for (verbPhrase, propbankSense), count in table.items():
    tableList.append((verbPhrase, propbankSense, count))
  return tableList

def exportToTsv(table, outputPath, derby=False):
  outputFile = open(outputPath, 'w')
  for key, pbSense, count in table:
    if (derby):
      key = '"{}"'.format(key)
      pbSense = '"{}"'.format(pbSense)
    count = str(count)
    print('\t'.join([key, pbSense, count]), file=outputFile)

def exportTables(inputDir, outputDir):
  """Main export function.
  """
  stringToPropbankSynonyms = readPropbankToStringTable(
    inputDir + 'propbank-to-synonyms.tsv'
  )
  stringToPropbankTroponyms = readPropbankToStringTable(
    inputDir + 'propbank-to-troponyms.tsv'
  )
  propbankToPropbankSynonyms = readPropbankToPropbankTable(
    inputDir + 'propbank-to-propbank-synonyms-cut.tsv'
  )
  propbankToPropbankTroponyms = readPropbankToPropbankTable(
    inputDir + 'propbank-to-propbank-troponyms-cut.tsv'
  )
  exportToTsv(stringToPropbankSynonyms, outputDir + 'str-to-pb-syn.tsv')
  exportToTsv(stringToPropbankTroponyms, outputDir + 'str-to-pb-tro.tsv')
  exportToTsv(propbankToPropbankSynonyms, outputDir + 'pb-to-pb-syn.tsv')
  exportToTsv(propbankToPropbankTroponyms, outputDir + 'pb-to-pb-tro.tsv')
  exportToTsv(
    stringToPropbankSynonyms,
    outputDir + 'str-to-pb-syn-derby.tsv',
    derby=True
  )
  exportToTsv(
    stringToPropbankTroponyms,
    outputDir + 'str-to-pb-tro-derby.tsv',
    derby=True
  )
  exportToTsv(
    propbankToPropbankSynonyms,
    outputDir + 'pb-to-pb-syn-derby.tsv',
    derby=True
  )
  exportToTsv(
    propbankToPropbankTroponyms,
    outputDir + 'pb-to-pb-tro-derby.tsv',
    derby=True
  )

def main():
  """Gather args and call export function.
  """
  inputDir = sys.argv[1]
  outputDir = sys.argv[2]
  exportTables(inputDir, outputDir)

if __name__ == '__main__':
  main()
