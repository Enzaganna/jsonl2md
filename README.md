# Tool Description
Claude Code session can easily reach context limit (200k for opus46, 1M for 46 above) and `auto compact` feature breaks the existing chat chain, makes the earlier chat unscrollable within CLI window.  
This tool extract jsonl session file to md file to make the whole chat history readable.

# How to use
Use `session.jsonl` as example. Change the file name promptly.
1. output md file to same directory
```python
python jsonl2md.py session.jsonl
```
2. Output md file with custom name and directroy
```python
`python jsonl2md.py session.jsonl Mychat.md` #custom name
`python jsonl2md.py session.jsonl ~/notes/2026-10.md`   #custom directory
```
3. Output full session with tool usage
```python
python jsonl2md.py session.jsonl --full
python jsonl2md.py session.jsonl out.md --full   # --full 放在任意位置都可以
```
----
# 基本用法
1. 准备好jsonl，输出到同目录，生成同名.md
python jsonl2md.py session.jsonl

2. 指定输出路径
python jsonl2md.py session.jsonl 我的对话.md

3. 完整导出，不截断工具结果
python jsonl2md.py session.jsonl --full
python jsonl2md.py session.jsonl out.md --full   # --full 放在任意位置都可以
