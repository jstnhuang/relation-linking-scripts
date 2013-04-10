"""Script that exports PropBank tables generated from Java WordSenseMapper to
SQLite, and a format that can be imported into Derby."""

import collections
import sys

PbToStringEntry = collections.namedtuple('PbToStringEntry',
  ['pb', 'wn1', 'word', 'wn2', 'wn2Count']
)

StrToPbEntry = collections.namedtuple('StrToPbEntry',
  ['vp', 'pb', 'probability', 'count']
)

def readTsvFile(path, namedType):
  """Reads a tab-separated file and populates the fields of the given type.
  """
  tsvFile = open(path)
  rows = []
  for line in tsvFile:
    columns = [column.strip() for column in line.split('\t')]
    rows.append(namedType(*columns))
  return rows

def quoteStrings(rows):
  """Quotes string fields.
  """
  for row in rows:
    entry = []
    for col in row:
      if isinstance(col, str):
        entry.append('"{}"'.format(col))
      else:
        entry.append(col)
    yield(entry)

def writeTsvFile(path, rows):
  """Writes a tab-separated file with the fields of the given type.
  """
  tsvFile = open(path, 'w')
  for row in rows:
    print('\t'.join([str(col) for col in row]), file=tsvFile)

def computeStrToPbTable(pbToStrRows):
  """
  Output is a list of tuples, (Verb phrase, PropBank sense, probability, count).

  Probability is determined by WordNet sense. Example:
  pb-to-syn  has two senses for exhibit
    exhibit%2:39:01::   11      display.01
    exhibit%2:39:00::   4       show.03, present.01, demonstrate.02
  We do add-1 smoothing, so exhibit links to display.01 with probability 12/17
  and to show.03, present.01, demonstrate.02 with probability 6/17. We store the
  count as well, so the tuples would be like (exhibit, display.01, 12/17, 12).
  """
  table = collections.Counter()
  wnCounts = {}
  for pbToStrEntry in pbToStrRows:
    count = int(pbToStrEntry.wn2Count) + 1
    table[pbToStrEntry.word, pbToStrEntry.pb] += count
    wnCounts[pbToStrEntry.word, pbToStrEntry.wn2] = count

  wnTotals = collections.Counter()
  for (word, wn), count in wnCounts.items():
    wnTotals[word] += count

  return sorted([
    StrToPbEntry(vp, pb, count/wnTotals[vp], count)
    for (vp, pb), count in table.items()
  ])

def exportToTsv(path, table):
  """Exports the given table to a TSV file for SQLite3 and Derby."""
  writeTsvFile(path, table)
  writeTsvFile(path[:-4] + '-derby' + path[-4:], quoteStrings(table))

def exportTables(inputDir, outputDir):
  """Main export function.
  """
  pbToStrSynRows = readTsvFile(
    inputDir + 'propbank-to-synonyms.tsv',
    PbToStringEntry
  )
  strSynToPbTable = computeStrToPbTable(pbToStrSynRows)
  exportToTsv(outputDir + 'str-to-pb-syn.tsv', strSynToPbTable)

  pbToStrTroRows = readTsvFile(
    inputDir + 'propbank-to-hyponyms.tsv',
    PbToStringEntry
  )
  strTroToPbTable = computeStrToPbTable(pbToStrTroRows)
  exportToTsv(outputDir + 'str-to-pb-tro.tsv', strTroToPbTable)

def main():
  """Gather args and call export function.
  """
  inputDir = sys.argv[1]
  outputDir = sys.argv[2]
  exportTables(inputDir, outputDir)

if __name__ == '__main__':
  main()
