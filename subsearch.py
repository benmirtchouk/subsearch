import sys
import os
import codecs
import datetime
import srt
import re
import unicodedata
import argparse

'''
TODO
  - more command line arguments
  - smi format
  - automate getting input data
'''

hdiv = '-' * 100
vdiv = ' ' * 5 + '|' + ' ' * 5

class bcolors:
  RED_BACKGROUND = '\033[41m'
  RED_TEXT = '\033[91m'
  WARNING = '\033[93m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

def extract_query(filename, query):
  pat = re.compile(f'\\b{query}\\b', flags=re.IGNORECASE)
  
  text = ''
  with codecs.open(filename, 'r', encoding='utf8') as f:
    text = f.read()
  subs = list(srt.parse(text))
  
  hits = []
  for i, sub in enumerate(subs):
    if pat.search(sub.content) is not None:
      hits.append(i)
  
  if len(hits) == 0:
    return None, None
    
  output = set()
  for idx in hits:
    i = idx
    while i >= 0:
      if idx - i <= interval_cnt \
         or subs[idx].start - subs[i].end < interval_time \
         and i not in output:
        output.add(i)
        i -= 1
      else:
        break
        
    i = idx + 1
    while i < len(subs):
      if i - idx <= interval_cnt \
         or subs[i].start - subs[idx].end < interval_time \
         and i not in output:
        output.add(i)
        i += 1
      else:
        break
        
  output = sorted(list(output))
  intervals = []
  st, en = -17, -17
  for i in output:
    if i == en + 1:
      en = i
    else:
      intervals.append((st,en))
      st = i
      en = i
  
  intervals.append((st,en))
  return subs, intervals[1:]
    
def extract_ref(filename, subs_query, output_query):
  text = ''
  with codecs.open(filename, 'r', encoding='utf8') as f:
    text = f.read()
  subs = list(srt.parse(text))

  i = 0
  output = []
  for a,b in output_query:
    start = subs_query[a].start
    end = subs_query[b].end
  
    while i < len(subs) and subs[i].end < start:
      i += 1
    
    st = i
    while i + 1 < len(subs) and subs[i + 1].start <= end:
      i += 1
    
    if st == len(subs):
      output.append((0, -1))
    else:
      output.append((st, i))
  
  return subs, output

def clean(s):
  return re.sub('\n+', '\n', s).lstrip().rstrip()

def get_width(s):
  return sum(2 if unicodedata.east_asian_width(c) == 'W' else 1 for c in s)
  
def widen(s):
  return ''.join(c + (' ' if unicodedata.east_asian_width(c) != 'W' else '') for c in s)

def disp(output_query, subs_query, output_ref, subs_ref, query, reflang):
  def color(s):
    return re.sub(f'(\\b)({query})(\\b)', f'\\1{bcolors.RED_BACKGROUND}\\2{bcolors.ENDC}\\3', s, flags=re.IGNORECASE)
  
  print(hdiv)
  for (a,b),(c,d) in zip(output_query, output_ref):
    s_query = clean('\n'.join(subs_query[i].content for i in range(a, b+1))).split('\n')
    s_ref = clean('\n'.join(subs_ref[i].content for i in range(c, d+1))).split('\n')
    
    if s_ref == ['']:
      print(f'{bcolors.WARNING}WARNING: no matching {reflang} subtitle found for timestamp {subs_query[a].start}{bcolors.ENDC}')
      continue
    
    # print('s_query is:\n', s_query)
    # print('\n\ns_ref is:\n', s_ref, '\n\n')
    
    mxlen = max(get_width(s) for s in s_query)
    diff = abs(len(s_query) - len(s_ref)) // 2
    
    for i in range(max(len(s_query), len(s_ref))):
      if len(s_query) < len(s_ref):
        if 0 <= i - diff < len(s_query):
          print(color(s_query[i - diff]), end=' ' * (mxlen - get_width(s_query[i - diff])))
        else:
          print(' ' * mxlen, end='')
      else:
        print(color(s_query[i]), end=' ' * (mxlen - get_width(s_query[i])))
      
      
      print(vdiv, end='')

      if len(s_ref) < len(s_query):
        if 0 <= i - diff < len(s_ref):
          print(s_ref[i - diff])
        else:
          print('')
      else:
        print(s_ref[i])
    
    print(hdiv)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Find subtitles containing a word in a query and corresponding reference language.')
  parser.add_argument('qlang', type=str, help='the query language')
  parser.add_argument('rlang', type=str, help='the reference language')
  parser.add_argument('query', type=str, help='a word to search for in the query language')
  parser.add_argument('--it', type=float, metavar="t_interval", default=10, help='the minimum number of seconds to keep surrounding a match')
  parser.add_argument('--iq', type=int, metavar="q_interval", default=2, help='the minimum number of subtitles to keep surrounding a match')
  args = parser.parse_args()
  # print(args)
  

  querylang = args.qlang
  reflang = args.rlang
  query = args.query.lower()
  interval_time = datetime.timedelta(seconds=args.it)
  interval_cnt = args.iq

  data = os.listdir('data')

  videos = {}
  for f in data:
    filename = f[:f.rfind('.')]
    name, lang = filename.split('_')
    if name not in videos:
      videos[name] = []
    videos[name].append(lang)

  # print('found data files:\n')
  # for v in videos:
  #   print(v)
  #   for lang in videos[v]:
  #     print('  - ' + lang)

  for v in videos:
    print(f'Searching {v}...')
    if querylang not in videos[v] or reflang not in videos[v]:
      continue
    
    subs_query, output_query = extract_query(f'data/{v}_{querylang}.srt', query)
    if subs_query is None:
      continue
    
    subs_ref, output_ref = extract_ref(f'data/{v}_{reflang}.srt', subs_query, output_query)
    
    # print('output_query', output_query)
    # print('len query subs', len(subs_query))
    # print('output_ref', output_ref)
    # print('len ref subs', len(subs_ref))
    disp(output_query, subs_query, output_ref, subs_ref, query, reflang)