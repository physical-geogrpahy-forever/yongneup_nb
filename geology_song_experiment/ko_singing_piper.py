#!/usr/bin/env python3
"""Korean TTS singing proof: coherent Korean phrases, note-aligned pitch map."""
import base64, gzip, io, os, math, csv, subprocess, wave
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa
import parselmouth
from parselmouth.praat import call

SCORE="H4sIAEYEx2oC/11V204bMRB977dYaH33/l2AUCGllyCxJQgSpRKIXqiakkTw0P5QvPsP9cysPVYe5+x4fOb4zKwUjWhOrLBe9GfP7yQGGZj9SoA84Yz7rwhQhmtE/2WfADVmOCPixRQBm4F+DYBOGRLDm3kKTfn6NIEwp7fisAcONhf04rCZIDBmWDGcQ0GXMhRWOF+mMNBXJeKPCwhzuhL9bZeANhdMGZdTBArD+AFukE1OsaJ/+UlIuZR4Sklt2MTqFGJVasyeMa76Xu4A0XwxMU1IUe/wtgHEYC9J3sN2DbEr6s7uMa70pho+V23GdhJy3E9gDfvdJSG2IFS5pX78WFex6shEZQW8Gk+obAYv8xnJj0cqKUVv40U8W0BsiooPVxhXulJVW2lPVW1lie1fQFzVz2xNCKtNdTz1k3VSbAvURFW+iI+3gLRs3aHbE8Lemf4B7zbUT6q6eoRYZWZxc40xc42zV0DKqydN3n8kpHIGqKJNVjJx+f1GCKuN/LXFfiDjGTTQLn8/7K4wzieA/XdAPFcd2WdnwIuhSjpQP4nbCqqYoms8+4Zx5ZMpMDOymsfXNSH8PsjFKOIqRyZG55h4GCM0aDp0MBcm5NNDd49xpeEG9DEtaxg/Twk50tA2VbeLB0KKhnGFObJoOIebrCon0K1WsYY01VZXVekezRrSm1uTNRzOYb9Yl78fXv5hzDxoyq2vJmdxSgj3jMrbQP4N46K143yCxqBasqDG87hEkwySJ9OVLsg7zlZKoPudqxhgX85Vs7u4A8SXjdBBn4mKRr2nUDOVwhel7eB1UelujnHlNOTgTfWGyMEb9tbwCbzlbd6p8Qm2lHfjjXh/4O15s8OYp5P2QpDVhu06Qsp+iWuY2KAqHps7QrjzDtwVTNmo2wnG1dZFBwfLW3dYXhPCu2INbxpc9SvENw31lqKbwvgrRP+FNnMl94X2+B/SNtnB/Qp0bmWerLiCCq0CxdL0zh7+A+TYx3fNBwAA"
LYRIC_LINES=[
"사십육억 년 전에 지구가 탄생",
"명왕누대 첫 지각 달이 생기고",
"시생누대 초시생 고시생 지나",
"중시생과 신시생 대륙핵 성장",
"바닷속의 미생물 광합성 시작",
"남세균 광합성해",
"한반도의 오래된 지각의 바탕",
"경기 영남 육괴에",
"시생대의 옛 암석 고원생대 편마암",
"열과 압력 받아 변성 흔적 남아",
"지각이 자란다",
]
GROUP_BARS=[(1,2),(3,4),(5,6),(7,8),(9,10),(11,12),(13,14),(15,16),(17,20),(21,22),(23,24)]
BEAT_SEC=60/156
OUT=Path("output");OUT.mkdir(exist_ok=True)
MODEL=Path("ko_KR-kss-medium.onnx")
def shell(cmd,**kwargs):
 print("RUN",cmd,flush=True)
 return subprocess.run(cmd,check=True,**kwargs)
rows=[]
for line in gzip.decompress(base64.b64decode(SCORE)).decode().splitlines():
 v,on,d,p,sy=line.split(",")
 rows.append(dict(start=float(on),dur=float(d),pitch=int(p),char=sy))
