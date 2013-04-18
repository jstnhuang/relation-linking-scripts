"""Extracts the gloss for each PropBank sense.
"""
import os
import sys
import xml.dom.minidom as minidom

def parseFileGlosses(pbFile):
  fileGlosses = {}
  dom = minidom.parse(pbFile)
  for roleset in dom.getElementsByTagName('roleset'):
    pbSense = roleset.getAttribute('id')
    gloss = roleset.getAttribute('name')
    fileGlosses[pbSense] = gloss
  return fileGlosses

def extractGlosses(inputDir):
  glosses = {}
  pbFileNames = os.listdir(path=inputDir)
  for filename in pbFileNames:
    pbFile = open(inputDir + filename)
    fileGlosses = parseFileGlosses(pbFile)
    glosses.update(fileGlosses)
  return glosses

def outputGlosses(glosses, outputFile):
  for pbSense, gloss in glosses.items():
    print('\t'.join([pbSense, gloss]), file=outputFile)

def run(inputDir, outputDir):
  glosses = extractGlosses(inputDir)
  outputFile = open(outputDir + 'glosses.tsv', 'w')
  outputGlosses(glosses, outputFile)

def main():
  inputDir = sys.argv[1]
  outputDir = sys.argv[2]
  run(inputDir, outputDir)

if __name__ == '__main__':
  main()
