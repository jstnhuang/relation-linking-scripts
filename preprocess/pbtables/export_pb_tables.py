"""Script that exports PropBank tables generated from Java WordSenseMapper to
SQLite, and a format that can be imported into Derby."""

import collections
import sys

PbToStringEntry = collections.namedtuple('PbToStringEntry',
  ['pb', 'wn1', 'wn1Count', 'word', 'wn2', 'wn2Count']
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

def computeWnTotals(pbToStrSynRows, pbToStrTroRows, pbToStrHypRows):
  """Totals the tag counts of all of a word's senses.

  Example:
  pb-to-syn has four senses of "exhibit":
    exhibit%2:38:00:: 0   exhibit.01, march.01
    exhibit%2:39:00:: 4   demonstrate.01, exhibit.01, present.01, show.01
    exhibit%2:39:01:: 11  display.01, exhibit.01, expose.01
    exhibit%2:42:00:: 13  exhibit.01
  pb-to-tro has three senses, all seen before, which we don't double-count.
    exhibit%2:39:00:: 4   show.01, show.02
    exhibit%2:39:01:: 11  show.01, show.02
    exhibit%2:42:00:: 13  possess.01
  With add-1 smoothing, the total is 1 + 5 + 12 + 14 = 32.
  """
  pbToStrRows = []
  pbToStrRows.extend(pbToStrSynRows)
  pbToStrRows.extend(pbToStrTroRows)
  pbToStrRows.extend(pbToStrHypRows)

  wnCounts = {}
  for pbToStrEntry in pbToStrRows:
    count = int(pbToStrEntry.wn2Count) + 1
    wnCounts[pbToStrEntry.word, pbToStrEntry.wn2] = count

  wnTotals = collections.Counter()
  for (word, wn), count in wnCounts.items():
    wnTotals[word] += count

  return wnTotals

def computeStrToPbTable(pbToStrRows, wnTotals):
  """Output the tuples: (Verb phrase, PropBank sense, probability, count).

  Probability is determined by WordNet sense. In the exhibit example, exhibit.01
  goes to every sense, so its total count is 32, making its probability 32/32 = 
  1. display.01 only goes to one sense, with count 12, so its probability is
  12/32 = 0.375. show.01 only goes to exhibit%2:39:00:: in pb-to-syn, so its
  probability is 5/32 = 0.15625. However, show.01 goes to both exhibit%2:39:00::
  and exhibit:%2:39:01 in pb-to-tro, so its probability in the str-to-pb-tro
  table is (5 + 12)/32 = 0.53125.
  """
  table = collections.Counter()
  pbToWnSenses = {}
  for entry in pbToStrRows:
    count = int(entry.wn2Count) + 1
    pb = entry.pb
    wn2 = entry.wn2
    if pb not in pbToWnSenses or wn2 not in pbToWnSenses[pb]:
      table[entry.word, pb] += count
      if pb not in pbToWnSenses:
        pbToWnSenses[pb] = {wn2}
      else:
        pbToWnSenses[pb].add(wn2)

  return sorted([
    StrToPbEntry(vp, pb, count/wnTotals[vp], count)
    for (vp, pb), count in table.items()
  ])

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
  pbToStrTroRows = readTsvFile(
    inputDir + 'propbank-to-hyponyms.tsv',
    PbToStringEntry
  )
  pbToStrHypRows = readTsvFile(
    inputDir + 'propbank-to-hypernyms.tsv',
    PbToStringEntry
  )
  wnTotals = computeWnTotals(pbToStrSynRows, pbToStrTroRows, pbToStrHypRows)

  strSynToPbTable = computeStrToPbTable(pbToStrSynRows, wnTotals)
  strTroToPbTable = computeStrToPbTable(pbToStrTroRows, wnTotals)
  strHypToPbTable = computeStrToPbTable(pbToStrHypRows, wnTotals)

  exportToTsv(outputDir + 'str-to-pb-syn.tsv', strSynToPbTable)
  exportToTsv(outputDir + 'str-to-pb-tro.tsv', strTroToPbTable)
  exportToTsv(outputDir + 'str-to-pb-hyp.tsv', strHypToPbTable)

def main():
  """Gather args and call export function.
  """
  inputDir = sys.argv[1]
  outputDir = sys.argv[2]
  exportTables(inputDir, outputDir)

if __name__ == '__main__':
  main()