assert len(rows)==118
assert "".join(x["char"] for x in rows)=="".join(ch for s in LYRIC_LINES for ch in s if "가"<=ch<="힣")
SR=22050
L=int((96*BEAT_SEC+1.0)*SR)
tts=np.zeros(L,dtype=np.float32); pitched=np.zeros(L,dtype=np.float32)
pitch_errors=[]
for i,(phrase,(a,b)) in enumerate(zip(LYRIC_LINES,GROUP_BARS),1):
 first=(a-1)*4; end=b*4
 start_sec=first*BEAT_SEC; dur_sec=(end-first)*BEAT_SEC
 selected=[x for x in rows if x["start"]>=first and x["start"]<end]
 assert "".join(x["char"] for x in selected)=="".join(c for c in phrase if "가"<=c<="힣")
 tmp=Path(f"voice_line_{i:02d}.wav")
 shell(["python","-m","piper","--model",str(MODEL),"--output_file",str(tmp)],input=phrase+"\n",text=True,timeout=100)
 y,sr=sf.read(tmp)
 if y.ndim>1:y=np.mean(y,axis=1)
 if sr!=SR:y=librosa.resample(y.astype(np.float32),orig_sr=sr,target_sr=SR)
 y=np.asarray(y,np.float32)
 # Speech alignment: preserve a coherent spoken phrase, then fit it to the full musical phrase.
 nz=np.flatnonzero(np.abs(y)>.006)
 if len(nz)>100:
  y=y[max(0,nz[0]-SR//20):min(len(y),nz[-1]+SR//10)]
 target_len=round(dur_sec*SR)
 rate=len(y)/target_len
 stretched=librosa.effects.time_stretch(y,rate=max(.4,min(2.8,rate)))
 if len(stretched)<target_len:stretched=np.pad(stretched,(0,target_len-len(stretched)))
 stretched=stretched[:target_len]
 low=.02
 fade=min(int(.025*SR),len(stretched)//10)
 stretched[:fade]*=np.linspace(0,1,fade)
 stretched[-fade:]*=np.linspace(1,0,fade)
 beg=round(start_sec*SR)
 tts[beg:beg+target_len]+=stretched
 # Prosody: one measured Korean utterance per line; change its fundamental frequency along the score.
 try:
  sound=parselmouth.Sound(stretched,sampling_frequency=SR)
  manip=call(sound,"To Manipulation",.01,75,650)
  tier=call(manip,"Extract pitch tier")
  call(tier,"Remove points between",0,sound.duration)
  # Music contours are linear within phonemes but retain consonants & vowels.
  for n in selected:
   freq=440*2**((n["pitch"]-69)/12)
   ts=(n["start"]-first)*BEAT_SEC
   for offset in (.02,max(.03,n["dur"]*BEAT_SEC*.70)):
    pos=min(sound.duration-.01,ts+offset)
    if pos>.001: call(tier,"Add point",pos,float(freq))
  call([manip,tier],"Replace pitch tier")
  res=call(manip,"Get resynthesis (overlap-add)")
  vo=res.values[0].astype(np.float32)
  if len(vo)<target_len:vo=np.pad(vo,(0,target_len-len(vo)))
  vo=vo[:target_len]
  vo[:fade]*=np.linspace(0,1,fade);vo[-fade:]*=np.linspace(1,0,fade)
 except Exception as e:
  pitch_errors.append(str(e))
  vo=stretched
 pitched[beg:beg+target_len]+=vo
 print(f"LINE {i} {phrase} original={len(y)/SR:.2f}s target={dur_sec:.2f}s voiced={np.max(np.abs(vo)):.3f}",flush=True)
# Subdued chordal accompaniment for intelligibility.
accomp=np.zeros(L,dtype=np.float32)
chords=[(57,60,64),(60,64,67),(62,65,69),(57,60,64)]*6
for j,chord in enumerate(chords):
 st=round(j*4*BEAT_SEC*SR)
 length=min(int(3.5*BEAT_SEC*SR),L-st)
 t=np.arange(length)/SR
 a=np.zeros(length,np.float32)
 for note in chord:
  f=440*2**((note-69-12)/12)
  a+=np.sin(2*np.pi*f*t)*.015
 a*=np.minimum(1,t/.04)*np.exp(-1.7*t)
 accomp[st:st+length]+=a
def save(name,x):
 x=np.nan_to_num(x)
 peak=np.max(np.abs(x))
 if peak>.93: x=x*(.93/peak)
 sf.write(OUT/(name+".wav"),x,SR)
 shell(["ffmpeg","-y","-loglevel","error","-i",str(OUT/(name+".wav")),"-b:a","192k",str(OUT/(name+".mp3"))])
save("1절_한국어_명료도_원음성",tts)
save("1절_한국어_음정적용_가창시험",pitched)
save("1절_가창시험_반주포함",pitched*.9+accomp*.55)
(OUT/"synthesis_report.txt").write_text("Lines: 11; syllables: 118; Korean Piper full-phrase TTS; model: official Korean kss medium. Pitch editing failures: "+repr(pitch_errors)+"\n",encoding="utf-8")
print("DONE",pitch_errors,flush=True)
