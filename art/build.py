"""BOUND artwork revision. Off-chain artwork only; no tier selection implementation.
Run: python build.py (requires Pillow). All coordinates derive from shared anchors.
"""
from pathlib import Path
import json, hashlib, itertools
from PIL import Image, ImageDraw
import prototype as p

ROOT = Path(__file__).resolve().parent
PAL, S, STACK = p.PAL, p.S, p.STACK
L, R, E, J = p.EYE_L, p.EYE_R, p.EYE_LINE, p.JAW_ROWS[0]
C = (L + R + 1)//2
TOP = min(y for y in range(S) if any(p.in_head(x,y) for x in range(S)))
TABLE = {
 'wrap': [('bone',2600),('ash',2000),('linen',1700),('stained',1200),('lapis',900),('verdigris',600),('bitumen',450),('gold_threaded',350),('unraveling',150),('alabaster',50)],
 'head': [('none',3000),('nemes',2200),('cap',1500),('circlet',1100),('jackal_mask',800),('falcon_mask',600),('crown',400),('horned_crown',250),('sun_disk',100),('gold_crown',50)],
 'eyes': [('hollow',2800),('painted',2400),('lapis',1600),('closed',1200),('glowing',900),('cracked',550),('gold',350),('twin_pupils',150),('void',50)],
 'jaw': [('wrapped',3400),('slack',2300),('grin',1700),('snarl',1200),('gilded',800),('scarab_in_mouth',450),('coin_in_mouth',150)],
 'bind': [('none',3500),('cord',2400),('leather_strap',1600),('chain',1100),('seal',700),('gold_wire',450),('broken_chain',200),('thread_of_light',50)],
 'charm': [('none',3600),('scarab',2200),('ankh',1500),('eye_amulet',1100),('coin',800),('vial',400),('key',250),('paired_scarabs',120),('hourglass',30)],
 'ground': [('sand',2600),('tomb',2100),('lapis',1600),('torchlit',1200),('night_sky',900),('flood',700),('gold',500),('void',300),('eclipse',100)]}
RAMPS = dict(bone=('bone','bone_sh','bone_dk'), ash=('ash','ash_sh','ash_dk'), linen=('linen','linen_sh','linen_dk'), stained=('linen_sh','linen_dk','wall'), lapis=('lapis_lt','lapis','lapis_dk'), verdigris=('glow','ash_sh','lapis_sh'), bitumen=('ash_dk','shadow','void'), gold_threaded=('linen','linen_sh','wall'), unraveling=('bone','bone_sh','bone_dk'), alabaster=('bone','ash','ash_sh'))

def canvas(): return p.blank()
def dot(im,x,y,col): p.px(im,x,y,PAL[col])
def line(im,xy,col,width=1): ImageDraw.Draw(im).line(xy,fill=PAL[col],width=width)
def box(im,xy,col): ImageDraw.Draw(im).rectangle(xy,fill=PAL[col])
def poly(im,xy,col): ImageDraw.Draw(im).polygon(xy,fill=PAL[col])
def body(x,y): return 0<=x<S and 0<=y<S and (p.in_head(x,y) or p.in_shoulder(x,y))

