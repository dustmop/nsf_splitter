import collections
import re
import sys


INFINITY = 999999


STATE_0_INIT = 0
STATE_1_SONG_LIST = 1
STATE_2_SONG_HEADERS = 2
STATE_3_FRAMES = 3
STATE_4_DPCM = 4


def process(contents, args, outtmpl):
  args = [0] + args + [INFINITY]
  for i in xrange(len(args) - 1):
    single_pass(contents, args[i], args[i + 1], outtmpl.replace('%d', '%d' % i))


def single_pass(contents, start, finish, outfile):
  count = 0
  ignoring = False
  curr_song = None
  curr_label = None
  # Store rows of byte data for song columns.
  symbols = collections.defaultdict(list)
  # Track what data the song range is dependent upon.
  dependencies = set()
  # Track what data is generated for the song range. Anything missing that is
  # in the `dependencies` will be included using `symbols`.
  generated = set()
  if finish is None:
    finish = INFINITY
  accum = []
  state = STATE_0_INIT
  for line in contents.split('\n'):
    if state == STATE_0_INIT:
      # STATE 0
      # Skip the module headers until we reach the song_list.
      if line.startswith('ft_song_list:'):
        state = STATE_1_SONG_LIST
    elif state == STATE_1_SONG_LIST:
      # STATE 1
      # The list of songs in the module, with pointers to their data.
      if not line:
        count = 0
        ignoring = False
        state = STATE_2_SONG_HEADERS
      else:
        m = re.match(r'^\t.word ft_song_(\d+)$', line)
        if not m:
          raise RuntimeError('Did not match "%s"' % line)
        num = int(m.group(1))
        if num < start:
          line = '\t.word 0'
        elif num >= finish:
          line = None
    elif state == STATE_2_SONG_HEADERS:
      # STATE 2
      # The headers for each individual song.
      if not line:
        count += 1
        # Two blank lines separate song headers from the per-song frames.
        if count >= 2:
          state = STATE_3_FRAMES
      else:
        count = 0
      # Ignore song headers for those outside of the range we care about.
      m = re.match(r'^ft_song_(\d+):', line)
      if m:
        num = int(m.group(1))
        ignoring = num < start or num >= finish
      if ignoring:
        line = None
    elif state == STATE_3_FRAMES:
      # STATE 3
      # Frame data for each song.
      m = re.match(r'^ft_s(\d+)_frames:', line)
      if m:
        curr_song = int(m.group(1))
      m = re.match(r'^; DPCM samples', line)
      if m:
        state = STATE_4_DPCM
        line = None
      # This check handles lines before the frames begin, and after DPCM starts.
      if curr_song is not None and line is not None:
        # Match label as something being defined.
        m = re.match(r'^(ft_s.*):', line)
        if m:
          curr_label = m.group(1)
        # Match byte to defined data to save. Might be outside the song range.
        m = re.match(r'^\t\.byte', line)
        if m:
          symbols[curr_label].append(line)
        # Don't output lines for songs outside the range we care about.
        if curr_song < start or curr_song >= finish:
          line = None
        elif curr_label:
          generated.add(curr_label)
          # Match word as pointer to data we depend on. Only track dependencies
          # for songs in the current range, but the data depended upon may be
          # outside the range, which is what `symbols` above handles.
          m = re.match(r'^\t\.word (.*)', line)
          if m:
            text = m.group(1)
            labels = [e.strip() for e in text.split(',')]
            for lbl in labels:
              if lbl not in dependencies:
                dependencies.add(lbl)
    elif state == STATE_4_DPCM:
      # STATE 4
      # Remove all DPCM data.
      line = None
    if line is not None:
      accum.append(line)
  accum.append('')
  accum.append('')
  # Any data dependended upon, but not generated for this song range, is here
  # retrieved from symbols, and then appended to the output
  for sym in dependencies:
    if sym not in generated:
      rows = symbols[sym]
      accum.append(sym)
      accum += rows
  write_output(accum, outfile)


def write_output(accum, outfile):
  fout = open(outfile, 'w')
  for line in accum:
    fout.write(line + '\n')
  fout.close()


def run():
  if len(sys.argv) < 4:
    sys.stderr.write("""
Usage: python nsf_splitter.py [music.asm] [split0,split1] [output_template]
""")
    sys.exit(1)
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
