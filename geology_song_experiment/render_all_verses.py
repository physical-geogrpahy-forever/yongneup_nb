#!/usr/bin/env python3
"""Render all 12 original-sheet geology mnemonic verses from Korean Piper TTS."""
import base64,gzip,json,subprocess,re
from pathlib import Path
import numpy as np,soundfile as sf

LYRICS_B64="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"
verses=json.loads(gzip.decompress(base64.b64decode(LYRICS_B64)))
assert len(verses)==12 and all(len(x)==11 for x in verses)
original=Path("geology_song_experiment/ko_singing_piper.py").read_text(encoding="utf-8")
pat=re.compile(r"LYRIC_LINES=\[.*?\]\nGROUP_BARS=",re.S)
oldcheck='assert len(rows)==118\nassert "".join(x["char"] for x in rows)=="".join(ch for s in LYRIC_LINES for ch in s if "가"<=ch<="힣")'
assert oldcheck in original
baseoutputs=Path("output")
baseoutputs.mkdir(exist_ok=True)
for idx,lines in enumerate(verses,1):
 script=pat.sub("LYRIC_LINES="+repr(lines)+"\nGROUP_BARS=",original,count=1)
 assert script!=original
 script=script.replace(oldcheck,
  'assert len(rows)==118\nsyllables=[c for line in LYRIC_LINES for c in line if "가"<=c<="힣"]\nassert len(syllables)==118,(len(syllables),LYRIC_LINES)\nfor note, c in zip(rows,syllables): note["char"]=c\nassert "".join(x["char"] for x in rows)=="".join(syllables)')
 script=script.replace('OUT=Path("output");OUT.mkdir(exist_ok=True)',f'OUT=Path("output/verse_{idx:02d}");OUT.mkdir(parents=True,exist_ok=True)')
 tmp=Path(f"/tmp/song_{idx:02d}.py");tmp.write_text(script,encoding="utf-8")
 p=subprocess.run(["python",str(tmp)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 print("VERSE",idx,"EXIT",p.returncode,"LASTLOG",p.stdout[-1500:],flush=True)
 if p.returncode:
  raise RuntimeError(f"verse {idx} failed:\n{p.stdout}")
# Assemble 12 original 24-bar musical verses
SR=22050
for name in ("1절_한국어_명료도_원음성","1절_한국어_음정적용_가창시험","1절_가창시험_반주포함"):
 segments=[]
 for i in range(1,13):
  y,sr=sf.read(baseoutputs/f"verse_{i:02d}"/(name+".wav"))
  assert sr==SR and y.ndim==1
  segments.append(y)
 combined=np.concatenate(segments)
 peak=np.max(np.abs(combined))
 if peak>.93:combined*=.93/peak
 outname={"1절_한국어_명료도_원음성":"12절_한국어_명료도_원음성","1절_한국어_음정적용_가창시험":"12절_음정적용_가창시험","1절_가창시험_반주포함":"12절_한국어_가창시험_반주포함"}[name]
 path=baseoutputs/(outname+".wav");sf.write(path,combined,SR)
 subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(path),"-b:a","192k",str(path.with_suffix(".mp3"))],check=True)
 print("FULL SONG",path.with_suffix(".mp3"),"seconds",len(combined)/SR,"peak",np.max(np.abs(combined)),flush=True)
(baseoutputs/"status.txt").write_text("12 Korean TTS verses rendered from supplied 24-bar score and synthesized as phrase-level vocals. Melodic note pitch resynthesis is approximate, not a natural singer. Models from rhasspy/piper-voices. 11 lines * 12 verses.\n",encoding="utf-8")