def wrap(name):
 im=canvas(); lt,md,dk=RAMPS[name]
 for y in range(S):
  for x in range(S):
   if not body(x,y): continue
   seam=(y+(x-C)//6)%4==0
   col=dk if seam else (md if x>C+3 or x<L-2 else lt)
   if not all(body(x+dx,y+dy) for dx,dy in [(1,0),(-1,0),(0,-1),(0,1)]): col='shadow'
   dot(im,x,y,col)
 # Separate sockets, retaining a wrapped nose bridge; no continuous black bar.
 for a in [L,R]:
  poly(im,[(a-2,E-1),(a-1,E-2),(a+1,E-2),(a+2,E-1),(a+2,E+1),(a,E+2),(a-2,E+1)],'shadow')
  box(im,(a-1,E-1,a+1,E+1),'void')
  line(im,[(a-1,E+2),(a+1,E+2)],dk)
 dot(im,C-1,E,lt); dot(im,C,E+1,md)
 if name=='stained':
  for x,y in [(L-2,J-2),(R+2,TOP+4),(C+2,J+4),(L-3,J+8)]:
   dot(im,x,y,'wall'); dot(im,x+1,y,'linen_dk')
 if name=='gold_threaded':
  line(im,[(L-2,TOP+4),(R+2,TOP+2)],'sand'); line(im,[(L,J+7),(R+4,J+9)],'sand')
 if name=='alabaster':
  for y in [TOP+2,TOP+5,J+3]: dot(im,L,y,'glow')
 if name=='unraveling':
  line(im,[(R+3,J-2),(R+5,J),(R+6,J-1),(R+7,J-1)],'shadow',3)
  line(im,[(R+3,J-2),(R+5,J),(R+6,J-1),(R+7,J-1)],'bone')
  line(im,[(L-3,J+5),(L-6,J+3),(L-7,J+5)],'bone_sh',2)
 return im

def eyes(name):
 im=canvas()
 for a in [L,R]:
  if name=='hollow':
   line(im,[(a-1,E+1),(a+1,E+1)],'ash_dk'); dot(im,a-1,E,'wall_dk')
  elif name=='closed':
   line(im,[(a-2,E-1),(a-1,E),(a+1,E),(a+2,E-1)],'bone_dk')
  elif name=='painted':
   line(im,[(a-2,E-1),(a+1,E-1),(a+2,E)],'lapis_lt'); dot(im,a,E,'bone'); dot(im,a+1,E+2,'lapis')
  elif name in ['lapis','gold','glowing']:
   col={'lapis':'lapis_lt','gold':'linen','glowing':'glow'}[name]
   box(im,(a-1,E,a+1,E+1),col); dot(im,a,E,'void' if name!='glowing' else 'bone')
   if name=='glowing': line(im,[(a-1,E-1),(a+1,E-1)],'lapis')
  elif name=='cracked':
   dot(im,a,E,'bone'); line(im,[(a+1,E-2),(a,E-1),(a+1,E),(a,E+2)],'ash_sh')
  elif name=='twin_pupils':
   dot(im,a-1,E,'gold'); dot(im,a+1,E,'glow')
  elif name=='void':
   box(im,(a-1,E-1,a+1,E+1),'void'); dot(im,a,E+2,'lapis_lt'); dot(im,a,E+3,'lapis')
 return im

def jaw(name):
 im=canvas()
 if name=='wrapped': return im
 if name=='slack':
  box(im,(C-2,J,C+1,J+2),'shadow'); box(im,(C-1,J,C,J+2),'void'); dot(im,C-1,J+3,'bone_dk')
 elif name in ['grin','gilded','snarl']:
  poly(im,[(C-4,J-1),(C-2,J),(C+2,J),(C+3,J-1),(C+2,J+2),(C-2,J+2)],'void')
  for x in range(C-3,C+3): dot(im,x,J,'linen' if name=='gilded' else 'bone')
  if name=='snarl':
   box(im,(C-4,J-1,C-1,J),'shadow'); dot(im,C+2,J+1,'bone'); dot(im,C-2,J+1,'bone')
  else:
   for x in [C-2,C,C+2]: dot(im,x,J+1,'bone_sh' if name=='grin' else 'sand')
 else:
  box(im,(C-3,J,C+2,J+1),'void')
  col='gold' if name=='coin_in_mouth' else 'lapis_lt'
  box(im,(C-1,J,C,J+2),col); dot(im,C,J+1,'gold_sh' if name=='coin_in_mouth' else 'lapis_dk')
 return im

def head(name):
 im=canvas(); t=TOP
 if name=='none': return im
 if name=='nemes':
  poly(im,[(L-2,t),(R+1,t),(R+5,t+4),(R+4,J+3),(R+2,J+3),(R+2,t+5),(L-3,t+5),(L-3,J+3),(L-5,J+3),(L-6,t+4)],'shadow')
  for y in range(t+1,t+6): line(im,[(L-3,y),(R+2,y)],'lapis_lt' if y%2 else 'lapis_sh')
  for y in range(t+5,J+3):
   for x in [L-5,L-4,R+3,R+4]: dot(im,x,y,'linen_sh' if y%3==0 else 'lapis')
 elif name=='cap':
  poly(im,[(L-2,t+2),(L,t-1),(R-1,t-1),(R+2,t+2),(R+2,t+4),(L-2,t+4)],'shadow')
  box(im,(L-1,t+1,R+1,t+3),'linen_dk'); line(im,[(L,t),(R-1,t)],'linen')
 elif name=='circlet':
  box(im,(L-3,t+3,R+3,t+4),'shadow'); line(im,[(L-2,t+3),(R+2,t+3)],'ash_sh'); dot(im,C-1,t+2,'lapis_lt')
 elif name in ['jackal_mask','falcon_mask']:
  poly(im,[(L-3,t+5),(L-2,t),(R+1,t),(R+3,t+5),(C,t+7)],'shadow')
  if name=='jackal_mask':
   poly(im,[(L-2,t+1),(L-2,t-4),(L+1,t)],'void'); poly(im,[(R-2,t),(R+1,t-4),(R+1,t+1)],'void')
   dot(im,L,t+3,'linen'); dot(im,R-1,t+3,'linen'); box(im,(C-1,t+4,C,t+5),'ash_dk')
  else:
   poly(im,[(L-2,t+2),(C-1,t),(R+1,t+2),(C,t+5)],'lapis')
   poly(im,[(C-1,t+3),(C+2,t+4),(C-1,t+6)],'linen'); dot(im,L,t+2,'glow')
 elif name in ['crown','gold_crown','horned_crown']:
  col='gold' if name!='crown' else 'bone'
  box(im,(L-2,t+1,R+2,t+4),'shadow'); box(im,(L-1,t+2,R+1,t+3),col)
  for x in [L-1,C-1,R+1]:
   box(im,(x-1,t-2,x+1,t+1),'shadow'); line(im,[(x,t-1),(x,t+1)],col)
  dot(im,C-1,t+2,'lapis_lt')
  if name=='horned_crown':
   line(im,[(L-2,t+2),(L-4,t),(L-5,t-3)],'bone',2); line(im,[(R+2,t+2),(R+4,t),(R+5,t-3)],'bone',2)
 elif name=='sun_disk':
  ImageDraw.Draw(im).ellipse((C-4,t-4,C+3,t+3),fill=PAL['shadow'])
  ImageDraw.Draw(im).ellipse((C-3,t-3,C+2,t+2),fill=PAL['gold'])
  line(im,[(C,t-2),(C+1,t)],'gold_sh'); line(im,[(L-1,t+4),(R,t+4)],'gold_sh')
 return im

def bind(name):
 im=canvas(); y=J+7
 if name=='none': return im
 if name in ['cord','leather_strap','gold_wire','thread_of_light']:
  col={'cord':'linen_dk','leather_strap':'wall','gold_wire':'sand','thread_of_light':'glow'}[name]
  line(im,[(L-4,y),(R+7,y+4)],'shadow',3)
  line(im,[(L-4,y),(R+7,y+4)],col,2 if name=='leather_strap' else 1)
 elif name in ['chain','broken_chain']:
  for x in range(L-4,R+7,3):
   if name=='broken_chain' and C-2<=x<=C+2: continue
   yy=y+abs(x-C)//4
   box(im,(x,yy,x+2,yy+2),'ash'); dot(im,x+1,yy+1,'shadow')
 else:
  line(im,[(L-3,y),(R+5,y+3)],'wall',2); box(im,(C-3,y,C,y+3),'lapis'); dot(im,C-2,y+1,'bone')
 return im

def charm(name):
 im=canvas(); x=C+3; y=J+8
 if name=='none': return im
 line(im,[(C-1,J+5),(x,y-1),(R+3,J+5)],'shadow')
 col='gold' if dict(TABLE['charm'])[name]<350 else 'linen'
 if name in ['scarab','paired_scarabs']:
  for a in ([x-3,x+2] if name=='paired_scarabs' else [x]):
   box(im,(a-2,y-1,a+2,y+2),'shadow'); box(im,(a-1,y,a+1,y+1),'lapis_lt'); line(im,[(a,y),(a,y+2)],col)
 elif name=='ankh':
  box(im,(x-1,y-2,x+1,y),'shadow'); dot(im,x,y-2,col); dot(im,x-1,y-1,col); dot(im,x+1,y-1,col)
  line(im,[(x,y),(x,y+3)],col); line(im,[(x-2,y+1),(x+2,y+1)],col)
 elif name=='eye_amulet':
  poly(im,[(x-3,y),(x,y-2),(x+3,y),(x,y+2)],'shadow'); line(im,[(x-2,y),(x+2,y)],'glow'); dot(im,x,y,'lapis_dk')
 elif name=='coin':
  box(im,(x-2,y-1,x+2,y+2),'shadow'); box(im,(x-1,y,x+1,y+1),col); dot(im,x,y,'linen_dk')
 elif name=='vial':
  box(im,(x-1,y-2,x+1,y+2),'shadow'); line(im,[(x,y-1),(x,y+1)],'glow'); dot(im,x,y-2,'linen_dk')
 elif name=='key':
  box(im,(x-1,y-2,x+1,y),col); dot(im,x,y-1,'shadow'); line(im,[(x,y),(x,y+3)],col); dot(im,x+1,y+2,col)
 else:
  line(im,[(x-2,y-2),(x+2,y-2)],col); line(im,[(x-2,y+2),(x+2,y+2)],col)
  line(im,[(x-1,y-1),(x+1,y+1)],'glow'); line(im,[(x+1,y-1),(x-1,y+1)],col)
 return im

def ground(name):
 base={'sand':'sand','tomb':'wall','lapis':'lapis_dk','torchlit':'wall_dk','night_sky':'lapis_dk','flood':'lapis_sh','gold':'linen_dk','void':'void','eclipse':'shadow'}[name]
 im=Image.new('RGBA',(S,S),PAL[base])
 if name=='sand':
  poly(im,[(0,23),(7,20),(24,25),(31,22),(31,31),(0,31)],'sand_dk')
 elif name=='tomb':
  for y in range(3,S,6):
   line(im,[(0,y),(31,y)],'wall_dk')
   for x in range((y//6%2)*5,S,10): line(im,[(x,y),(x,y+5)],'wall_dk')
 elif name in ['lapis','gold']:
  for x in [2,29]: line(im,[(x,2),(x,29)],'lapis' if name=='lapis' else 'sand')
  for y in [2,29]: line(im,[(2,y),(29,y)],'lapis' if name=='lapis' else 'sand')
 elif name=='torchlit':
  for x in [3,28]:
   line(im,[(x,16),(x,22)],'shadow',2); poly(im,[(x-2,15),(x,10),(x+2,15),(x,17)],'linen_dk'); dot(im,x,14,'linen')
 elif name=='flood':
  for y in range(18,S,3):
   for x in range(y%5,S,6): line(im,[(x,y),(x+3,y)],'lapis_lt')
 elif name=='night_sky':
  for x,y in [(3,4),(27,6),(5,17),(25,21),(10,2),(29,13)]: dot(im,x,y,'ash')
 elif name=='eclipse':
  ImageDraw.Draw(im).ellipse((C-10,2,C+9,21),fill=PAL['gold_sh'])
  ImageDraw.Draw(im).ellipse((C-8,3,C+8,20),fill=PAL['void'])
 return im

FUNCS=dict(wrap=wrap,head=head,eyes=eyes,jaw=jaw,bind=bind,charm=charm,ground=ground)
LAYERS={(s,n):FUNCS[s](n) for s,opts in TABLE.items() for n,w in opts}
BASE=dict(wrap='bone',head='none',eyes='lapis',jaw='grin',bind='none',charm='none',ground='tomb')
def compose(traits):
 out=canvas()
 for s in STACK: out=Image.alpha_composite(out,LAYERS[s,traits[s]])
 return out
def sheet(items,path,cols=8,scale=4):
 tile=S*scale; cellh=tile+30
 out=Image.new('RGB',(cols*(tile+12)+12,((len(items)+cols-1)//cols)*cellh+12),(24,24,30)); d=ImageDraw.Draw(out)
 for i,(im,label) in enumerate(items):
  x=12+(i%cols)*(tile+12); y=12+(i//cols)*cellh
  out.paste(im.resize((tile,tile),Image.Resampling.NEAREST),(x,y),im.resize((tile,tile),Image.Resampling.NEAREST) if im.mode=='RGBA' else None)
  d.text((x,y+tile+3),label,fill=(232,226,208))
 out.save(path)

def main():
 preview=ROOT/'preview'; preview.mkdir(exist_ok=True); pairs=preview/'pairs'; pairs.mkdir(exist_ok=True)
 manifest={'canvas':S,'stack':STACK,'slot_order':list(TABLE),'palette':PAL,'slots':{},'assets':[]}; errors=[]
 for s,opts in TABLE.items():
  assert sum(w for _,w in opts)==10000
  manifest['slots'][s]=[n for n,w in opts]
  folder=ROOT/'layers'/s; folder.mkdir(parents=True,exist_ok=True)
  for n,w in opts:
   im=LAYERS[s,n]; errors+=p.validate(im,s,n,w)
   if not im.getbbox() and n not in ['none','wrapped']: errors.append(f'Unexpected empty layer: {s}/{n}')
   if s=='ground' and im.getextrema()[3]!=(255,255): errors.append(f'Ground not opaque: {n}')
   path=folder/f'{n}.png'; im.save(path)
   manifest['assets'].append(dict(slot=s,option=n,weight=w,path=path.relative_to(ROOT).as_posix(),pixel_sha256=hashlib.sha256(im.tobytes()).hexdigest(),file_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
  sheet([(compose(BASE|{s:n}),n) for n,w in opts],preview/f'{s}.png',5)
 (ROOT/'layers'/'manifest.json').write_text(json.dumps(manifest,indent=2))
 heroes=[]
 for i in range(24):
  tr={s:opts[(i*[1,3,2,3,3,5,2][k]+k)%len(opts)][0] for k,(s,opts) in enumerate(TABLE.items())}
  im=compose(tr); heroes.append((im,f'Study {i+1:02}')); im.resize((1024,1024),Image.Resampling.NEAREST).save(preview/f'study_{i+1:02}.png')
 sheet(heroes,preview/'collection.png',6,6)
 crop=[]
 for im,label in heroes:
  im=im.resize((48,48),Image.Resampling.NEAREST); mask=Image.new('L',(48,48)); ImageDraw.Draw(mask).ellipse((0,0,47,47),fill=255); im.putalpha(mask); crop.append((im,label))
 # True 48px crops, no enlarged substitute.
 out=Image.new('RGB',(6*100,4*78),(24,24,30)); d=ImageDraw.Draw(out)
 for i,(im,label) in enumerate(crop):
  x=(i%6)*100+26; y=(i//6)*78; out.paste(im,(x,y),im); d.text((x-4,y+51),label,fill='white')
 out.save(preview/'avatar_48px.png')
 total=0
 for a,b in itertools.combinations(TABLE,2):
  items=[(compose(BASE|{a:n,b:m}),f'{n}\n{m}') for n,w in TABLE[a] for m,v in TABLE[b]]
  sheet(items,pairs/f'{a}--{b}.png',len(TABLE[b]),3); total+=len(items)
 assert len(LAYERS)==62
 # Re-render from scratch to detect accidental nondeterminism.
 for (s,n),im in LAYERS.items():
  if FUNCS[s](n).tobytes()!=im.tobytes(): errors.append(f'Nonrepeatable: {s}/{n}')
 report=dict(layers=len(LAYERS),pair_sheets=21,pair_compositions=total,errors=errors,checks=['32x32 RGBA','binary alpha','original palette','gold weight < 350','expected empty layers only','opaque backgrounds','10000 weights per slot','repeatable pixels'],scope='Artwork checks only. Pair sheets generated, not exhaustive human visual certification. No chain parity verification.')
 (ROOT/'validation.json').write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))
 if errors: raise SystemExit(1)

if __name__=='__main__': main()
