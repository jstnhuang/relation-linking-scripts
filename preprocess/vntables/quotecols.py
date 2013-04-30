import sys

def main():
  for line in sys.stdin:
    cols = [col.strip() for col in line.split('\t')]
    print('"{}"\t"{}"'.format(cols[0], cols[1]))

if __name__ == '__main__':
  main()
