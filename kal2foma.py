import sys
import shlex

new_word = True
for line in sys.stdin:
    if line[:2] == '"<':
        new_word = True
        continue
    if not new_word or line.strip() == "":
        continue
    if "?" in line:
        continue
    if "%" in line:
        anal = line.strip().split("%")[0]
    else:
        anal = line.strip().split(" @")[0]
    try:
        print("+".join(shlex.split(anal)))
    except:
        print(anal, file=sys.stderr)
    new_word = False
