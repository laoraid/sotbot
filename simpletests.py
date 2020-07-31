import re

p = r'[^ㄱ-ㅎㅏ-ㅣ가-힣]'

arr = ['asieg gegif', '시발', 'ㅅㄱ', 'ㅅ바발ㅏㅏ', 'ㅏㅏㅐㅏ', '아 awef ㄱ','wegieng eigeugghebtkejt!']

for a in arr:
    if re.match(p, a) is not None:
        print(f"{a} 는 한글안들어감")
    else:
        print(f"{a} 는 한글들어감")