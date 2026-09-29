#!/usr/bin/env python3
"""칸별 싱크 점검 — 각 칸의 문장 / 붙은 클립이 실제로 보여주는 것(clip_index "seen") / 늘린 배율을 나란히 뽑는다.

WHY(2026-09-29 사용자 "싱크가 잘 맞는 영상들로 가득차있어서 더이상 필요없다고 판단한거야? 아니면 그냥 합쳐놓은거"):
대본을 고칠 때 클립은 구절만 옮겨 붙이고 내용 대조를 안 해서, 눈 비비는 장면이 "카메라 비유" 칸에, 기침·폐 점등이 "성대" 칸에
붙은 채 조립됐다. 검사(verify_output)는 배율만 본다 — 문장과 화면이 맞는지는 이 표를 사람이 읽고 판정한다.
배율 3배 이상은 ⚠ — 거의 멈춘 화면이 되기 직전이다. 안 맞는 칸은 기존 클립으로 바꾸고, 없으면 clip_requests.json에 요청한다.

    .venv/bin/python3 scripts/xray_sync_audit.py <topic> [<topic> ...]
"""
import sys,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from lib import tracks
idx=json.load(open(ROOT/"assets_library/xray/clip_index.json"))
def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True).stdout)
    except: return None
def srt(t):
    b=(tracks.output_dir(t)/"narration.srt").read_text().strip().split("\n\n"); out=[]
    for x in b:
        l=x.split("\n"); a,bb=l[1].split(" --> ")
        f=lambda s: int(s[:2])*3600+int(s[3:5])*60+float(s[6:].replace(",","."))
        out.append((f(a),f(bb)," ".join(l[2:])))
    return out
for t in sys.argv[1:]:
    x=json.loads((tracks.data_dir(t)/"xray.json").read_text()); S=srt(t)
    def start(ph):
        for a,b,txt in S:
            if ph in txt: return a
        return None
    rows=x["timeline"]; bounds=[start(r["from"]) for r in rows]
    end_board=start(x["summary_from"]) or S[-1][1]
    print(f"\n### {t}")
    for i,r in enumerate(rows):
        if r["from"]==x["summary_from"]: continue
        s=bounds[i]; e=next((b for b in bounds[i+1:] if b is not None), end_board)
        if s is None: print("  ?",r["from"]); continue
        seg=e-s; text=" ".join(txt for a,b,txt in S if a>=s-0.01 and a<e-0.01)
        for kind in ("act","mech"):
            c=r.get(kind)
            if not c: continue
            d=dur(str(ROOT/f"assets_library/xray/output/{c}.mp4")); st=seg/d if d else 0
            seen=idx.get(c,{}).get("seen","(색인 없음)")
            flag="⚠" if st>=3 else " "
            print(f"  {flag}[{s:5.1f}-{e:5.1f} {seg:4.1f}s x{st:3.1f}] {kind}:{c}\n      문장: {text[:110]}\n      화면: {seen[:110]}")
