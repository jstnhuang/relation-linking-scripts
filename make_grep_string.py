# Not proud of this, but...
# Creates a huge grep string for the tuples output by format_json_tuples.

import sys

def main():
  tuples = set()
  for line in sys.stdin:
    tuples.add(line.strip())
  print('grep \'{}\' $1'.format('\\|'.join(tuples)))

if __name__ == '__main__':
  main()
