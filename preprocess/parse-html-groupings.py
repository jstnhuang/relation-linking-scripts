"""Extracts WordNet to PropBank mappings from Colorado HTML groupings.
See http://verbs.colorado.edu/html_groupings/ for the data.

To execute: python3 parse-html-groupings.py /path/to/input /path/to/output
"""

import collections
import os
import re
import sys

WordSenseMapping = collections.namedtuple(
  'WordSenseMapping',
  ['word', 'wnSenseNum', 'propbankSense']
)

def parseLine(line):
  """Parses an HTML grouping file line and returns relevant information.

  If the line indicates a new sense number, it returns a new sense number.
  If the line indicates a Propbank mapping, it returns the Propbank senses.
  If the line indicates a WordNet mapping, it returns the WordNet sense numbers.
  """
  match = re.search('Sense Number (\d+)', line)
  if match is not None:
    return match.group(1), 'SENSENUM'
  match = re.search('PropBank: (.+\..+)<br>', line)
  if match is not None:
    return set([x.strip() for x in match.group(1).split(',')]), 'PROPBANK'
  match = re.search('WordNet 3\.0 Sense Numbers: (\d.*)</font>', line)
  if match is not None:
    return set([x.strip() for x in match.group(1).split(',')]), 'WORDNET'
  return None, None

def updateFileMapping(fileMapping, word, wnSenses, pbSenses):
  for num in wnSenses:
    subMapping = {(word, num): pbSenses}
    updateMapping(fileMapping, subMapping)

def parseGroupingFile(groupingFile):
  """FSA that gets the WordNet-Propbank mappings for each grouping sense.

  The rules are:
    START -> SENSENUM
    SENSENUM -> reset mappings, go to PROPBANK or WORDNET or SENSENUM
    PROPBANK -> WORDNET (save mapping) or SENSENUM
    WORDNET -> PROPBANK (save mapping) or SENSENUM

  Returns: a map like {('prompt', '1'): {'prompt.01', 'prompt.02'}}
  """
  path, groupingFileName = os.path.split(groupingFile.name)
  word = groupingFileName[:-7]
  fileMapping = {}
  state = 'START'
  pbSenses = set()
  wnSenses = set()
  for line in groupingFile:
    match, nextState = parseLine(line)
    if match is not None:
      if state == 'START':
        if nextState != 'SENSENUM':
          raise RuntimeError('Sense number not the first thing found.')
      elif state == 'SENSENUM':
        pbSenses = set()
        wnSenses = set()
        if nextState == 'PROPBANK':
          pbSenses = match
        elif nextState == 'WORDNET':
          wnSenses = match
        elif nextState == 'SENSENUM':
          pass
        else:
          raise RuntimeError('Went back to start state.')
      elif state == 'PROPBANK':
        if nextState == 'WORDNET':
          wnSenses = match
          updateFileMapping(fileMapping, word, wnSenses, pbSenses)
        elif nextState == 'SENSENUM':
          pass
        else:
          raise RuntimeError('Illegal state.')
      elif state == 'WORDNET':
        if nextState == 'PROPBANK':
          pbSenses = match
          updateFileMapping(fileMapping, word, wnSenses, pbSenses)
        elif nextState == 'SENSENUM':
          pass
        else:
          raise RuntimeError('Illegal state.')
      else:
        raise RuntimeError('Entered unknown state.')
      state = nextState
  return fileMapping

def updateMapping(mapping, subMapping):
  for (word, num), pbSenses in subMapping.items():
    if (word, num) in mapping:
      mapping[word, num].update(pbSenses)
    else:
      mapping[word, num] = pbSenses

def getMapping(inputDir):
  mapping = {} # Maps (word, WN sense number) tuples to sets of PropBank senses.
  groupingFilenames = os.listdir(path=inputDir)
  for filename in groupingFilenames:
    groupingFile = open(inputDir + filename)
    fileMapping = parseGroupingFile(groupingFile)
    updateMapping(mapping, fileMapping)
  for (word, num), pbSenses in mapping.items():
    for pbSense in pbSenses:
      yield WordSenseMapping(word, num, pbSense)

def outputMapping(outputDir, mapping):
  outputFile = open(outputDir + 'wn-pb.tsv', 'w')
  for entry in mapping:
    print('\t'.join(entry), file=outputFile)

def run(inputDir, outputDir):
  mapping = getMapping(inputDir)
  outputMapping(outputDir, mapping)

def main():
  inputDir = sys.argv[1]
  outputDir = sys.argv[2]
  run(inputDir, outputDir)

if __name__ == '__main__':
  main()
