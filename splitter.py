import re
import sys


INFINITY = 999999


STATE_0_INIT = 0
STATE_1_SONG_LIST = 1
STATE_2_SONG_DATA = 2


def process(contents, args, outtmpl):
  args = [0] + args + [INFINITY]
  for i in xrange(len(args) - 1):
    single_pass(contents, args[i], args[i + 1], outtmpl.replace('%d', '%d' % i))


def single_pass(contents, start, finish, outfile):
  if finish is None:
    finish = INFINITY
  accum = []
  state = STATE_0_INIT
  for line in contents.split('\n'):
    if line.startswith('ft_song_list:'):
      state = STATE_1_SONG_LIST
    elif state == STATE_1_SONG_LIST:
      if not line:
        state = STATE_2_SONG_DATA
      else:
        m = re.match(r'^\t.word ft_song_(\d+)$', line)
        if not m:
          raise RuntimeError('Did not match "%s"' % line)
        num = int(m.group(1))
        if num < start or num >= finish:
          line = '\t.word 0'
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
  args = [int(n) for n in sys.argv[2].split(',')]
  outtmpl = sys.argv[3]
  if not '%d' in outtmpl:
    raise RuntimeError('Error, must have "%d" in output template')
  process(contents, args, outtmpl)


if __name__ == '__main__':
  run()
