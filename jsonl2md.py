#!/usr/bin/env python3
"""Claude Code 会话 JSONL -> 可读 Markdown。用法: python jsonl2md.py session.jsonl [out.md] [--full]"""
import json, sys, re
from datetime import datetime, timezone
args=[a for a in sys.argv[1:] if not a.startswith('--')]
FULL='--full' in sys.argv
src=args[0]; dst=args[1] if len(args)>1 else re.sub(r'\.jsonl$','',src)+'.md'
LIMIT=None if FULL else 3000
def ts(s):
    try: return datetime.fromisoformat(s.replace('Z','+00:00')).astimezone().strftime('%Y-%m-%d %H:%M:%S')
    except Exception: return ''
def fence(t,lang=''):
    t=str(t); n=3
    while '`'*n in t: n+=1
    return f"{'`'*n}{lang}\n{t}\n{'`'*n}"
def clip(t):
    t=str(t)
    if LIMIT and len(t)>LIMIT: return t[:LIMIT]+f"\n…（已截断，原长 {len(t)} 字符；用 --full 可完整导出）"
    return t
def details(summary,body): return f"<details>\n<summary>{summary}</summary>\n\n{body}\n\n</details>\n"
def result_text(c):
    if isinstance(c,str): return c
    if isinstance(c,list):
        return '\n'.join(b.get('text','') if b.get('type')=='text' else f"[{b.get('type')}]" for b in c if isinstance(b,dict))
    return json.dumps(c,ensure_ascii=False,indent=2)
def tool_use(b):
    name=b.get('name','?'); inp=b.get('input',{}) or {}
    brief=inp.get('file_path') or inp.get('pattern') or inp.get('command') or inp.get('description') or ''
    brief=str(brief).replace('\n',' ')[:100]
    parts=[]
    for k,v in inp.items():
        if isinstance(v,str) and ('\n' in v or len(v)>120): parts.append(f"**{k}:**\n\n{fence(v)}")   # 写入/编辑内容完整保留
        else: parts.append(f"**{k}:** `{json.dumps(v,ensure_ascii=False) if not isinstance(v,str) else v}`")
    return details(f"🔧 工具调用：<b>{name}</b> {('— <code>'+brief+'</code>') if brief else ''}",'\n\n'.join(parts) or '（无参数）')
out=[]; title=None; n_user=n_asst=0; first=last=None
for line in open(src,encoding='utf-8'):
    line=line.strip()
    if not line: continue
    try: d=json.loads(line)
    except Exception: continue
    t=d.get('type')
    if t=='ai-title': title=d.get('aiTitle') or title; continue
    if t=='system':
        st=d.get('subtype')
        if st=='compact_boundary':
            m=d.get('compactMetadata',{})
            out.append(f"\n---\n\n> ✂️ **对话在此处被压缩（compact）** · {ts(d.get('timestamp',''))} · 触发方式: {m.get('trigger','?')} · {m.get('preTokens','?')} → {m.get('postTokens','?')} tokens\n\n---\n")
        elif st=='away_summary':
            out.append(f"> 💤 *离开期间摘要（{ts(d.get('timestamp',''))}）：* {d.get('content','')}\n")
        continue
    if t not in('user','assistant'): continue
    if d.get('isSidechain'): continue
    msg=d.get('message',{}) or {}; c=msg.get('content'); when=ts(d.get('timestamp',''))
    first=first or when; last=when or last
    if t=='user':
        if d.get('isCompactSummary'):
            out.append(f"## 📦 压缩摘要 · {when}\n\n{details('展开查看 compact 生成的摘要',result_text(c))}"); continue
        if isinstance(c,str): blocks=[{'type':'text','text':c}]
        else: blocks=c or []
        for b in blocks:
            bt=b.get('type')
            if bt=='text':
                if d.get('isMeta'): continue
                txt=b.get('text','')
                cmd=re.search(r'<command-name>(.*?)</command-name>',txt,re.S)
                if cmd:
                    a=re.search(r'<command-args>(.*?)</command-args>',txt,re.S)
                    out.append(f"> ⌨️ `{cmd.group(1).strip()} {(a.group(1).strip() if a else '')}`".rstrip()+f" · {when}\n"); continue
                if txt.lstrip().startswith(('<local-command','<system-reminder')): continue
                n_user+=1
                out.append(f"## 👤 用户 #{n_user} · {when}\n\n{txt}\n")
            elif bt=='tool_result':
                body=clip(result_text(b.get('content')))
                tag='❌ 工具报错' if b.get('is_error') else '📥 工具结果'
                out.append(details(f"{tag}（{len(result_text(b.get('content')))} 字符）",fence(body)))
            elif bt=='image': out.append("*[用户附图]*\n")
    else:
        for b in c or []:
            bt=b.get('type')
            if bt=='text' and b.get('text','').strip():
                n_asst+=1
                out.append(f"## 🤖 Claude · {when}\n\n{b['text']}\n")
            elif bt=='thinking' and b.get('thinking','').strip():
                out.append(details('💭 思考过程',b['thinking']))
            elif bt=='tool_use': out.append(tool_use(b))
head=f"# {title or '对话记录'}\n\n- **来源文件：** `{src.split('/')[-1]}`\n- **时间范围：** {first} → {last}\n- **用户消息：** {n_user} 条 · **Claude 回复：** {n_asst} 条\n\n---\n"
open(dst,'w',encoding='utf-8').write(head+'\n'.join(out)+'\n')
print(dst,n_user,n_asst)
