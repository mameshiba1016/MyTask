"""Update this project's counts only; overall and other projects are user-managed."""
from collections import Counter
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'progress/shadow-route.json').read_text(encoding='utf-8'))
tasks=data['tasks'];title=data['project'];statuses={'done','in_progress','todo'}
assert tasks and len({t['id'] for t in tasks})==len(tasks),'Task IDs must be unique.'
assert all(t['status'] in statuses and t['title'] for t in tasks),'Unknown status or missing task title.'
assert all(t.get('evidence') for t in tasks if t['status']=='done'),'Completed tasks require evidence.'
counts=Counter(t['status'] for t in tasks);total=len(tasks);done=counts['done'];percent=f'{done/total*100:.1f}'
p=root/'List';raw=p.read_bytes();text=raw.decode('utf-8-sig').replace('\r\n','\n')
a=text.index('【3. '+title+'】');b=text.index('【4. BLIND SPOT】',a);main=text[a:b]
def block(start,end,content):
    global main
    x=main.index(start);y=main.index(end,x+len(start));main=main[:x]+content.rstrip()+'\n\n'+main[y:]
summary=f'''【タスク集計】

全タスク：{total}件
完了タスク：{done} / {total}
作業中：{counts['in_progress']}件
未着手：{counts['todo']}件
進捗率：約{percent}％

集計元：progress/shadow-route.json（更新日：{data['updated']}）
■完了だけを1件として集計。△作業中・□未着手は完了数へ含めない。
新規計画の固定IDを管理し、旧作品のタスク数は継承しない。
単純タスク数の割合であり、作業量やゲーム品質の完成率ではない。'''
block('【タスク集計】' if '【タスク集計】' in main else '完了タスク・全タスク：','【現在の状態】',summary)
def rows(status,mark):return '\n'.join(mark+' '+t['id']+' '+t['title'] for t in tasks if t['status']==status)
block('【タスク一覧：完了】' if '【タスク一覧：完了】' in main else '【完了済みの主な内容】','【確認範囲と制限】','【タスク一覧：完了】\n\n'+rows('done','■'))
block('【タスク一覧：作業中】' if '【タスク一覧：作業中】' in main else '【現在作業中・今後の主な課題】','【次の大目標】','【タスク一覧：作業中】\n\n'+rows('in_progress','△')+'\n\n【タスク一覧：未着手】\n\n'+rows('todo','□'))
text=text[:a]+main+text[b:]
pattern=r'(?m)^(・'+re.escape(title)+r'\n)　[^\n]+\n　進捗率：[^\n]+'
text,n=re.subn(pattern,lambda m:m[1]+f'　{done} / {total}完了\n　進捗率：約{percent}％',text)
assert n==2,'Expected the top and closing project summaries.'
p.write_bytes((b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+text.replace('\n','\r\n').encode('utf-8'))
print(f'SHADOW ROUTE: {done}/{total} ({percent}%), in progress={counts["in_progress"]}, todo={counts["todo"]}')
