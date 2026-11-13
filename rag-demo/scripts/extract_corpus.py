# -*- coding: utf-8 -*-
"""Extract main article text from downloaded gov.cn / 12371.cn pages."""
import re, sys
from pathlib import Path
from bs4 import BeautifulSoup

SRC = Path(r"F:/zaqizaba/软件项目管理/zhihui-dangjian/rag-demo/corpus")
OUT = Path(r"F:/zaqizaba/软件项目管理/zhihui-dangjian/rag-demo/backend/corpus")
OUT.mkdir(parents=True, exist_ok=True)

JOBS = [
    ("zhangcheng.html", "page_body", "中国共产党章程（2022年10月22日通过）.txt",
     "中国共产党章程\n（中国共产党第二十次全国代表大会部分修改，2022年10月22日通过）"),
    ("e2afd1ee.html", "UCAP-CONTENT", "中国共产党支部工作条例（试行）.txt",
     "中国共产党支部工作条例（试行）\n（中共中央2018年10月28日印发）"),
    ("fee07e80.html", "UCAP-CONTENT", "习近平在中国共产党第二十次全国代表大会上的报告.txt",
     "高举中国特色社会主义伟大旗帜 为全面建设社会主义现代化国家而团结奋斗\n——在中国共产党第二十次全国代表大会上的报告（2022年10月16日）"),
]

def clean(text: str) -> str:
    text = text.replace("\u3000", " ").replace("\xa0", " ")
    lines = []
    for ln in text.splitlines():
        ln = re.sub(r"[ \t]+", " ", ln).strip()
        if ln:
            lines.append(ln)
    return "\n".join(lines)

for fn, cid, outname, title in JOBS:
    raw = (SRC / fn).read_bytes()
    for enc in ("utf-8", "gb18030"):
        try:
            html = raw.decode(enc); break
        except UnicodeDecodeError:
            continue
    soup = BeautifulSoup(html, "html.parser")
    node = soup.find(id=cid)
    if node is None:
        print("MISSING", fn, cid); sys.exit(1)
    body = clean(node.get_text("\n", strip=True))
    # drop boilerplate lines
    drop = ("扫一扫在手机打开当前页", "责任编辑", "【我要纠错】", "打印", "关闭")
    body = "\n".join(ln for ln in body.splitlines() if not any(d in ln for d in drop))
    text = f"{title}\n\n{body}\n"
    (OUT / outname).write_text(text, encoding="utf-8")
    print(f"{outname}: {len(text)} chars, {text.count(chr(10))+1} lines")
    print("  HEAD:", body[:80].replace("\n", " / "))
    print("  TAIL:", body[-80:].replace("\n", " / "))
