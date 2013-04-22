"""Extracts WordNet to VerbNet mappings from Colorado HTML groupings.
See http://verbs.colorado.edu/html_groupings/ for the data.

To execute: python3 parse-html-groupings.py /path/to/input/ /path/to/output/
"""

import collections
import os
import re
import sys

WordNetSense = collections.namedtuple(
  'WordNetSense',
  ['word', 'senseNum']
)
VerbNetSense = collections.namedtuple(
  'VerbNetSense',
  ['verb', 'senseNum', 'gloss']
)

def parseLine(line):
  """Parses an HTML grouping file line and returns relevant information.

  If the line indicates a new sense number, it returns a new sense number.
  If the line indicates a Propbank mapping, it returns the Propbank senses.
  If the line indicates a WordNet mapping, it returns the WordNet sense numbers.
  If the line indicates a verb particle construction, it returns a singleton
    mapping from the verb phrase to the set of senses for that phrase.
  """
  match = re.search('Sense Number (\d+): (.*)</h3>', line)
  if match is not None:
    return (match.group(1).strip(), match.group(2).strip()), 'SENSENUM'

  match = re.search('WordNet 3\.0 Sense Numbers: (\d.*)</font>', line)
  if match is not None:
    return set([x.strip() for x in match.group(1).split(',')]), 'WORDNET'

  match = re.match(' ?<i>(\w+)</i> (\d.*)<br>', line)
  if match is not None:
    return (
      (
        match.group(1),
        set([x.strip() for x in match.group(2).split(',')])
      ),
      'VPC'
    )

  return None, None

def updateFileMapping(fileMapping, wnSense, vnSense):
  if wnSense in fileMapping:
    fileMapping[wnSense].add(vnSense)
  else:
    fileMapping[wnSense] = set([vnSense])

def parseGroupingFile(groupingFile):
  """FSA that gets the WordNet-VerbNet mappings for each grouping sense.

  The rules are:
    START -> SENSENUM
    SENSENUM -> Reset mappings. Go to WORDNET or back to SENSENUM
    WORDNET -> Go to VPC or back to SENSENUM
    VPC -> Go back to SENSENUM

  Returns: a map from WordNet senses to a set of VerbNet senses.
  """
  fileMapping = {}
  path, groupingFileName = os.path.split(groupingFile.name)
  fileWord = groupingFileName[:-7]
  state = 'START'
  transitions = {
    ('START', 'SENSENUM'),
    ('SENSENUM', 'SENSENUM'),
    ('SENSENUM', 'WORDNET'),
    ('SENSENUM', 'VPC'),
    ('WORDNET', 'SENSENUM'),
    ('WORDNET', 'VPC'),
    ('VPC', 'SENSENUM'),
    ('VPC', 'VPC')
  }
  vnSense = None
  wnSenses = set()
  for line in groupingFile:
    match, nextState = parseLine(line)
    if match is not None and (state, nextState) in transitions:
      if nextState == 'SENSENUM':
        senseNum, gloss = match
        vnSense = VerbNetSense(fileWord, senseNum, gloss)
        wnSenses = set()
      elif nextState == 'WORDNET':
        wnSenseNums = match
        word = fileWord[:-4] if fileWord.endswith('-vpc') else fileWord
        for senseNum in wnSenseNums:
          wnSense = WordNetSense(word, senseNum)
          updateFileMapping(fileMapping, wnSense, vnSense)
      elif nextState == 'VPC':
        vpcWord, vpcSenseNums = match
        for senseNum in vpcSenseNums:
          vpcSense = WordNetSense(vpcWord, senseNum)
          updateFileMapping(fileMapping, vpcSense, vnSense)
      else:
        raise RuntimeError('Entered illegal state.')
      state = nextState

  return fileMapping

def updateMapping(mapping, subMapping):
  for wnSense, vnSenses in subMapping.items():
    if wnSense in mapping:
      mapping[wnSense].update(vnSenses)
    else:
      mapping[wnSense] = vnSenses

def getMapping(inputDir):
  mapping = {} # Maps WordNet senses to sets of VerbNet senses.
  groupingFilenames = os.listdir(path=inputDir)
  for filename in groupingFilenames:
    groupingFile = open(inputDir + filename)
    fileMapping = parseGroupingFile(groupingFile)
    updateMapping(mapping, fileMapping)
  return mapping

def invertMapping(mapping):
  """Given a map from keys to sets of values, build the inverse map.
  """
  inverse = {}
  for key, values in mapping.items():
    for value in values:
      if value in inverse:
        inverse[value].update(set([key]))
      else:
        inverse[value] = set([key])
  return inverse

def outputMapping(outputDir, mapping):
  outputFile = open(outputDir + 'wn-vn.tsv', 'w')
  for wnSense, vnSenses in mapping.items():
    for vnSense in vnSenses:
      print('\t'.join([
        wnSense.word,
        wnSense.senseNum,
        vnSense.verb,
        vnSense.senseNum,
        vnSense.gloss
      ]), file=outputFile)

  inverse = invertMapping(mapping)
  inverseFile = open(outputDir + 'vn-wn.tsv', 'w')
  for vnSense, wnSenses in inverse.items():
    for wnSense in wnSenses:
      print('\t'.join([
        vnSense.verb,
        vnSense.senseNum,
        vnSense.gloss,
        wnSense.word,
        wnSense.senseNum
      ]), file=inverseFile)

def run(inputDir, outputDir):
  mapping = getMapping(inputDir)
  outputMapping(outputDir, mapping)

def main():
  inputDir = sys.argv[1]
  outputDir = sys.argv[2]
  run(inputDir, outputDir)

if __name__ == '__main__':
  main()
