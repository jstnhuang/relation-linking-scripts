# Formats tuples from the Open IE demo (given as JSON) into serialized ReVerb
# extraction group format.
import collections
import json
import os
import sys

Entity = collections.namedtuple('Entity', [
  'fbid',
  'inlink',
  'name',
  'score'
])

EntityType = collections.namedtuple('EntityType', [
  'domain',
  'typ'
])

Arg = collections.namedtuple('ExtractionArgument', [
  'entity',
  'lemma',
  'types'
])

Extraction = collections.namedtuple('Extraction', [ 'arg1Text',
  'relText',
  'arg2Text',
  'sentenceText'
])

Instance = collections.namedtuple('Instance', [
  'confidence',
  'corpus',
  'extraction'
])

Reg = collections.namedtuple('ReverbExtractionGroup', [
  'arg1',
  'rel',
  'arg2',
  'instances'
])

def jsonToEntity(jsonEntity):
  if jsonEntity is None:
    return None
  return Entity(
    fbid=jsonEntity['fbid'],
    inlink=jsonEntity['inlink'],
    name=jsonEntity['name'],
    score=jsonEntity['score']
  )

def jsonToEntityType(jsonType):
  if jsonType is None:
    return None
  return EntityType(
    domain=jsonType['domain'],
    typ=jsonType['type']
  )

def jsonToArg(jsonArg):
  return Arg(
    entity=jsonToEntity(jsonArg['entity']),
    lemma=jsonArg['lemma'],
    types=[jsonToEntityType(jsonType) for jsonType in jsonArg['types']]
  )

def jsonToExtraction(jsonExtraction):
  return Extraction(
    arg1Text=jsonExtraction['arg1Text'],
    relText=jsonExtraction['relText'],
    arg2Text=jsonExtraction['arg2Text'],
    sentenceText=jsonExtraction['sentenceText'],
  )

def jsonToInstances(jsonInstances):
  return [
    Instance(
      confidence=jsonInstance['confidence'],
      corpus=jsonInstance['corpus'],
      extraction=jsonToExtraction(jsonInstance['extraction'])
    )
    for jsonInstance in jsonInstances
  ]

def jsonToRegs(jsonTuple):
  return Reg(
    arg1=jsonToArg(jsonTuple['arg1']),
    rel=jsonTuple['rel']['lemma'],
    arg2=jsonToArg(jsonTuple['arg2']),
    instances=jsonToInstances(jsonTuple['instances'])
  )

def readGroups(jsonFile):
  for line in jsonFile:
    results = json.loads(line, encoding='UTF-8')
    for result in results:
      yield jsonToRegs(result)

def regToString(group):
  """Prints a string representation of the group. For now, just printing out the
  tuple because that's the only thing I need.
  """
  return '\t'.join([
    group.arg1.lemma,
    group.rel,
    group.arg2.lemma
  ])

def main():
  inputDir = sys.argv[1]
  jsonFiles = [open(inputDir + jsonFile) for jsonFile in os.listdir(inputDir)]
  for jsonFile in jsonFiles:
    groups = readGroups(jsonFile)
    for group in groups:
      print(regToString(group))

if __name__ == '__main__':
  main()
