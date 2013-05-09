# Not proud of this, but...
# Creates a huge grep string for the tuples output by format_json_tuples.

import sys

def main():
  tuples = set()
  specialChars = ['^', '$', '\\', '[', ']', '.', '*', '"']
  for line in sys.stdin:
    pattern = line.strip()
    for specialChar in specialChars:
      pattern = pattern.replace(specialChar, '\\' + specialChar)
    tuples.add(pattern)
  print('grep "{}" $1'.format('\\|'.join(tuples)))

if __name__ == '__main__':
  main()
