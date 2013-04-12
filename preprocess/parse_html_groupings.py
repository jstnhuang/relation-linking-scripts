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
  If the line indicates a verb particle construction, it returns a singleton
    mapping from the verb phrase to the set of senses for that phrase.
  """
  match = re.search('Sense Number (\d+)', line)
  if match is not None:
    return match.group(1), 'SENSENUM'

  match = re.search('PropBank: (.+\..+)<br>', line)
  if match is not None:
    return (
      set([x.strip() for x in match.group(1).split(',') if '-' not in x]),
      'PROPBANK'
    )

  match = re.search('WordNet 3\.0 Sense Numbers: (\d.*)</font>', line)
  if match is not None:
    return set([x.strip() for x in match.group(1).split(',')]), 'WORDNET'

  match = re.match(' ?<i>(\w+)</i> (\d.*)<br>', line)
  if match is not None:
    return (
      {
        match.group(1):
        set([x.strip() for x in match.group(2).split(',')])
      },
      'VPC'
    )

  return None, None

def updateFileMapping(fileMapping, word, wnSenses, pbSenses):
  for num in wnSenses:
    subMapping = {(word, num): pbSenses}
    updateMapping(fileMapping, subMapping)

def parseGroupingFile(groupingFile):
  """FSA that gets the WordNet-Propbank mappings for each grouping sense.

  The rules are:
    START -> SENSENUM
    SENSENUM -> Reset mappings. Go to PROPBANK or back to SENSENUM
    PROPBANK -> Go to WORDNET (save mappings) or back to SENSENUM
    WORDNET -> Go to VPC (save mappings) or back to SENSENUM
    VPC -> Go back to SENSENUM

  Returns: a map like {('prompt', '1'): {'prompt.01', 'prompt.02'}}
  """
  path, groupingFileName = os.path.split(groupingFile.name)
  word = groupingFileName[:-7]
  isVpc = word.endswith('-vpc')
  fileMapping = {}
  state = 'START'
  transitions = {
    ('START', 'SENSENUM'),
    ('SENSENUM', 'SENSENUM'),
    ('SENSENUM', 'PROPBANK'),
    ('PROPBANK', 'SENSENUM'),
    ('PROPBANK', 'WORDNET'),
    ('PROPBANK', 'VPC'),
    ('WORDNET', 'SENSENUM'),
    ('WORDNET', 'VPC'),
    ('VPC', 'SENSENUM'),
    ('VPC', 'VPC')
  }
  pbSenses = set()
  wnSenses = set()
  for line in groupingFile:
    match, nextState = parseLine(line)
    if match is not None and (state, nextState) in transitions:
      if nextState == 'SENSENUM':
        pbSenses = set()
        wnSenses = set()
      elif nextState == 'PROPBANK':
        pbSenses = match
      elif nextState == 'WORDNET':
        wnSenses = match
        if not isVpc:
          updateFileMapping(fileMapping, word, wnSenses, pbSenses)
      elif nextState == 'VPC':
        for vp, senseNumbers in match.items():
          updateFileMapping(fileMapping, vp, senseNumbers, pbSenses)
      else:
        raise RuntimeError('Entered illegal state.')
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
  outputFile = open(outputDir + 'wn-pb.tsv', 'w')
  for (word, num), pbSenses in mapping.items():
    for pbSense in pbSenses:
      print('\t'.join([word, num, pbSense]), file=outputFile)

  inverse = invertMapping(mapping)
  inverseFile = open(outputDir + 'pb-wn.tsv', 'w')
  for pbSense, wnSenses in inverse.items():
    for (word, num) in wnSenses:
      print('\t'.join([pbSense, word, num]), file=inverseFile)

def run(inputDir, outputDir):
  mapping = getMapping(inputDir)
  outputMapping(outputDir, mapping)

def main():
  inputDir = sys.argv[1]
  outputDir = sys.argv[2]
  run(inputDir, outputDir)

if __name__ == '__main__':
  main()
