import sys


STATE_0_INIT = 0
STATE_1_SONG_LIST = 1


def process(contents, args, outfile):
  accum = []
  state = STATE_0_INIT
  for line in contents.split('\n'):
    if line.startswith('ft_song_list:'):
      state = STATE_1_SONG_LIST
    accum.append(line)
  write_output(accum, outfile)


def write_output(accum, outfile):
  fout = open(outfile, 'w')
  for line in accum:
    fout.write(line + '\n')
  fout.close()


def run():
  fp = open(sys.argv[1], 'r')
  contents = fp.read()
  fp.close()
  args = sys.argv[2].split(',')
  process(contents, args, sys.argv[3])


if __name__ == '__main__':
  run()
