"""
DEMON KING QUEST v4
pip install pygame  →  python demon_king_quest.py

KONTROL UMUM:
  WASD / Arrow  = Gerak
  ENTER / Z     = Konfirmasi / Lanjut dialog
  X             = Kembali ke World Map (+ konfirmasi)

BERBURU MONSTER KECIL (hutan):
  WASD          = Gerak player
  J             = Tebas pedang  (area kecil, CD pendek)
  K             = Ultimate pedang  (area besar, CD panjang)
  Sentuh monster = +1 monster (setelah kena sword)

GUA MONSTER BESAR (dungeon bercabang):
  WASD          = Gerak player di dalam dungeon
  J             = Tebas pedang  (jangkauan pendek)
  K             = Ultimate pedang  (area besar, CD panjang)
  M             = Tembak monster kecil sebagai proyektil
  Monster besar bisa kena pedang langsung saat didekati!

LAWAN RAJA IBLIS (battle box):
  Phase Explore : WASD  cari monster, SPASI = mulai lawan
  Phase Battle  :
    WASD        = Gerak soul (dodge peluru musuh)
    J           = Lempar 1 monster kecil (ammo)
    K           = Ultimate: lempar 5 sekaligus (pakai 5 ammo)
"""

import pygame, sys, json, os, random, math
pygame.init()

SW, SH = 800, 600
FPS    = 60
SAVE_FILE = "save_data.json"

C = {
    "black":(0,0,0),"white":(255,255,255),"red":(220,50,50),"darkred":(140,20,20),
    "green":(60,160,60),"dkgreen":(30,90,30),"blue":(60,100,200),"dkblue":(20,40,120),
    "yellow":(240,200,40),"orange":(220,130,40),"purple":(130,50,180),"dkpurple":(60,20,100),
    "cyan":(80,200,200),"gray":(120,120,120),"dkgray":(60,60,60),"ltgray":(200,200,200),
    "sky":(100,180,240),"ground":(60,140,60),"brown":(120,80,40),"pink":(255,120,150),
    "cream":(255,240,210),"gold":(255,215,0),
    "cave":(30,22,18),"cavewall":(55,40,30),"cavefloor":(45,35,28),"cavetorch":(200,120,40),
    "fog":(10,8,6),"stone":(70,60,50),"darkstone":(40,32,25),
}

screen = pygame.display.set_mode((SW,SH))
pygame.display.set_caption("Demon King Quest")
clock  = pygame.time.Clock()

def mkf(s): return pygame.font.SysFont("couriernew",s,bold=True)
F_SM=mkf(14);F_MD=mkf(18);F_LG=mkf(26);F_XL=mkf(36);F_TTL=mkf(52)

def pxr(s,c,r,bw=0,bc=(0,0,0)):
    pygame.draw.rect(s,c,r)
    if bw: pygame.draw.rect(s,bc,r,bw)

def pxt(s,txt,f,c,x,y,center=False,shadow=True):
    if shadow:
        sh=f.render(txt,False,(0,0,0));r=sh.get_rect()
        if center: r.center=(x+2,y+2)
        else: r.topleft=(x+2,y+2)
        s.blit(sh,r)
    t=f.render(txt,False,c);r=t.get_rect()
    if center: r.center=(x,y)
    else: r.topleft=(x,y)
    s.blit(t,r);return r

def hpbar(s,x,y,w,h,cur,mx,col=(80,200,80)):
    pxr(s,C["dkgray"],(x,y,w,h))
    fw=int(w*max(0,cur)/max(1,mx))
    if fw>0: pxr(s,col,(x,y,fw,h))
    pxr(s,C["black"],(x,y,w,h),2)

# ── sprites ───────────────────────────────────────────────────────────────────
def draw_player(s,x,y,frame=0,sword=False,ult=False):
    bx,by=int(x),int(y)
    pxr(s,C["blue"],(bx-8,by-20,16,18))
    pxr(s,C["cream"],(bx-7,by-34,14,14))
    pxr(s,C["black"],(bx-4,by-30,3,3));pxr(s,C["black"],(bx+2,by-30,3,3))
    pxr(s,C["dkblue"],(bx-8,by-2,7,14));pxr(s,C["dkblue"],(bx+1,by-2,7,14))
    pxr(s,C["blue"],(bx-14,by-18,6,12));pxr(s,C["blue"],(bx+8,by-18,6,12))
    if ult:
        col=C["gold"]
        pygame.draw.line(s,col,(bx+8,by-18),(bx+50,by-60),4)
        pygame.draw.line(s,(255,255,180),(bx+8,by-18),(bx+55,by-55),2)
        pygame.draw.circle(s,C["yellow"],(bx+14,by-14),14,0)
        for ang in range(0,360,45):
            r=math.radians(ang+frame*10)
            pygame.draw.line(s,C["yellow"],(bx+14,by-14),
                (int(bx+14+math.cos(r)*22),int(by-14+math.sin(r)*22)),2)
    elif sword:
        pygame.draw.line(s,C["ltgray"],(bx+8,by-18),(bx+36,by-46),3)
        pygame.draw.line(s,C["yellow"],(bx+10,by-16),(bx+16,by-22),3)
    else:
        pygame.draw.line(s,C["gray"],(bx+6,by-34),(bx+12,by-2),2)

def draw_friend_a(s,x,y,frame=0):
    bx,by=int(x),int(y)
    pxr(s,C["orange"],(bx-8,by-20,16,18))
    pxr(s,C["yellow"],(bx-7,by-34,14,14))
    pxr(s,C["black"],(bx-4,by-30,3,3));pxr(s,C["black"],(bx+2,by-30,3,3))
    for i in range(-6,8,4):
        pygame.draw.polygon(s,C["orange"],[(bx+i,by-34),(bx+i+2,by-44),(bx+i+4,by-34)])
    pxr(s,C["brown"],(bx-8,by-2,7,14));pxr(s,C["brown"],(bx+1,by-2,7,14))
    pxr(s,C["orange"],(bx-14,by-18,6,12));pxr(s,C["orange"],(bx+8,by-18,6,12))
    pygame.draw.line(s,C["brown"],(bx-14,by-18),(bx-20,by-50),2)
    pygame.draw.circle(s,C["orange"],(bx-20,by-50),4)

def draw_friend_b(s,x,y,frame=0):
    bx,by=int(x),int(y)
    pxr(s,C["purple"],(bx-8,by-20,16,18))
    pxr(s,C["pink"],(bx-7,by-34,14,14))
    pxr(s,C["black"],(bx-4,by-30,3,3));pxr(s,C["black"],(bx+2,by-30,3,3))
    pygame.draw.polygon(s,C["purple"],[(bx-7,by-34),(bx-12,by-46),(bx-1,by-34)])
    pygame.draw.polygon(s,C["purple"],[(bx+7,by-34),(bx+12,by-46),(bx+1,by-34)])
    pxr(s,C["dkpurple"],(bx-8,by-2,7,14));pxr(s,C["dkpurple"],(bx+1,by-2,7,14))
    pxr(s,C["purple"],(bx-14,by-18,6,12));pxr(s,C["purple"],(bx+8,by-18,6,12))
    pygame.draw.line(s,C["ltgray"],(bx+8,by-18),(bx+18,by-10),2)
    pygame.draw.line(s,C["ltgray"],(bx+8,by-18),(bx+20,by-18),2)

def draw_small_monster(s,x,y,variant=0,scale=1.0):
    bx,by=int(x),int(y)
    r=int(10*scale)
    cols=[(180,60,60),(60,60,180),(60,180,60),(180,120,60),(120,60,180)]
    c=cols[variant%len(cols)]
    pygame.draw.ellipse(s,c,(bx-r,by-int(14*scale),r*2,int(16*scale)))
    pygame.draw.ellipse(s,(0,0,0),(bx-r,by-int(14*scale),r*2,int(16*scale)),1)
    ew=max(2,int(4*scale));eh=max(2,int(4*scale))
    pxr(s,C["white"],(bx-int(5*scale),by-int(12*scale),ew,eh))
    pxr(s,C["white"],(bx+int(2*scale),by-int(12*scale),ew,eh))
    pxr(s,C["black"],(bx-int(4*scale),by-int(11*scale),max(1,int(2*scale)),max(1,int(2*scale))))
    pxr(s,C["black"],(bx+int(3*scale),by-int(11*scale),max(1,int(2*scale)),max(1,int(2*scale))))
    pygame.draw.polygon(s,C["darkred"],[(bx-int(6*scale),by-int(14*scale)),
        (bx-int(8*scale),by-int(20*scale)),(bx-int(3*scale),by-int(14*scale))])
    pygame.draw.polygon(s,C["darkred"],[(bx+int(6*scale),by-int(14*scale)),
        (bx+int(8*scale),by-int(20*scale)),(bx+int(3*scale),by-int(14*scale))])

def draw_big_monster(s,x,y,color=(140,40,40),scale=1.0):
    bx,by=int(x),int(y)
    sc=scale
    pxr(s,color,(bx-int(20*sc),by-int(40*sc),int(40*sc),int(40*sc)),2,C["black"])
    pxr(s,color,(bx-int(18*sc),by-int(66*sc),int(36*sc),int(28*sc)),2,C["black"])
    pygame.draw.polygon(s,C["darkred"],[(bx-int(18*sc),by-int(66*sc)),
        (bx-int(28*sc),by-int(84*sc)),(bx-int(6*sc),by-int(66*sc))])
    pygame.draw.polygon(s,C["darkred"],[(bx+int(18*sc),by-int(66*sc)),
        (bx+int(28*sc),by-int(84*sc)),(bx+int(6*sc),by-int(66*sc))])
    pxr(s,C["yellow"],(bx-int(12*sc),by-int(60*sc),int(8*sc),int(8*sc)))
    pxr(s,C["yellow"],(bx+int(4*sc),by-int(60*sc),int(8*sc),int(8*sc)))
    pxr(s,C["black"],(bx-int(10*sc),by-int(58*sc),int(4*sc),int(4*sc)))
    pxr(s,C["black"],(bx+int(6*sc),by-int(58*sc),int(4*sc),int(4*sc)))
    pxr(s,C["black"],(bx-int(8*sc),by-int(48*sc),int(16*sc),int(5*sc)))
    pxr(s,color,(bx-int(40*sc),by-int(38*sc),int(20*sc),int(14*sc)),2,C["black"])
    pxr(s,color,(bx+int(20*sc),by-int(38*sc),int(20*sc),int(14*sc)),2,C["black"])
    pxr(s,C["dkgray"],(bx-int(18*sc),by,int(16*sc),int(20*sc)),2,C["black"])
    pxr(s,C["dkgray"],(bx+int(2*sc),by,int(16*sc),int(20*sc)),2,C["black"])

def draw_demon_king(s,x,y,frame=0):
    bx,by=int(x),int(y)
    pulse=abs(math.sin(frame*0.05))*10
    pygame.draw.circle(s,(80,0,80),(bx,by-40),int(60+pulse))
    pygame.draw.polygon(s,C["dkpurple"],[(bx-30,by-50),(bx+30,by-50),(bx+40,by+10),(bx-40,by+10)])
    pxr(s,C["darkred"],(bx-22,by-50,44,50),2,C["black"])
    pxr(s,(160,60,60),(bx-20,by-84,40,36),2,C["black"])
    for i in[-16,-6,4,14]:
        pygame.draw.polygon(s,C["yellow"],[(bx+i,by-84),(bx+i+3,by-98),(bx+i+7,by-84)])
    pxr(s,C["red"],(bx-14,by-76,10,10));pxr(s,C["red"],(bx+4,by-76,10,10))
    pxr(s,(255,200,0),(bx-12,by-74,6,6));pxr(s,(255,200,0),(bx+6,by-74,6,6))
    pxr(s,C["black"],(bx-10,by-60,20,8))
    pxr(s,C["white"],(bx-8,by-60,4,6));pxr(s,C["white"],(bx+4,by-60,4,6))
    pxr(s,C["darkred"],(bx-44,by-48,22,16),2,C["black"])
    pxr(s,C["darkred"],(bx+22,by-48,22,16),2,C["black"])
    pygame.draw.line(s,C["ltgray"],(bx+44,by-48),(bx+70,by-80),4)
    pxr(s,C["dkpurple"],(bx-20,by,18,24),2,C["black"])
    pxr(s,C["dkpurple"],(bx+2,by,18,24),2,C["black"])

# ── particles ──────────────────────────────────────────────────────────────
class Particles:
    def __init__(self): self.p=[]
    def emit(self,x,y,n=10,color=(255,200,0),spd=3,life=40,sz=4,grav=0.1,spread=360):
        for _ in range(n):
            a=math.radians(random.uniform(0,spread)); sp=spd*random.uniform(0.5,1.5)
            col=random.choice(color) if isinstance(color,list) else color
            self.p.append({"x":float(x),"y":float(y),"vx":math.cos(a)*sp,"vy":math.sin(a)*sp,
                           "l":life,"ml":life,"sz":sz,"col":col,"g":grav})
    def update(self):
        for p in self.p[:]:
            p["x"]+=p["vx"];p["y"]+=p["vy"];p["vy"]+=p["g"];p["l"]-=1
            if p["l"]<=0: self.p.remove(p)
    def draw(self,s,ox=0,oy=0):
        for p in self.p:
            a=p["l"]/p["ml"]; sz=max(1,int(p["sz"]*a))
            pygame.draw.circle(s,tuple(min(255,int(c*a)) for c in p["col"]),
                (int(p["x"]+ox),int(p["y"]+oy)),sz)

# ── transition ──────────────────────────────────────────────────────────────
class Transition:
    def __init__(self):
        self._s=pygame.Surface((SW,SH));self._s.fill((0,0,0))
        self.alpha=0;self.state="idle";self.spd=8;self._cb=None
    def fade_to(self,cb,spd=8):
        self.state="out";self.alpha=0;self.spd=spd;self._cb=cb
    def update(self):
        if self.state=="out":
            self.alpha=min(255,self.alpha+self.spd)
            if self.alpha>=255 and self._cb: self._cb();self._cb=None;self.state="in"
        elif self.state=="in":
            self.alpha=max(0,self.alpha-self.spd)
            if self.alpha<=0: self.state="idle"
    def draw(self,s):
        if self.state=="idle" and self.alpha==0: return
        self._s.set_alpha(self.alpha);s.blit(self._s,(0,0))
    @property
    def busy(self): return self.state!="idle"

# ── dialog ──────────────────────────────────────────────────────────────────
class Dialog:
    def __init__(self):
        self.lines=[];self.speaker="";self.visible=False
        self.ci=0;self.timer=0;self.spd=2
        self.choices=[];self.csel=0;self.await_c=False;self.done=False
    def show(self,sp,txt,choices=None):
        self.speaker=sp;self.lines=self._wrap(txt,60)
        self.visible=True;self.ci=0;self.timer=0;self.done=False
        self.choices=choices or[];self.csel=0;self.await_c=bool(choices)
    def _wrap(self,t,w):
        words=t.split();lines=[];cur=""
        for wd in words:
            if len(cur)+len(wd)+1<=w: cur+=("" if not cur else " ")+wd
            else: lines.append(cur);cur=wd
        if cur: lines.append(cur)
        return lines
    def update(self):
        if not self.visible or self.done: return
        self.timer+=1
        if self.timer>=self.spd:
            self.timer=0;self.ci+=1
            tot=sum(len(l) for l in self.lines)+len(self.lines)
            if self.ci>=tot:
                self.ci=tot
                if not self.await_c: self.done=True
    def key(self,k):
        if not self.visible: return None
        tot=sum(len(l) for l in self.lines)+len(self.lines)
        if not self.done and self.ci<tot:
            self.ci=tot
            if not self.await_c: self.done=True
            return None
        if self.await_c:
            if k==pygame.K_UP:   self.csel=(self.csel-1)%len(self.choices)
            if k==pygame.K_DOWN: self.csel=(self.csel+1)%len(self.choices)
            if k in(pygame.K_RETURN,pygame.K_z):
                sel=self.csel;self.visible=False;return sel
        else:
            if k in(pygame.K_RETURN,pygame.K_z,pygame.K_SPACE):
                self.visible=False;return -1
        return None
    def draw(self,s):
        if not self.visible: return
        bx,by,bw,bh=30,SH-180,SW-60,160
        pxr(s,C["black"],(bx-2,by-2,bw+4,bh+4))
        pxr(s,C["dkgray"],(bx,by,bw,bh))
        pxr(s,C["dkpurple"],(bx,by,bw,bh),3)
        if self.speaker:
            tw=F_MD.size(self.speaker)[0]+16
            pxr(s,C["dkgray"],(bx+8,by-22,tw,24))
            pxr(s,C["white"],(bx+8,by-22,tw,24),2)
            pxt(s,self.speaker,F_MD,C["yellow"],bx+16,by-20)
        rendered=0
        for i,line in enumerate(self.lines):
            ch=min(max(0,self.ci-rendered),len(line))
            pxt(s,line[:ch],F_SM,C["white"],bx+16,by+14+i*22,shadow=False)
            rendered+=len(line)+1
        if self.await_c and self.ci>=sum(len(l) for l in self.lines)+len(self.lines):
            for i,ch in enumerate(self.choices):
                cy=by+bh-20-(len(self.choices)-i)*26
                col=C["yellow"] if i==self.csel else C["ltgray"]
                pxt(s,("> " if i==self.csel else "  ")+ch,F_SM,col,bx+30,cy,shadow=False)
        elif self.done and not self.await_c:
            if(pygame.time.get_ticks()//400)%2==0:
                pxt(s,"▼",F_SM,C["yellow"],bx+bw-30,by+bh-28,shadow=False)

# ── back confirm ────────────────────────────────────────────────────────────
class BackConfirm:
    def __init__(self): self.visible=False;self.sel=1;self._cb=None
    def show(self,cb): self.visible=True;self.sel=1;self._cb=cb
    def key(self,k):
        if not self.visible: return False
        if k==pygame.K_LEFT: self.sel=0
        if k==pygame.K_RIGHT: self.sel=1
        if k in(pygame.K_RETURN,pygame.K_z):
            self.visible=False
            if self.sel==0 and self._cb: self._cb()
            return True
        if k==pygame.K_ESCAPE: self.visible=False;return True
        return True
    def draw(self,s):
        if not self.visible: return
        dim=pygame.Surface((SW,SH),pygame.SRCALPHA);dim.fill((0,0,0,160));s.blit(dim,(0,0))
        bx,by,bw,bh=SW//2-220,SH//2-80,440,160
        pxr(s,C["black"],(bx-3,by-3,bw+6,bh+6))
        pxr(s,C["dkgray"],(bx,by,bw,bh));pxr(s,C["orange"],(bx,by,bw,bh),3)
        pxt(s,"⚠ Kembali ke World Map?",F_MD,C["yellow"],SW//2,by+18,center=True)
        pxt(s,"Progress di lokasi ini TIDAK tersimpan!",F_SM,C["orange"],SW//2,by+44,center=True)
        for i,(lbl,col) in enumerate(zip(["YA, Kembali","TIDAK, Lanjut"],
                [C["red"] if self.sel==0 else C["gray"],C["green"] if self.sel==1 else C["gray"]])):
            bxb=bx+30+i*210;byb=by+90
            pxr(s,col,(bxb,byb,180,36),3,C["black"])
            pxt(s,("> " if i==self.sel else "  ")+lbl,F_SM,C["white"],bxb+90,byb+18,center=True)
        pxt(s,"← → pilih  ENTER konfirmasi",F_SM,C["ltgray"],SW//2,by+bh-18,center=True)

# ── save/load ────────────────────────────────────────────────────────────────
def save_game(st):
    with open(SAVE_FILE,"w") as f: json.dump(st,f)
def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE) as f: return json.load(f)
    return None
def default_state():
    return{"scene":"intro","small_monsters":0,"big_monsters":0,
           "has_friend_a":False,"has_friend_b":False,"defeated_king":False,"flags":{}}

# ════════════════════════════════════════════════════════════════════════════
#  SMALL MONSTER HUNT  – sword-based, touch = capture after sword contact
# ════════════════════════════════════════════════════════════════════════════
class SmallHunt:
    SWORD_R  = 55
    ULT_R    = 110
    SWORD_CD = 18
    ULT_CD   = 120
    # HP player di hutan
    PHP_MAX  = 60

    def __init__(self,state):
        self.state=state
        self.px=float(SW//2);self.py=float(SH//2)
        self.frame=0;self.phase="hunt";self.result=None
        self.monsters=self._spawn(30)
        self.sword_cd=0;self.ult_cd=0
        self.sword_anim=0;self.ult_anim=0
        self.shake=0
        self.ax=self.px-50;self.ay=self.py
        self.bx=self.px+50;self.by_=self.py
        self.particles=Particles()
        # player HP & invincibility
        self.php=self.PHP_MAX
        self.inv=0          # invincibility frames setelah kena
        # semua peluru monster kecil
        self.enemy_bullets=[]

    def _spawn(self,n):
        ms=[]
        for _ in range(n):
            while True:
                x=float(random.randint(40,SW-40));y=float(random.randint(40,SH-80))
                if math.hypot(x-SW//2,y-SH//2)>80: break
            ms.append({
                "x":x,"y":y,
                "vx":random.uniform(-1,1),"vy":random.uniform(-1,1),
                "variant":random.randint(0,4),"alive":True,"stunned":0,
                "atk_cd":random.randint(60,140),   # cooldown tembak
            })
        return ms

    def handle_key(self,k):
        if self.phase!="hunt": return
        if k==pygame.K_j and self.sword_cd<=0:
            self._slash(self.SWORD_R,dmg=1);self.sword_cd=self.SWORD_CD;self.sword_anim=12
        if k==pygame.K_k and self.ult_cd<=0:
            self._slash(self.ULT_R,dmg=3);self.ult_cd=self.ULT_CD;self.ult_anim=24

    def _slash(self,radius,dmg):
        for m in self.monsters:
            if not m["alive"]: continue
            if math.hypot(m["x"]-self.px,m["y"]-self.py)<=radius:
                m["stunned"]=40
                self.particles.emit(m["x"],m["y"],n=8,
                    color=[(255,200,0),(255,255,100)],spd=3,life=20,sz=4,grav=0)

    def _monster_shoot(self,m):
        """Monster kecil tembak peluru kecil ke arah player."""
        dx=self.px-m["x"]; dy=self.py-m["y"]
        d=max(1,math.hypot(dx,dy))
        spd=3.2+random.uniform(-0.4,0.4)
        # sedikit spread
        spread=random.uniform(-0.18,0.18)
        cols=[(220,80,80),(80,80,220),(80,200,80),(200,140,60),(160,80,220)]
        col=cols[m["variant"]%len(cols)]
        self.enemy_bullets.append({
            "x":float(m["x"]),"y":float(m["y"]),
            "vx":(dx/d+spread)*spd,"vy":(dy/d+spread)*spd,
            "r":5,"col":col,"life":70,
        })

    def update(self):
        if self.phase!="hunt": return
        self.frame+=1
        if self.shake>0: self.shake-=1
        if self.inv>0:   self.inv-=1
        if self.sword_cd>0: self.sword_cd-=1
        if self.ult_cd>0:   self.ult_cd-=1
        if self.sword_anim>0: self.sword_anim-=1
        if self.ult_anim>0:   self.ult_anim-=1
        self.particles.update()

        keys=pygame.key.get_pressed()
        spd=3.5
        if keys[pygame.K_LEFT]:  self.px=max(16,self.px-spd)
        if keys[pygame.K_RIGHT]: self.px=min(SW-16,self.px+spd)
        if keys[pygame.K_UP]:    self.py=max(16,self.py-spd)
        if keys[pygame.K_DOWN]:  self.py=min(SH-80,self.py+spd)

        ha=self.state.get("has_friend_a");hb=self.state.get("has_friend_b")
        if ha:
            self.ax+=(self.px-55-self.ax)*0.12
            self.ay+=(self.py-self.ay)*0.12
        if hb:
            self.bx+=(self.px+55-self.bx)*0.12
            self.by_+=(self.py-self.by_)*0.12

        for m in self.monsters:
            if not m["alive"]: continue
            if m["stunned"]>0:
                m["stunned"]-=1
                if math.hypot(m["x"]-self.px,m["y"]-self.py)<24:
                    m["alive"]=False
                    self.state["small_monsters"]=min(50,self.state["small_monsters"]+1)
                    self.particles.emit(m["x"],m["y"],n=12,
                        color=[(100,220,255),(200,255,200)],spd=4,life=30,sz=5,grav=-0.05)
                    self.shake=4
                    if self.state["small_monsters"]>=50:
                        self.phase="full";self.result="full"
                continue
            # gerak wandering
            m["x"]+=m["vx"];m["y"]+=m["vy"]
            if m["x"]<20 or m["x"]>SW-20: m["vx"]*=-1
            if m["y"]<20 or m["y"]>SH-80: m["vy"]*=-1
            # tembak ke player jika cukup dekat
            dist=math.hypot(m["x"]-self.px,m["y"]-self.py)
            m["atk_cd"]-=1
            if m["atk_cd"]<=0 and dist<260:
                m["atk_cd"]=random.randint(70,130)
                self._monster_shoot(m)

        # update peluru musuh
        for b in self.enemy_bullets[:]:
            b["x"]+=b["vx"]; b["y"]+=b["vy"]; b["life"]-=1
            if b["life"]<=0 or b["x"]<0 or b["x"]>SW or b["y"]<0 or b["y"]>SH:
                self.enemy_bullets.remove(b); continue
            if self.inv<=0 and math.hypot(b["x"]-self.px,b["y"]-self.py)<b["r"]+8:
                self.php-=6; self.inv=30; self.shake=5
                self.particles.emit(self.px,self.py,n=6,
                    color=[(255,80,80),(255,160,0)],spd=2,life=14,sz=3,grav=0)
                self.enemy_bullets.remove(b)
                if self.php<=0:
                    self.php=0; self.phase="lost"; self.result="lost"
                continue

        alive=[m for m in self.monsters if m["alive"]]
        if not alive and self.phase=="hunt":
            self.phase="done";self.result="cleared"

    def draw(self,s):
        ox=random.randint(-3,3) if self.shake else 0
        s.fill(C["dkgreen"])
        for gx in range(0,SW,32): pygame.draw.line(s,(40,110,40),(gx,0),(gx,SH))
        for gy in range(0,SH,32): pygame.draw.line(s,(40,110,40),(0,gy),(SW,gy))

        if self.sword_anim>0:
            pygame.draw.circle(s,(255,220,0),(int(self.px+ox),int(self.py)),self.SWORD_R,2)
        if self.ult_anim>0:
            surf2=pygame.Surface((SW,SH),pygame.SRCALPHA)
            pygame.draw.circle(surf2,(255,200,0,60),(int(self.px+ox),int(self.py)),self.ULT_R)
            s.blit(surf2,(0,0))
            pygame.draw.circle(s,(255,220,80),(int(self.px+ox),int(self.py)),self.ULT_R,3)

        # peluru musuh
        for b in self.enemy_bullets:
            pygame.draw.circle(s,b["col"],(int(b["x"]+ox),int(b["y"])),b["r"])
            pygame.draw.circle(s,C["white"],(int(b["x"]+ox),int(b["y"])),b["r"],1)

        for m in self.monsters:
            if m["alive"]:
                draw_small_monster(s,m["x"]+ox,m["y"],m["variant"])
                if m["stunned"]>0:
                    pygame.draw.circle(s,C["yellow"],(int(m["x"]+ox),int(m["y"]-18)),6,2)

        self.particles.draw(s)

        ha=self.state.get("has_friend_a");hb=self.state.get("has_friend_b")
        if ha: draw_friend_a(s,self.ax+ox,self.ay,self.frame)
        if hb: draw_friend_b(s,self.bx+ox,self.by_,self.frame)

        # player berkedip saat invincible
        if self.inv<=0 or (self.frame//4)%2==0:
            draw_player(s,self.px+ox,self.py,frame=self.frame,
                        sword=self.sword_anim>0,ult=self.ult_anim>0)

        sm=self.state["small_monsters"]
        # HP bar player
        hpbar(s,10,10,140,14,self.php,self.PHP_MAX,(80,200,80))
        pxt(s,f"HP: {self.php}/{self.PHP_MAX}",F_SM,C["white"],10,28)
        hpbar(s,10,46,180,12,sm,50,(80,180,220))
        pxt(s,f"Tangkap: {sm}/50",F_SM,C["white"],10,62)
        pxt(s,f"[J]=Tebas(CD:{self.sword_cd}) [K]=Ult(CD:{self.ult_cd})",F_SM,C["yellow"],10,78)
        pxt(s,"Dodge peluru! Tebas lalu sentuh monster kuning!",F_SM,C["cyan"],10,94)
        pxt(s,"[X]=Kembali",F_SM,C["orange"],SW-150,10)
        alive_cnt=sum(1 for m in self.monsters if m["alive"])
        pxt(s,f"Sisa: {alive_cnt}",F_SM,C["white"],SW-150,30)

        if self.phase in("done","full","lost"):
            pxr(s,C["black"],(SW//2-210,SH//2-30,420,90))
            if self.result=="full":
                pxt(s,"MONSTER SUDAH CUKUP! (50/50)",F_LG,C["yellow"],SW//2,SH//2,center=True)
                pxt(s,"Kembali ke Map Dunia...",F_MD,C["white"],SW//2,SH//2+44,center=True)
            elif self.result=="lost":
                pxt(s,"KAU PINGSAN! Kembali ke Map...",F_LG,C["red"],SW//2,SH//2,center=True)
                pxt(s,"ENTER lanjut",F_MD,C["white"],SW//2,SH//2+44,center=True)
            else:
                pxt(s,f"Area Bersih! +{sm} monster",F_LG,C["cyan"],SW//2,SH//2,center=True)
                pxt(s,"ENTER lanjut",F_MD,C["white"],SW//2,SH//2+44,center=True)


# ════════════════════════════════════════════════════════════════════════════
#  DUNGEON CAVE  – top-down dungeon dengan fog of war & beberapa ruangan
# ════════════════════════════════════════════════════════════════════════════

TILE_SIZE = 48   # pixel per tile di dunia dungeon
TILE_FLOOR  = 0
TILE_WALL   = 1
TILE_DOOR   = 2
TILE_ENTRY  = 3
TILE_EXIT   = 4

class Room:
    def __init__(self, tx, ty, tw, th, room_id):
        self.tx=tx; self.ty=ty; self.tw=tw; self.th=th
        self.id=room_id
        self.cleared=False
        self.monsters=[]
        # tile coords of center
        self.cx=tx+tw//2; self.cy=ty+th//2
    def rect(self): return pygame.Rect(self.tx,self.ty,self.tw,self.th)
    def world_center(self):
        return (self.cx*TILE_SIZE+TILE_SIZE//2, self.cy*TILE_SIZE+TILE_SIZE//2)

class DungeonCave:
    MAP_W = 52   # tiles wide
    MAP_H = 44   # tiles tall
    FOG_R = 6    # fog of war radius in tiles
    SWORD_R  = 60
    ULT_R    = 120
    SWORD_CD = 20
    ULT_CD   = 140
    SHOOT_CD = 22

    def __init__(self, state):
        self.state = state
        self.frame = 0
        self.shake = 0
        self.result = None
        self.particles = Particles()
        self.shoot_cd = 0
        self.sword_cd = 0
        self.ult_cd   = 0
        self.sword_anim = 0
        self.ult_anim   = 0
        self.projectiles = []   # player-fired monster projectiles
        self.big_killed  = 0   # monsters killed this session

        # generate map
        self.tiles, self.rooms, self.corridors = self._gen_map()
        self.explored = [[False]*self.MAP_H for _ in range(self.MAP_W)]

        # spawn player at entry room
        entry = self.rooms[0]
        wx,wy = entry.world_center()
        self.px = float(wx); self.py = float(wy)

        # populate rooms with monsters (skip entry room)
        self._populate_monsters()

        # camera
        self.cam_x = 0.0; self.cam_y = 0.0

        # torch flicker
        self.torch_flicker = 0

        # minimap surface
        self.minimap_surf = pygame.Surface((self.MAP_W*4, self.MAP_H*4))

    # ── map generation ──────────────────────────────────────────────────
    def _gen_map(self):
        W,H = self.MAP_W, self.MAP_H
        tiles = [[TILE_WALL]*H for _ in range(W)]

        # define castle-like room layout
        room_defs = [
            # entry hall
            (2, H//2-3, 8, 6, "entry"),
            # left branch
            (12, H//2-4, 7, 8, "left1"),
            (21, H//2-6, 8, 7, "left2"),
            # right branch top
            (12, H//2-14, 7, 7, "top1"),
            (21, H//2-16, 9, 8, "top2"),
            # right branch bottom
            (12, H//2+6, 7, 7, "bot1"),
            (21, H//2+8, 9, 8, "bot2"),
            # center junction
            (31, H//2-5, 9, 10, "center"),
            # far rooms
            (42, H//2-8, 7, 7, "far1"),
            (42, H//2+1, 7, 7, "far2"),
        ]

        rooms = []
        for i,(tx,ty,tw,th,_) in enumerate(room_defs):
            # clamp to map
            tx=max(1,min(W-tw-1,tx)); ty=max(1,min(H-th-1,ty))
            r = Room(tx,ty,tw,th,i)
            rooms.append(r)
            for x in range(tx,tx+tw):
                for y in range(ty,ty+th):
                    tiles[x][y] = TILE_FLOOR

        # mark entry & build corridors
        ex,ey = rooms[0].cx, rooms[0].cy
        tiles[ex][ey] = TILE_ENTRY

        # connect rooms with corridors
        connections = [(0,1),(1,2),(0,3),(3,4),(0,5),(5,6),(1,7),(7,8),(7,9)]
        corridors = []
        for a_idx,b_idx in connections:
            if a_idx>=len(rooms) or b_idx>=len(rooms): continue
            ra=rooms[a_idx]; rb=rooms[b_idx]
            ax,ay=ra.cx,ra.cy; bx,by=rb.cx,rb.cy
            # L-shaped corridor
            for x in range(min(ax,bx),max(ax,bx)+1):
                y=ay
                tiles[max(1,min(W-2,x))][max(1,min(H-2,y))] = TILE_FLOOR
                tiles[max(1,min(W-2,x))][max(1,min(H-2,y+1))] = TILE_FLOOR
            for y in range(min(ay,by),max(ay,by)+1):
                x=bx
                tiles[max(1,min(W-2,x))][max(1,min(H-2,y))] = TILE_FLOOR
                tiles[max(1,min(W-2,x))][max(1,min(H-2,y+1))] = TILE_FLOOR
            corridors.append((ax,ay,bx,by))

        # add some pillars / detail in larger rooms
        for r in rooms[1:]:
            if r.tw>=8 and r.th>=7:
                for px_,py_ in [(r.tx+2,r.ty+2),(r.tx+r.tw-3,r.ty+2),
                                 (r.tx+2,r.ty+r.th-3),(r.tx+r.tw-3,r.ty+r.th-3)]:
                    if 1<px_<W-1 and 1<py_<H-1:
                        tiles[px_][py_] = TILE_WALL

        return tiles, rooms, corridors

    def _populate_monsters(self):
        # boss monster colors
        colors=[(160,40,40),(40,40,160),(40,140,40),(140,80,20),(100,40,160),(160,40,100)]
        for i,room in enumerate(self.rooms[1:], 1):
            count = 1 if i<=3 else (2 if i<=6 else 3)
            for j in range(count):
                wx,wy = room.world_center()
                offset_x = random.randint(-40,40)
                offset_y = random.randint(-40,40)
                col = colors[(i+j)%len(colors)]
                variant = (i+j)%5
                scale = random.uniform(0.9,1.4)
                hp = int(60*scale)
                room.monsters.append({
                    "x":float(wx+offset_x), "y":float(wy+offset_y),
                    "vx":random.uniform(-0.6,0.6), "vy":random.uniform(-0.6,0.6),
                    "color":col, "variant":variant, "scale":scale,
                    "hp":hp, "maxhp":hp, "alive":True,
                    "stun":0, "atk_cd":0,
                    "bullets":[], "aggro":False,
                })

    # ── tile helpers ────────────────────────────────────────────────────
    def _is_walkable(self,tx,ty):
        if tx<0 or ty<0 or tx>=self.MAP_W or ty>=self.MAP_H: return False
        return self.tiles[tx][ty] != TILE_WALL

    def _world_walkable(self,wx,wy):
        """check 4 corners of a small bbox around player"""
        r=10
        for dx,dy in [(-r,-r),(r,-r),(-r,r),(r,r)]:
            tx=int((wx+dx)//TILE_SIZE); ty=int((wy+dy)//TILE_SIZE)
            if not self._is_walkable(tx,ty): return False
        return True

    # ── update ──────────────────────────────────────────────────────────
    def handle_key(self,k):
        if self.result: return
        if k==pygame.K_m and self.shoot_cd<=0:
            self._shoot_projectile()
        if k==pygame.K_j and self.sword_cd<=0:
            self._sword_attack(self.SWORD_R, dmg=20)
            self.sword_cd=self.SWORD_CD; self.sword_anim=14
        if k==pygame.K_k and self.ult_cd<=0:
            self._sword_attack(self.ULT_R, dmg=45)
            self.ult_cd=self.ULT_CD; self.ult_anim=28

    def _shoot_projectile(self):
        ammo=self.state["small_monsters"]
        if ammo<=0: return
        self.state["small_monsters"]-=1; self.shoot_cd=self.SHOOT_CD
        # find nearest living monster in range
        nearest=None; nd=99999
        for room in self.rooms:
            for m in room.monsters:
                if m["alive"]:
                    d=math.hypot(m["x"]-self.px, m["y"]-self.py)
                    if d<nd: nd=d; nearest=m
        if nearest:
            dx=nearest["x"]-self.px; dy=nearest["y"]-self.py
            d=max(1,math.hypot(dx,dy))
            spd=9
            self.projectiles.append({"x":self.px,"y":self.py,
                "vx":dx/d*spd,"vy":dy/d*spd,
                "variant":random.randint(0,4),"dmg":22,"r":8,"life":80})
        else:
            # no target, shoot upward
            self.projectiles.append({"x":self.px,"y":self.py,
                "vx":0,"vy":-9,
                "variant":random.randint(0,4),"dmg":22,"r":8,"life":80})
        self.particles.emit(self.px,self.py,n=5,
            color=[(255,180,0),(255,100,50)],spd=3,life=12,sz=4,grav=0)

    def _sword_attack(self, radius, dmg):
        hit_any=False
        for room in self.rooms:
            for m in room.monsters:
                if not m["alive"]: continue
                d=math.hypot(m["x"]-self.px, m["y"]-self.py)
                if d<=radius:
                    m["hp"]-=dmg; m["stun"]=20
                    self.particles.emit(m["x"],m["y"],n=10,
                        color=[(255,220,0),(255,100,0)],spd=4,life=22,sz=5,grav=0)
                    hit_any=True
                    if m["hp"]<=0:
                        m["alive"]=False
                        self.big_killed+=1
                        self.state["big_monsters"]=min(5,self.state["big_monsters"]+1)
                        self.particles.emit(m["x"],m["y"],n=20,
                            color=[(255,200,0),(200,50,50),(100,200,255)],
                            spd=6,life=40,sz=7,grav=-0.05)
        if hit_any: self.shake=5

    def update(self):
        self.frame+=1
        if self.shake>0: self.shake-=1
        if self.sword_cd>0: self.sword_cd-=1
        if self.ult_cd>0: self.ult_cd-=1
        if self.shoot_cd>0: self.shoot_cd-=1
        if self.sword_anim>0: self.sword_anim-=1
        if self.ult_anim>0: self.ult_anim-=1
        self.particles.update()
        self.torch_flicker = random.randint(-2,2)

        if self.result: return

        # player movement
        keys=pygame.key.get_pressed(); spd=3.2
        dx=0.0; dy=0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx-=spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx+=spd
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy-=spd
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy+=spd
        if dx!=0 and dy!=0: dx*=0.707; dy*=0.707

        nx=self.px+dx; ny=self.py+dy
        if self._world_walkable(nx, self.py): self.px=nx
        if self._world_walkable(self.px, ny): self.py=ny

        # update explored tiles
        ptx=int(self.px//TILE_SIZE); pty=int(self.py//TILE_SIZE)
        for fx in range(ptx-self.FOG_R, ptx+self.FOG_R+1):
            for fy in range(pty-self.FOG_R, pty+self.FOG_R+1):
                if 0<=fx<self.MAP_W and 0<=fy<self.MAP_H:
                    if math.hypot(fx-ptx,fy-pty)<=self.FOG_R:
                        self.explored[fx][fy]=True

        # camera follows player
        self.cam_x = self.px - SW//2
        self.cam_y = self.py - SH//2

        # update monsters
        for room in self.rooms:
            all_dead=all(not m["alive"] for m in room.monsters)
            if room.monsters: room.cleared = all_dead
            for m in room.monsters:
                if not m["alive"]: continue
                if m["stun"]>0: m["stun"]-=1; continue

                dist=math.hypot(m["x"]-self.px, m["y"]-self.py)
                if dist<250: m["aggro"]=True

                if m["aggro"]:
                    # chase player slowly
                    if dist>30:
                        spd_m=0.7+m["scale"]*0.3
                        ddx=(self.px-m["x"])/max(1,dist)*spd_m
                        ddy=(self.py-m["y"])/max(1,dist)*spd_m
                        # try move
                        nmx=m["x"]+ddx; nmy=m["y"]+ddy
                        if self._world_walkable(nmx,m["y"]): m["x"]=nmx
                        if self._world_walkable(m["x"],nmy): m["y"]=nmy

                    # shoot bullet at player
                    m["atk_cd"]-=1
                    if m["atk_cd"]<=0:
                        m["atk_cd"]=int(100/m["scale"])
                        if dist<300:
                            ddx=(self.px-m["x"])/max(1,dist)
                            ddy=(self.py-m["y"])/max(1,dist)
                            spread=random.uniform(-0.2,0.2)
                            m["bullets"].append({"x":m["x"],"y":m["y"],
                                "vx":(ddx+spread)*3.5,"vy":(ddy+spread)*3.5,
                                "r":7,"life":80,"dmg":int(8*m["scale"])})
                else:
                    # wander
                    m["x"]+=m["vx"]; m["y"]+=m["vy"]
                    if not self._world_walkable(m["x"]+m["vx"]*4, m["y"]):
                        m["vx"]*=-1
                    if not self._world_walkable(m["x"], m["y"]+m["vy"]*4):
                        m["vy"]*=-1

                # update monster bullets
                for b in m["bullets"][:]:
                    b["x"]+=b["vx"]; b["y"]+=b["vy"]; b["life"]-=1
                    if b["life"]<=0 or not self._world_walkable(b["x"]//TILE_SIZE*TILE_SIZE//TILE_SIZE,
                                                                  b["y"]//TILE_SIZE*TILE_SIZE//TILE_SIZE):
                        m["bullets"].remove(b); continue
                    # hit player
                    if math.hypot(b["x"]-self.px, b["y"]-self.py)<b["r"]+10:
                        self.shake=6
                        self.particles.emit(self.px,self.py,n=8,
                            color=[(255,80,80),(255,160,0)],spd=3,life=15,sz=4,grav=0)
                        m["bullets"].remove(b)

        # update player projectiles
        for proj in self.projectiles[:]:
            proj["x"]+=proj["vx"]; proj["y"]+=proj["vy"]; proj["life"]-=1
            if proj["life"]<=0: self.projectiles.remove(proj); continue
            tx=int(proj["x"]//TILE_SIZE); ty=int(proj["y"]//TILE_SIZE)
            if not self._is_walkable(tx,ty): self.projectiles.remove(proj); continue
            # check hit monster
            hit=False
            for room in self.rooms:
                for m in room.monsters:
                    if not m["alive"]: continue
                    if math.hypot(proj["x"]-m["x"],proj["y"]-m["y"])<m["scale"]*20+proj["r"]:
                        m["hp"]-=proj["dmg"]; m["stun"]=15; hit=True
                        self.particles.emit(m["x"],m["y"],n=8,
                            color=[(255,150,50),(200,50,50)],spd=3,life=18,sz=5,grav=0)
                        if m["hp"]<=0:
                            m["alive"]=False; self.big_killed+=1
                            self.state["big_monsters"]=min(5,self.state["big_monsters"]+1)
                            self.particles.emit(m["x"],m["y"],n=20,
                                color=[(255,200,0),(200,50,50),(100,200,255)],
                                spd=6,life=40,sz=7,grav=-0.05)
                        break
                if hit: break
            if hit: self.projectiles.remove(proj); continue

        # check win: all non-entry rooms cleared
        all_clear=all(r.cleared for r in self.rooms[1:] if r.monsters)
        if all_clear and self.big_killed>0:
            self.result="win"

        # check if we got 5 big monsters total
        if self.state["big_monsters"]>=5 and not self.result:
            self.result="win"

    # ── drawing ──────────────────────────────────────────────────────────
    def draw(self, s):
        if self.result:
            self._draw_game(s)
            self._draw_result(s)
            return
        self._draw_game(s)

    def _draw_game(self, s):
        ox = random.randint(-3,3) if self.shake else 0
        oy = random.randint(-3,3) if self.shake else 0

        cam_x = int(self.cam_x)
        cam_y = int(self.cam_y)

        # draw tiles
        s.fill(C["cave"])
        start_tx = max(0, cam_x//TILE_SIZE-1)
        start_ty = max(0, cam_y//TILE_SIZE-1)
        end_tx   = min(self.MAP_W, start_tx + SW//TILE_SIZE+3)
        end_ty   = min(self.MAP_H, start_ty + SH//TILE_SIZE+3)

        for tx in range(start_tx, end_tx):
            for ty in range(start_ty, end_ty):
                sx = tx*TILE_SIZE - cam_x + ox
                sy = ty*TILE_SIZE - cam_y + oy
                tile = self.tiles[tx][ty]
                explored = self.explored[tx][ty]

                if not explored:
                    pxr(s, C["fog"], (sx, sy, TILE_SIZE, TILE_SIZE))
                    continue

                if tile == TILE_WALL:
                    # stone wall with texture
                    pxr(s, C["cavewall"], (sx, sy, TILE_SIZE, TILE_SIZE))
                    pxr(s, C["darkstone"], (sx, sy, TILE_SIZE, TILE_SIZE), 1)
                    # brick lines
                    if (tx+ty)%2==0:
                        pygame.draw.line(s, C["darkstone"],
                            (sx+TILE_SIZE//2, sy), (sx+TILE_SIZE//2, sy+TILE_SIZE), 1)
                    pygame.draw.line(s, C["darkstone"],
                        (sx, sy+TILE_SIZE//2), (sx+TILE_SIZE, sy+TILE_SIZE//2), 1)
                else:
                    # floor
                    base=C["cavefloor"]
                    # subtle variation
                    rng = ((tx*7+ty*13)%5)*3
                    col = (base[0]+rng, base[1]+rng, base[2]+rng)
                    pxr(s, col, (sx, sy, TILE_SIZE, TILE_SIZE))
                    # floor cracks
                    if (tx*3+ty*7)%11==0:
                        pygame.draw.line(s, C["darkstone"],
                            (sx+8, sy+10), (sx+20, sy+30), 1)
                    if tile == TILE_ENTRY:
                        pxr(s, (60,80,60), (sx+4, sy+4, TILE_SIZE-8, TILE_SIZE-8))
                        pxt(s,"IN",F_SM,C["green"],sx+TILE_SIZE//2,sy+TILE_SIZE//2,center=True,shadow=False)

        # dim overlay for unexplored (lighter for semi-visible)
        ptx=int(self.px//TILE_SIZE); pty=int(self.py//TILE_SIZE)
        for tx in range(start_tx, end_tx):
            for ty in range(start_ty, end_ty):
                if not self.explored[tx][ty]: continue
                d=math.hypot(tx-ptx, ty-pty)
                if d>self.FOG_R-1:
                    sx=tx*TILE_SIZE-cam_x+ox; sy=ty*TILE_SIZE-cam_y+oy
                    alpha=min(220, int((d-(self.FOG_R-1))*120))
                    fog=pygame.Surface((TILE_SIZE,TILE_SIZE),pygame.SRCALPHA)
                    fog.fill((8,5,4,alpha))
                    s.blit(fog,(sx,sy))

        # draw torches in rooms
        tf=self.torch_flicker
        for room in self.rooms:
            if not self.explored[room.cx][room.cy]: continue
            # torch at room corners (world coord)
            for corner in [(room.tx+1,room.ty+1),(room.tx+room.tw-2,room.ty+1)]:
                wx_=corner[0]*TILE_SIZE-cam_x+TILE_SIZE//2+ox
                wy_=corner[1]*TILE_SIZE-cam_y+TILE_SIZE//2+oy
                if -20<wx_<SW+20 and -20<wy_<SH+20:
                    # torch glow
                    glow=pygame.Surface((40,40),pygame.SRCALPHA)
                    pygame.draw.circle(glow,(200,120,40,60+tf*10),(20,20),18+tf)
                    s.blit(glow,(wx_-20,wy_-20))
                    pxr(s,C["brown"],(wx_-2,wy_-6,4,10))
                    pygame.draw.polygon(s,(255,180,0+tf*20),
                        [(wx_-3,wy_-6),(wx_+3,wy_-6),(wx_,wy_-14+tf)])

        # draw monsters (only in explored area)
        for room in self.rooms:
            if not self.explored[room.cx][room.cy]: continue
            for m in room.monsters:
                if not m["alive"]: continue
                mx=int(m["x"]-cam_x+ox); my=int(m["y"]-cam_y+oy)
                if -60<mx<SW+60 and -80<my<SH+80:
                    draw_big_monster(s, mx, my, m["color"], m["scale"])
                    # hp bar
                    bw=int(50*m["scale"]); bh=5
                    hpbar(s, mx-bw//2, my-int(90*m["scale"])-4, bw, bh,
                          m["hp"], m["maxhp"], (200,50,50))
                    if m["stun"]>0:
                        pxt(s,"STUN",F_SM,C["yellow"],mx,my-int(100*m["scale"]),
                            center=True,shadow=False)
                # monster bullets
                for b in m["bullets"]:
                    bsx=int(b["x"]-cam_x+ox); bsy=int(b["y"]-cam_y+oy)
                    if 0<bsx<SW and 0<bsy<SH:
                        pygame.draw.circle(s,(200,60,60),(bsx,bsy),b["r"])
                        pygame.draw.circle(s,C["red"],(bsx,bsy),b["r"],1)

        # draw player projectiles
        for proj in self.projectiles:
            px_=int(proj["x"]-cam_x+ox); py_=int(proj["y"]-cam_y+oy)
            if 0<px_<SW and 0<py_<SH:
                draw_small_monster(s, px_, py_, proj["variant"], 0.7)

        # draw particles
        self.particles.draw(s, -cam_x+ox, -cam_y+oy)

        # draw friends
        ha=self.state.get("has_friend_a"); hb=self.state.get("has_friend_b")
        if ha: draw_friend_a(s, self.px-cam_x-40+ox, self.py-cam_y+oy, self.frame)
        if hb: draw_friend_b(s, self.px-cam_x+40+ox, self.py-cam_y+oy, self.frame)

        # draw player
        sx=int(self.px-cam_x+ox); sy=int(self.py-cam_y+oy)
        draw_player(s, sx, sy, frame=self.frame,
                    sword=self.sword_anim>0, ult=self.ult_anim>0)

        # sword range circle
        if self.sword_anim>0:
            pygame.draw.circle(s,(255,220,0),(sx,sy),self.SWORD_R,2)
        if self.ult_anim>0:
            surf2=pygame.Surface((SW,SH),pygame.SRCALPHA)
            pygame.draw.circle(surf2,(255,200,0,50),(sx,sy),self.ULT_R)
            s.blit(surf2,(0,0))
            pygame.draw.circle(s,(255,220,80),(sx,sy),self.ULT_R,3)

        # ── HUD ─────────────────────────────────────────
        # dark HUD bar top
        pxr(s,(10,8,6),(0,0,SW,60))
        pxr(s,(40,30,20),(0,60,SW,2))

        bm=self.state["big_monsters"]; am=self.state["small_monsters"]
        killed=sum(1 for r in self.rooms for m in r.monsters if not m["alive"])
        total=sum(len(r.monsters) for r in self.rooms[1:])
        hpbar(s,10,10,160,12,bm,5,(200,80,80))
        pxt(s,f"Monster Takluk: {bm}/5",F_SM,C["white"],10,26)
        pxt(s,f"Ammo: {am}  Terbunuh sesi: {killed}/{total}",F_SM,C["cyan"],10,42)
        pxt(s,f"[J]=Pedang(CD:{self.sword_cd}) [K]=Ult(CD:{self.ult_cd}) [M]=Tembak(CD:{self.shoot_cd})",
            F_SM,C["yellow"],SW//2,6,center=True)
        pxt(s,"[X]=Kembali",F_SM,C["orange"],SW-130,42)

        # minimap
        self._draw_minimap(s)

    def _draw_minimap(self, s):
        mm_scale=3
        mm_w=self.MAP_W*mm_scale; mm_h=self.MAP_H*mm_scale
        mm_x=SW-mm_w-8; mm_y=SH-mm_h-8

        mm=pygame.Surface((mm_w,mm_h))
        mm.fill((5,3,2))
        for tx in range(self.MAP_W):
            for ty in range(self.MAP_H):
                if not self.explored[tx][ty]: continue
                t=self.tiles[tx][ty]
                col=(5,3,2) if t==TILE_WALL else (60,50,40)
                pxr(mm,col,(tx*mm_scale,ty*mm_scale,mm_scale,mm_scale))
        # monsters on minimap
        for room in self.rooms:
            for m in room.monsters:
                if m["alive"] and self.explored[room.cx][room.cy]:
                    mmx=int(m["x"]//TILE_SIZE)*mm_scale
                    mmy=int(m["y"]//TILE_SIZE)*mm_scale
                    pygame.draw.rect(mm,(200,50,50),(mmx,mmy,mm_scale,mm_scale))
        # player dot
        pmx=int(self.px//TILE_SIZE)*mm_scale; pmy=int(self.py//TILE_SIZE)*mm_scale
        pygame.draw.rect(mm,(100,200,255),(pmx,pmy,mm_scale+1,mm_scale+1))

        pxr(s,(20,15,10),(mm_x-2,mm_y-2,mm_w+4,mm_h+4))
        s.blit(mm,(mm_x,mm_y))
        pygame.draw.rect(s,(80,60,40),(mm_x-2,mm_y-2,mm_w+4,mm_h+4),2)
        pxt(s,"PETA",F_SM,C["orange"],mm_x+mm_w//2,mm_y-16,center=True)

    def _draw_result(self, s):
        dim=pygame.Surface((SW,SH),pygame.SRCALPHA); dim.fill((0,0,0,140)); s.blit(dim,(0,0))
        if self.result=="win":
            pxt(s,"SEMUA MONSTER TAKLUK!",F_XL,C["yellow"],SW//2,SH//2-20,center=True)
            pxt(s,f"Total: {self.state['big_monsters']}/5 monster besar",F_MD,C["white"],SW//2,SH//2+30,center=True)
        else:
            pxt(s,"Kembali ke Map...",F_XL,C["red"],SW//2,SH//2,center=True)
        pxt(s,"ENTER untuk lanjut",F_MD,C["ltgray"],SW//2,SH//2+70,center=True)


# ════════════════════════════════════════════════════════════════════════════
#  BIG MONSTER / BOSS  – explore + battle-box duel (for demon king only now)
# ════════════════════════════════════════════════════════════════════════════
class BigBattle:
    def __init__(self,state,is_dk=False):
        self.state=state;self.is_dk=is_dk
        self.phase="explore";self.frame=0
        self.px=0.0;self.pz=5.0
        self.mx=random.uniform(-8,8);self.mz=random.uniform(-20,-8)
        self.found=False
        self.box=pygame.Rect(140,100,SW-280,SH-200)
        self.sx=float(self.box.centerx);self.sy=float(self.box.centery)
        self.mhp_max=350;self.mhp=self.mhp_max
        self.php=100;self.php_max=100
        self.enemy_bullets=[];self.ammo_bullets=[]
        self.atk_timer=0;self.atk_phase=0
        self.bf=0;self.result=None;self.shake=0
        self.turn="enemy";self.turn_timer=0
        self.shoot_cd=0;self.ult_cd=0
        self.sword_anim=0;self.ult_anim=0
        self.particles=Particles()
        self.fax=0.0;self.faz=6.0
        self.fbx=0.0;self.fbz=6.0

    def handle_key(self,k):
        if self.phase=="explore":
            if k==pygame.K_SPACE and self.found: self.phase="battle"
        elif self.phase=="battle":
            if k==pygame.K_j and self.shoot_cd<=0:
                self._fire(1);self.shoot_cd=14;self.sword_anim=12
            if k==pygame.K_k and self.ult_cd<=0:
                self._fire(5);self.ult_cd=100;self.ult_anim=20

    def _fire(self,n):
        ammo=self.state["small_monsters"]
        n=min(n,ammo)
        if n<=0: return
        self.state["small_monsters"]-=n
        for i in range(n):
            spread=(n-1)*14
            angle=-90+(-spread//2+i*(spread//(max(n-1,1)))) if n>1 else -90
            rad=math.radians(angle)
            v=random.randint(0,4)
            self.ammo_bullets.append({"x":self.sx,"y":self.sy-12,
                "vx":math.cos(rad)*9,"vy":math.sin(rad)*9,
                "variant":v,"r":10,"dmg":8 if n==1 else 12})
        self.particles.emit(self.sx,self.sy-10,n=8,
            color=[(255,200,0),(255,100,50)],spd=4,life=16,sz=5,grav=0)

    def update(self):
        self.frame+=1
        if self.phase=="explore": self._upd_ex()
        elif self.phase=="battle": self._upd_bt()

    def _upd_ex(self):
        keys=pygame.key.get_pressed();spd=0.08
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.px-=spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.px+=spd
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.pz-=spd
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.pz+=spd
        self.px=max(-15,min(15,self.px));self.pz=max(-25,min(10,self.pz))
        if abs(self.px-self.mx)<3 and abs(self.pz-self.mz)<3: self.found=True
        self.fax+=(self.px-self.fax)*0.08;self.faz+=(self.pz+1.5-self.faz)*0.08
        self.fbx+=(self.px-self.fbx)*0.08;self.fbz+=(self.pz+2.5-self.fbz)*0.08

    def _proj(self,wx,wz,base_y=400):
        fov=200;rz=wz-(self.pz-2)
        if rz>=-0.1: rz=-0.1
        sc=fov/(-rz)
        return int(SW//2+(wx-self.px)*sc),int(base_y-rz*8),max(0.1,sc)

    def _draw_ex(self,s):
        s.fill(C["sky"])
        pygame.draw.rect(s,C["ground"],(0,SH//2,SW,SH//2))
        pygame.draw.line(s,C["dkgreen"],(0,SH//2),(SW,SH//2),2)
        for tx,tz in[(-5,-8),(-8,-15),(3,-10),(6,-18),(-2,-20),(9,-12)]:
            ex,ey,sc=self._proj(tx,tz)
            if sc<0.01 or not(0<ex<SW and 0<ey<SH): continue
            h=int(80*sc);w=int(24*sc)
            pxr(s,C["brown"],(ex-w//2,ey-h,w,h))
            pygame.draw.ellipse(s,C["dkgreen"],(ex-w,ey-h-int(w*1.2),w*2,int(w*1.4)))
        ex,ey,sc=self._proj(self.mx,self.mz)
        if 0<ex<SW and 0<ey<SH and sc>0.05:
            draw_demon_king(s,ex,ey,self.frame)
            if self.found: pxt(s,"! DITEMUKAN !",F_MD,C["yellow"],ex,ey-90,center=True)
        ha=self.state.get("has_friend_a");hb=self.state.get("has_friend_b")
        if ha:
            fx,fy,fsc=self._proj(self.fax-1,self.faz)
            if 0<fx<SW and 0<fy<SH: draw_friend_a(s,fx,fy,self.frame)
        if hb:
            fx,fy,fsc=self._proj(self.fbx+1,self.fbz)
            if 0<fx<SW and 0<fy<SH: draw_friend_b(s,fx,fy,self.frame)
        pxr(s,C["red"],(SW//2-6,SH//2+20,12,16))
        pxr(s,C["cream"],(SW//2-5,SH//2+6,10,12))
        pxt(s,"Eksplorasi – Cari RAJA IBLIS",F_SM,C["white"],8,8)
        pxt(s,"WASD=gerak | SPASI=lawan (setelah ditemukan)",F_SM,C["ltgray"],8,28)
        pxt(s,"[X]=Kembali",F_SM,C["orange"],SW-150,8)
        if self.found: pxt(s,"[SPASI] Mulai Pertarungan!",F_MD,C["yellow"],SW//2,SH-40,center=True)

    def _upd_bt(self):
        if self.result: return
        self.bf+=1
        if self.shake>0: self.shake-=1
        if self.sword_cd>0: self.sword_cd-=1
        if self.ult_cd>0:   self.ult_cd-=1
        if self.sword_anim>0: self.sword_anim-=1
        if self.ult_anim>0:   self.ult_anim-=1
        self.particles.update()

        if self.turn=="enemy":
            keys=pygame.key.get_pressed();spd=3.5
            if keys[pygame.K_LEFT]:  self.sx=max(self.box.left+6,self.sx-spd)
            if keys[pygame.K_RIGHT]: self.sx=min(self.box.right-6,self.sx+spd)
            if keys[pygame.K_UP]:    self.sy=max(self.box.top+6,self.sy-spd)
            if keys[pygame.K_DOWN]:  self.sy=min(self.box.bottom-6,self.sy+spd)
            self.atk_timer+=1
            if self.atk_timer>=28:
                self.atk_timer=0;self._spawn_ebullets()
            for b in self.enemy_bullets[:]:
                b["x"]+=b["vx"];b["y"]+=b["vy"]
                if not self.box.inflate(20,20).collidepoint(b["x"],b["y"]):
                    self.enemy_bullets.remove(b);continue
                if math.hypot(b["x"]-self.sx,b["y"]-self.sy)<b["r"]+5:
                    self.php-=b.get("dmg",10);self.shake=6;self.enemy_bullets.remove(b)
            mcx=SW//2;mcy=120
            for b in self.ammo_bullets[:]:
                b["x"]+=b["vx"];b["y"]+=b["vy"]
                if not pygame.Rect(0,0,SW,SH).collidepoint(b["x"],b["y"]):
                    self.ammo_bullets.remove(b);continue
                if math.hypot(b["x"]-mcx,b["y"]-mcy)<55:
                    self.mhp-=b["dmg"]
                    self.particles.emit(b["x"],b["y"],n=6,
                        color=[(255,150,50),(255,100,100)],spd=3,life=18,sz=4,grav=0)
                    self.ammo_bullets.remove(b)
            if self.bf%300==0:
                self.turn="player_turn";self.turn_timer=100;self.enemy_bullets.clear()
        elif self.turn=="player_turn":
            self.turn_timer-=1
            if self.turn_timer<=0:
                dmg=random.randint(15,30)
                if self.state.get("has_friend_a"): dmg+=random.randint(5,12)
                if self.state.get("has_friend_b"): dmg+=random.randint(5,12)
                dmg+=self.state["big_monsters"]*8
                self.mhp-=dmg;self.turn="enemy";self.bf=0

        if self.php<=0: self.php=0;self.result="lose"
        if self.mhp<=0: self.mhp=0;self.result="win"

    def _spawn_ebullets(self):
        cx,cy=self.box.centerx,self.box.centery
        ap=self.atk_phase%4;self.atk_phase+=1
        for ang in range(0,360,30):
            r=math.radians(ang+self.bf*3)
            self.enemy_bullets.append({"x":float(cx),"y":float(cy),
                "vx":math.cos(r)*4,"vy":math.sin(r)*4,"r":7,"color":C["red"],"dmg":12})
        dx=self.sx-cx;dy=self.sy-cy;d=max(1,math.hypot(dx,dy))
        for off in[-0.2,0,0.2]:
            self.enemy_bullets.append({"x":float(cx),"y":float(cy),
                "vx":(dx/d+off)*5,"vy":(dy/d+off)*5,"r":8,"color":C["purple"],"dmg":14})

    def _draw_bt(self,s):
        s.fill((10,10,20))
        ox=random.randint(-3,3) if self.shake else 0
        pxr(s,C["black"],self.box.inflate(6,6));pxr(s,C["white"],self.box,3)
        mcx=SW//2+ox
        draw_demon_king(s,mcx,120,self.bf)
        hpbar(s,self.box.left,self.box.top-22,self.box.width,14,self.mhp,self.mhp_max,(200,60,60))
        pxt(s,"RAJA IBLIS HP",F_SM,C["white"],self.box.left,self.box.top-38)
        for b in self.enemy_bullets:
            pygame.draw.circle(s,b["color"],(int(b["x"]+ox),int(b["y"])),b["r"])
            pygame.draw.circle(s,C["white"],(int(b["x"]+ox),int(b["y"])),b["r"],1)
        for b in self.ammo_bullets:
            draw_small_monster(s,b["x"]+ox,b["y"],b["variant"])
        self.particles.draw(s)
        if self.ult_anim>0:
            surf2=pygame.Surface((SW,SH),pygame.SRCALPHA)
            pygame.draw.circle(surf2,(255,200,0,60),(int(self.sx+ox),int(self.sy)),50)
            s.blit(surf2,(0,0))
        pygame.draw.polygon(s,C["red"],
            [(int(self.sx+ox),int(self.sy-8)),
             (int(self.sx-7+ox),int(self.sy+6)),
             (int(self.sx+7+ox),int(self.sy+6))])
        draw_player(s,self.sx+ox,self.sy+30,sword=self.sword_anim>0,ult=self.ult_anim>0,frame=self.bf)
        ha=self.state.get("has_friend_a");hb=self.state.get("has_friend_b")
        if ha: draw_friend_a(s,self.box.left-30,self.box.centery,self.bf)
        if hb: draw_friend_b(s,self.box.right+30,self.box.centery,self.bf)
        hpbar(s,self.box.left,self.box.bottom+8,self.box.width,14,self.php,self.php_max,(80,200,80))
        pxt(s,f"HP: {self.php}",F_SM,C["white"],self.box.left,self.box.bottom+26)
        ammo=self.state["small_monsters"]
        pxt(s,f"Ammo (monster kecil): {ammo}",F_SM,C["cyan"],self.box.left,self.box.bottom+46)
        pxt(s,f"[J]=Lempar 1 (CD:{self.shoot_cd})  [K]=Lempar 5 (CD:{self.ult_cd})",
            F_SM,C["yellow"],self.box.left,self.box.bottom+62)
        if self.turn=="player_turn":
            pxt(s,f"GILIRAN SERANG! ({self.turn_timer//60+1}s)",F_MD,C["yellow"],SW//2,self.box.bottom+82,center=True)
        else:
            pxt(s,"DODGE! WASD=gerak | J/K=lempar monster",F_SM,C["ltgray"],SW//2,self.box.bottom+82,center=True)
        pxt(s,"[X]=Kembali",F_SM,C["orange"],SW-150,10)
        if ammo<=0 and self.turn=="enemy":
            pxt(s,"AMMO HABIS! Survive sampai giliran auto-attack",F_SM,C["red"],SW//2,self.box.top-56,center=True)
        if self.result:
            msg="MENANG!" if self.result=="win" else "KALAH..."
            col=C["yellow"] if self.result=="win" else C["red"]
            pxr(s,C["black"],(SW//2-120,SH//2-30,240,60))
            pxt(s,msg,F_XL,col,SW//2,SH//2,center=True)
            pxt(s,"ENTER lanjut",F_SM,C["white"],SW//2,SH//2+40,center=True)

    def draw(self,s):
        if self.phase=="explore": self._draw_ex(s)
        else: self._draw_bt(s)


# ════════════════════════════════════════════════════════════════════════════
#  MAIN GAME
# ════════════════════════════════════════════════════════════════════════════
class Game:
    def __init__(self):
        self.state=default_state()
        self.dialog=Dialog()
        self.back_confirm=BackConfirm()
        self.sub=None
        self.particles=Particles()
        self.transition=Transition()
        self.menu_sel=0;self.prologue_step=0
        self.wx=float(SW//2);self.wy=float(SH//2);self.wframe=0
        self._near=None
        self._smap={
            "intro":self._s_intro,"title":self._s_title,"prologue":self._s_prologue,
            "world":self._s_world,"meet_a":self._s_meet_a,
            "meet_b_setup":self._s_meet_b_setup,"meet_b":self._s_meet_b,
            "hunting_small":self._s_hunt_sm,"hunting_big":self._s_hunt_big,
            "pre_final":self._s_pre_final,"final_battle":self._s_final,
            "ending_good":self._s_end_good,"ending_no_friends":self._s_end_nof,
            "ending_weak":self._s_end_weak,"ending_lost":self._s_end_lost,
        }

    def run(self):
        while True:
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: pygame.quit();sys.exit()
                if ev.type==pygame.KEYDOWN and not self.transition.busy:
                    self._key(ev.key)
            screen.fill(C["black"])
            fn=self._smap.get(self.state["scene"],self._s_world);fn()
            self.particles.update();self.particles.draw(screen)
            self.transition.update();self.transition.draw(screen)
            self.back_confirm.draw(screen)
            pygame.display.flip();clock.tick(FPS)

    def _key(self,k):
        if self.back_confirm.visible: self.back_confirm.key(k);return
        scene=self.state["scene"]
        if k==pygame.K_x and scene not in("title","intro","world","prologue",
            "ending_good","ending_no_friends","ending_weak","ending_lost"):
            self.back_confirm.show(self._go_world);return

        if self.sub:
            if isinstance(self.sub,SmallHunt):
                self.sub.handle_key(k)
                if self.sub.phase in("done","full"):
                    if k in(pygame.K_RETURN,pygame.K_z) or self.sub.result=="full":
                        self._end_sub()
            elif isinstance(self.sub,DungeonCave):
                self.sub.handle_key(k)
                if self.sub.result and k in(pygame.K_RETURN,pygame.K_z):
                    self._end_sub()
            elif isinstance(self.sub,BigBattle):
                self.sub.handle_key(k)
                if self.sub.result and k in(pygame.K_RETURN,pygame.K_z):
                    self._end_sub()
            return

        if self.dialog.visible:
            res=self.dialog.key(k)
            if res is not None: self._on_dlg(res)
            return

        if scene=="title":
            if k in(pygame.K_UP,pygame.K_w):   self.menu_sel=(self.menu_sel-1)%3
            if k in(pygame.K_DOWN,pygame.K_s):  self.menu_sel=(self.menu_sel+1)%3
            if k in(pygame.K_RETURN,pygame.K_z):
                if self.menu_sel==0:
                    self.state=default_state();self.prologue_step=0
                    self.state["scene"]="prologue";self._dlg_prolog()
                elif self.menu_sel==1:
                    sv=load_game()
                    if sv: self.state=sv
                    else: self.dialog.show("System","Tidak ada save ditemukan!")
                elif self.menu_sel==2: pygame.quit();sys.exit()
        elif scene=="world":
            if k==pygame.K_s: save_game(self.state);self.dialog.show("System","✓ Game tersimpan!")
            elif k in(pygame.K_RETURN,pygame.K_z):
                if self._near: self._enter(self._near[7])
                else: self._wadv()
        elif scene in("hunting_small","hunting_big","final_battle"):
            if k in(pygame.K_RETURN,pygame.K_z) and not self.sub: self._start(scene)

    def _go_world(self):
        self.sub=None
        def do(): self.state["scene"]="world"
        self.transition.fade_to(do,8)

    def _on_dlg(self,res):
        sc=self.state["scene"]
        if sc=="intro": self.state["scene"]="title"
        elif sc=="prologue":
            if self.prologue_step==0:
                self.prologue_step=1
                self.dialog.show("Kael","Aku akan mengumpulkan teman-teman dan monster-monster terkuat! Perjalanan menuju kastil Raja Iblis dimulai!")
            else: self.transition.fade_to(lambda:self.state.update({"scene":"world"}),6)
        elif sc=="meet_a":
            if not self.state["flags"].get("a_cd"):
                self.state["flags"]["a_cd"]=True
                if res==0: self.state["has_friend_a"]=True;self.dialog.show("A","Sip! Petualangan seru. Ayo!")
                else: self.dialog.show("A","Oh... baiklah. Hati-hati.")
            else: self.state["scene"]="world"
        elif sc=="meet_b_setup":
            if res==0: self.state["flags"]["b_bs"]=True;self.sub=SmallHunt(self.state)
            else: self.state["scene"]="world"
        elif sc=="meet_b":
            if not self.state["flags"].get("b_cd"):
                self.state["flags"]["b_cd"]=True
                if res==0: self.state["has_friend_b"]=True;self.dialog.show("B","Haah... baiklah. Tapi jangan harap aku jadi lemah!")
                else: self.dialog.show("B","Hmph. Aku tidak mau ikut orang lemah.")
            else: self.state["scene"]="world"
        elif sc=="pre_final": self._chk_final()
        elif sc in("ending_good","ending_no_friends","ending_weak","ending_lost"):
            self.state["scene"]="title";save_game(self.state)
        if res==-1 and self.state["flags"].get("_bw"):
            self.state["flags"].pop("_bw")
            self.transition.fade_to(lambda:self.state.update({"scene":"world"}),8)

    def _end_sub(self):
        sc=self.sub;self.sub=None;scene=self.state["scene"]
        if isinstance(sc,SmallHunt):
            sm=self.state["small_monsters"]
            if scene=="meet_b_setup":
                self.state["scene"]="meet_b";self.state["flags"]["b_cd"]=False;self._dlg()
            elif scene=="hunting_small":
                if sc.result=="full":
                    self.dialog.show("System","Monster sudah 50/50! Cukup untuk melawan Raja Iblis. Kembali ke Map.")
                else:
                    self.dialog.show("System",f"Area bersih! Total: {sm}/50")
                self.state["flags"]["_bw"]=True
        elif isinstance(sc,DungeonCave):
            bm=self.state["big_monsters"]
            if sc.result=="win":
                self.dialog.show("System",
                    f"Dungeon bersih! Monster besar: {bm}/5"+
                    (" — SEMUA TERKUMPUL!" if bm>=5 else ""))
            else:
                self.dialog.show("System","Kembali dari dungeon.")
            self.state["flags"]["_bw"]=True
        elif isinstance(sc,BigBattle):
            if scene=="final_battle":
                if sc.result=="win":
                    self.state["defeated_king"]=True
                    for _ in range(6):
                        self.particles.emit(random.randint(100,700),random.randint(100,400),
                            n=30,color=[(255,200,0),(255,100,100),(100,200,255)],
                            spd=6,life=90,sz=7,grav=-0.05)
                    def gg(): self.state["scene"]="ending_good";save_game(self.state);self._dlg()
                    self.transition.fade_to(gg,5)
                else:
                    def gl(): self.state["scene"]="ending_lost";save_game(self.state);self._dlg()
                    self.transition.fade_to(gl,5)

    def _start(self,scene):
        if scene=="hunting_small": self.sub=SmallHunt(self.state)
        elif scene=="hunting_big":  self.sub=DungeonCave(self.state)
        elif scene=="final_battle": self.sub=BigBattle(self.state,True)

    def _wadv(self):
        fl=self.state["flags"];sm=self.state["small_monsters"];bm=self.state["big_monsters"]
        if not fl.get("met_a"): fl["met_a"]=True;fl["a_cd"]=False;self.state["scene"]="meet_a";self._dlg()
        elif not fl.get("met_b"): fl["met_b"]=True;self.state["scene"]="meet_b_setup";self._dlg()
        elif sm<50: self.state["scene"]="hunting_small";self._dlg()
        elif bm<5:  self.state["scene"]="hunting_big";self._dlg()
        else: self.state["scene"]="pre_final";self._dlg()

    def _enter(self,skey):
        fl=self.state["flags"];sm=self.state["small_monsters"];bm=self.state["big_monsters"]
        if skey=="meet_a":
            if not fl.get("met_a"): fl["met_a"]=True;fl["a_cd"]=False;self.state["scene"]="meet_a";self._dlg()
            else: self.dialog.show("A","Hei! Tetap semangat!" if self.state["has_friend_a"] else "Kamu tidak mengajakku...")
        elif skey=="meet_b_setup":
            if not fl.get("met_b"): fl["met_b"]=True;self.state["scene"]="meet_b_setup";self._dlg()
            else: self.dialog.show("B","Sudah siap?" if self.state["has_friend_b"] else "Kau tidak layak.")
        elif skey=="hunting_small": self.state["scene"]="hunting_small";self._dlg()
        elif skey=="hunting_big":   self.state["scene"]="hunting_big";self._dlg()
        elif skey=="pre_final":
            if sm<50 or bm<5: self.dialog.show("Kael",f"Belum siap! {sm}/50 kecil, {bm}/5 besar.")
            else: self.state["scene"]="pre_final";self._dlg()

    def _chk_final(self):
        ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
        sm=self.state["small_monsters"];bm=self.state["big_monsters"]
        if not ha and not hb: self.state["scene"]="ending_no_friends"
        elif sm<50 or bm<5:   self.state["scene"]="ending_weak"
        else:                  self.state["scene"]="final_battle"
        self._dlg()

    def _dlg_prolog(self):
        self.dialog.show("Narator","Di dunia Arathos, Raja Iblis Malachar telah bangkit kembali. Seorang pemuda bernama Kael memutuskan untuk menghentikannya. Ia tahu ia butuh teman-teman terbaik dan monster-monster kuat di sisinya.")

    def _dlg(self):
        sc=self.state["scene"]
        sm=self.state["small_monsters"];bm=self.state["big_monsters"]
        ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
        D={
            "meet_a":("Kael","Itu A! Petualang terkenal yang selalu ingin mencoba hal baru. Mungkin dia mau ikut?",["Ajak A bergabung","Lewati saja"]),
            "meet_b_setup":("Narator","Di arena kota ada B – monster tamer terkuat. Kalahkan dia dalam pertandingan untuk mengajaknya!",["Mulai pertandingan!","Nanti saja"]),
            "meet_b":("B","Hmph... Kau cukup kuat. Mengapa kau melawanku?",["Ajak B – kalahkan Raja Iblis!","Tidak perlu"]),
            "hunting_small":("Narator",f"Hutan monster kecil! Saat ini: {sm}/50. Tebas dengan pedang [J/K] lalu sentuh monster kuning untuk menangkapnya! [ENTER] Mulai | [X] Kembali"),
            "hunting_big":("Narator",f"Gua Kastil Monster Besar! Saat ini: {bm}/5. Jelajahi dungeon bercabang, bunuh monster dengan pedang [J/K] atau tembak [M]! WASD=gerak. [ENTER] Masuk | [X] Kembali"),
            "pre_final":("Kael",f"A: {'Bersama' if ha else 'Tidak ada'}. B: {'Bersama' if hb else 'Tidak ada'}. Monster: {sm}/50 kecil, {bm}/5 besar. Kastil Raja Iblis ada di depan!"),
            "final_battle":("Narator","RAJA IBLIS MALACHAR! Di battle: dodge peluru, lempar monster kecil [J/K] untuk menyerang! [ENTER] Mulai | [X] Kembali"),
            "ending_good":("Narator","LUAR BIASA! Raja Iblis Malachar jatuh! Dunia Arathos damai. Kael dan sahabat-sahabatnya menjadi pahlawan legendaris! ★ ENDING TERBAIK ★"),
            "ending_no_friends":("Narator","Kael berdiri sendiri. Tanpa teman ia memutuskan mundur. ENDING: Sendirian..."),
            "ending_weak":("Narator",f"Monster tidak cukup! ({sm}/50 kecil, {bm}/5 besar). Raja Iblis terlalu kuat. ENDING: Berlatih lebih keras..."),
            "ending_lost":("Narator","Raja Iblis terlalu kuat! Kael mundur. Semangat tidak padam. ENDING: Perjuangan belum berakhir!"),
        }
        if sc in D:
            d=D[sc];self.dialog.show(d[0],d[1],d[2] if len(d)>2 else None)

    # ── scene renderers ──────────────────────────────────────────────────
    def _s_intro(self):
        screen.fill(C["black"])
        pxt(screen,"DEMON KING QUEST",F_TTL,C["red"],SW//2,SH//2-40,center=True)
        pxt(screen,"Tekan ENTER untuk mulai",F_MD,C["white"],SW//2,SH//2+40,center=True)
        if not self.dialog.visible: self.dialog.show("","Selamat datang di Demon King Quest!")
        self.dialog.update();self.dialog.draw(screen)

    def _s_title(self):
        screen.fill((10,5,20))
        random.seed(42)
        for _ in range(80): pygame.draw.circle(screen,C["white"],(random.randint(0,SW),random.randint(0,SH//2)),random.randint(1,2))
        random.seed()
        pxt(screen,"DEMON KING QUEST",F_TTL,C["red"],SW//2,80,center=True)
        pxt(screen,"～ Quest of Legends ～",F_MD,C["orange"],SW//2,130,center=True)
        draw_player(screen,SW//2-120,300);draw_friend_a(screen,SW//2,300);draw_friend_b(screen,SW//2+120,300)
        draw_demon_king(screen,SW//2,490)
        for i,lbl in enumerate(["New Game","Load Game","Quit"]):
            col=C["yellow"] if i==self.menu_sel else C["ltgray"]
            pxt(screen,("> " if i==self.menu_sel else "  ")+lbl,F_LG,col,SW//2,360+i*42,center=True)
        sm=self.state["small_monsters"];bm=self.state["big_monsters"]
        ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
        pxt(screen,f"Save: SM={sm}/50 BM={bm}/5 A={'v'if ha else'x'} B={'v'if hb else'x'}",F_SM,C["gray"],SW//2,SH-30,center=True)
        self.dialog.update();self.dialog.draw(screen)

    def _s_prologue(self):
        screen.fill((20,10,40))
        for i in range(5): pygame.draw.line(screen,(40,20,60),(0,80+i*60),(SW,80+i*60),2)
        pxt(screen,"PROLOG",F_XL,C["yellow"],SW//2,30,center=True)
        draw_player(screen,SW//2,SH//2-40)
        if not self.dialog.visible and self.prologue_step==0: self._dlg_prolog()
        self.dialog.update();self.dialog.draw(screen)

    def _s_world(self):
        self.wframe+=1
        keys=pygame.key.get_pressed();spd=3.0
        if not self.dialog.visible and not self.back_confirm.visible:
            if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.wx=max(20,self.wx-spd)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.wx=min(SW-20,self.wx+spd)
            if keys[pygame.K_UP]    or keys[pygame.K_w]: self.wy=max(50,self.wy-spd)
            if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.wy=min(SH-50,self.wy+spd)
        screen.fill(C["dkgreen"])
        for gx in range(0,SW,40): pygame.draw.line(screen,(40,110,40),(gx,0),(gx,SH))
        for gy in range(0,SH,40): pygame.draw.line(screen,(40,110,40),(0,gy),(SW,gy))
        sm=self.state["small_monsters"];bm=self.state["big_monsters"]
        ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
        locs=[
            (120,100,80,60,C["brown"],"Desa A","Temui Teman A","meet_a"),
            (580,120,80,60,C["purple"],"Arena B","Temui Teman B","meet_b_setup"),
            (200,380,90,60,C["darkred"],"Hutan Monster",f"Berburu Kecil {sm}/50","hunting_small"),
            (560,380,90,60,C["dkgray"],"Gua Monster",f"Dungeon Besar {bm}/5","hunting_big"),
            (SW//2,80,100,55,(80,0,80),"Kastil Iblis","Pertarungan Final","pre_final"),
        ]
        path=[(120,130),(200,410),(560,410),(580,150),(SW//2,107)]
        for i in range(len(path)-1): pygame.draw.line(screen,(80,150,80),path[i],path[i+1],6)
        near=None
        for lx,ly,lw,lh,col,label,hint,skey in locs:
            rect=pygame.Rect(lx-lw//2,ly-lh//2,lw,lh)
            dist=math.hypot(self.wx-lx,self.wy-ly)
            if dist<70:
                near=(lx,ly,lw,lh,col,label,hint,skey)
                pulse=int(abs(math.sin(pygame.time.get_ticks()/300))*6)
                pygame.draw.rect(screen,C["yellow"],rect.inflate(pulse*2,pulse*2),3)
            pxr(screen,col,rect,2,C["black"])
            pxr(screen,tuple(min(c+40,255) for c in col),rect.inflate(-20,-20))
            pxt(screen,label,F_SM,C["white"],lx,ly-lh//2-16,center=True)
        if ha: draw_friend_a(screen,self.wx-40,self.wy+4,self.wframe)
        if hb: draw_friend_b(screen,self.wx+40,self.wy+4,self.wframe)
        draw_player(screen,self.wx,self.wy,frame=self.wframe)
        if near and not self.dialog.visible:
            lx,ly,lw,lh,col,label,hint,skey=near
            bw2=310;bh2=44
            pxr(screen,C["black"],(SW//2-bw2//2,SH-100,bw2,bh2))
            pxr(screen,col,(SW//2-bw2//2,SH-100,bw2,bh2),3)
            pxt(screen,f"[ENTER] {hint}",F_SM,C["yellow"],SW//2,SH-78,center=True)
        pxt(screen,"PETA DUNIA",F_LG,C["yellow"],SW//2,14,center=True)
        pxt(screen,f"Monster: {sm}/50 kecil | {bm}/5 besar",F_SM,C["white"],8,8)
        pxt(screen,f"Teman: {'A✓'if ha else'A✗'} {'B✓'if hb else'B✗'}",F_SM,C["cyan"],8,28)
        pxt(screen,"WASD=gerak  ENTER=masuk lokasi  S=simpan",F_SM,C["yellow"],8,SH-28)
        self._near=near;self.dialog.update();self.dialog.draw(screen)

    def _s_meet_a(self):
        screen.fill((80,120,60));pygame.draw.rect(screen,C["dkgreen"],(0,SH-100,SW,100))
        draw_player(screen,SW//2-80,SH//2+20);draw_friend_a(screen,SW//2+80,SH//2+20)
        pxt(screen,"BERTEMU TEMAN A",F_LG,C["yellow"],SW//2,20,center=True)
        pxt(screen,"A – Si Petualang Sejati",F_MD,C["orange"],SW//2+80,SH//2-60,center=True)
        pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
        if not self.dialog.visible and not self.state["flags"].get("a_is"): self.state["flags"]["a_is"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

    def _s_meet_b_setup(self):
        screen.fill((40,40,80));pygame.draw.rect(screen,(60,60,100),(100,100,SW-200,SH-200),4)
        draw_player(screen,SW//2-120,SH//2+40);draw_friend_b(screen,SW//2+120,SH//2+40)
        pxt(screen,"ARENA PERTANDINGAN",F_LG,C["yellow"],SW//2,20,center=True)
        pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
        if not self.dialog.visible and not self.state["flags"].get("b_ss"): self.state["flags"]["b_ss"]=True;self._dlg()
        if self.sub: self.sub.update();self.sub.draw(screen)
        self.dialog.update();self.dialog.draw(screen)

    def _s_meet_b(self):
        screen.fill((40,40,80))
        draw_player(screen,SW//2-120,SH//2+40);draw_friend_b(screen,SW//2+120,SH//2+40)
        pxt(screen,"BERTEMU TEMAN B",F_LG,C["yellow"],SW//2,20,center=True)
        pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
        if not self.dialog.visible and not self.state["flags"].get("b_ms"): self.state["flags"]["b_ms"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

    def _s_hunt_sm(self):
        if self.sub: self.sub.update();self.sub.draw(screen)
        else:
            screen.fill(C["dkgreen"])
            pxt(screen,"HUTAN MONSTER KECIL",F_LG,C["yellow"],SW//2,30,center=True)
            pxt(screen,f"Total: {self.state['small_monsters']}/50",F_MD,C["white"],SW//2,80,center=True)
            pxt(screen,"[ENTER] Mulai berburu!",F_LG,C["cyan"],SW//2,SH//2,center=True)
            pxt(screen,"[J]=Tebas [K]=Ultimate — sentuh monster kuning untuk tangkap!",F_SM,C["yellow"],SW//2,SH//2+50,center=True)
            pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
            for i in range(8):
                a=i*45;draw_small_monster(screen,SW//2+math.cos(math.radians(a))*120,SH//2+80+math.sin(math.radians(a))*60,i)
            ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
            if ha: draw_friend_a(screen,SW//2-70,SH//2+80)
            if hb: draw_friend_b(screen,SW//2+70,SH//2+80)
            draw_player(screen,SW//2,SH//2+80,sword=True)
        self.dialog.update();self.dialog.draw(screen)

    def _s_hunt_big(self):
        if self.sub: self.sub.update();self.sub.draw(screen)
        else:
            screen.fill(C["cave"])
            # cave entrance screen
            for gx in range(0,SW,48):
                for gy in range(0,SH,48):
                    if (gx//48+gy//48)%2==0:
                        pxr(screen,C["cavewall"],(gx,gy,48,48))
                    pygame.draw.rect(screen,C["darkstone"],(gx,gy,48,48),1)
            # torches
            for tx in [100,300,500,700]:
                pxr(screen,C["brown"],(tx-2,SH//2-30,4,20))
                pygame.draw.polygon(screen,(255,160,0),[(tx-4,SH//2-30),(tx+4,SH//2-30),(tx,SH//2-46)])
                glow=pygame.Surface((60,60),pygame.SRCALPHA)
                pygame.draw.circle(glow,(200,120,40,50),(30,30),28)
                screen.blit(glow,(tx-30,SH//2-58))
            pxt(screen,"GUA KASTIL MONSTER",F_LG,C["orange"],SW//2,30,center=True)
            pxt(screen,f"Total: {self.state['big_monsters']}/5",F_MD,C["white"],SW//2,70,center=True)
            pxt(screen,"[ENTER] Masuk Dungeon!",F_LG,C["cyan"],SW//2,SH//2-20,center=True)
            pxt(screen,"WASD=gerak | J=Pedang | K=Ultimate | M=Tembak monster",F_SM,C["yellow"],SW//2,SH//2+20,center=True)
            pxt(screen,f"Ammo tersedia: {self.state['small_monsters']} monster kecil",F_SM,C["cyan"],SW//2,SH//2+46,center=True)
            pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
            draw_big_monster(screen,SW//2,SH//2+130)
            ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
            if ha: draw_friend_a(screen,SW//2-80,SH//2+130)
            if hb: draw_friend_b(screen,SW//2+80,SH//2+130)
            draw_player(screen,SW//2-130,SH//2+130,sword=True)
        self.dialog.update();self.dialog.draw(screen)

    def _s_pre_final(self):
        screen.fill((30,10,50))
        pxt(screen,"SEBELUM PERTEMPURAN FINAL",F_LG,C["red"],SW//2,20,center=True)
        draw_player(screen,SW//2,SH//2-20,sword=True)
        if self.state["has_friend_a"]: draw_friend_a(screen,SW//2-90,SH//2-20)
        if self.state["has_friend_b"]: draw_friend_b(screen,SW//2+90,SH//2-20)
        draw_demon_king(screen,SW//2,100)
        pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
        if not self.dialog.visible and not self.state["flags"].get("pf_s"): self.state["flags"]["pf_s"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

    def _s_final(self):
        if self.sub: self.sub.update();self.sub.draw(screen)
        else:
            screen.fill((20,0,30))
            pxt(screen,"PERTEMPURAN FINAL!",F_XL,C["red"],SW//2,30,center=True)
            draw_demon_king(screen,SW//2,200,pygame.time.get_ticks()//16)
            ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
            if ha: draw_friend_a(screen,SW//2-120,280)
            if hb: draw_friend_b(screen,SW//2+120,280)
            draw_player(screen,SW//2,280,sword=True)
            pxt(screen,"[ENTER] Mulai pertempuran!",F_MD,C["yellow"],SW//2,SH-60,center=True)
            pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
        self.dialog.update();self.dialog.draw(screen)

    def _bg(self,col):
        screen.fill(col)
        for i in range(0,SW,16): pygame.draw.line(screen,(max(0,col[0]-20),max(0,col[1]-20),max(0,col[2]-20)),(i,0),(i,SH))

    def _s_end_good(self):
        self._bg((10,30,60))
        t=pygame.time.get_ticks()
        for i in range(5):
            cx=100+i*140;cy=100+math.sin(t/500+i)*40
            for a in range(0,360,30):
                r=math.radians(a+t//10);d=30+math.sin(t/200+i)*10
                pygame.draw.circle(screen,[(255,200,0),(255,100,100),(100,200,255),(200,100,255),(100,255,100)][i%5],(int(cx+math.cos(r)*d),int(cy+math.sin(r)*d)),3)
        draw_player(screen,SW//2-120,SH//2+60)
        if self.state["has_friend_a"]: draw_friend_a(screen,SW//2,SH//2+60)
        if self.state["has_friend_b"]: draw_friend_b(screen,SW//2+120,SH//2+60)
        pxt(screen,"★ ENDING TERBAIK ★",F_XL,C["yellow"],SW//2,40,center=True)
        pxt(screen,"Raja Iblis Malachar telah dikalahkan!",F_LG,C["white"],SW//2,110,center=True)
        if not self.dialog.visible and not self.state["flags"].get("eg_d"): self.state["flags"]["eg_d"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

    def _s_end_nof(self):
        self._bg((30,20,10));draw_player(screen,SW//2,SH//2)
        pxt(screen,"ENDING: Sendirian",F_XL,C["orange"],SW//2,40,center=True)
        if not self.dialog.visible and not self.state["flags"].get("en_d"): self.state["flags"]["en_d"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

    def _s_end_weak(self):
        self._bg((20,10,10));draw_player(screen,SW//2-60,SH//2)
        if self.state["has_friend_a"]: draw_friend_a(screen,SW//2+60,SH//2)
        pxt(screen,"ENDING: Kurang Kuat",F_XL,C["red"],SW//2,40,center=True)
        if not self.dialog.visible and not self.state["flags"].get("ew_d"): self.state["flags"]["ew_d"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

    def _s_end_lost(self):
        self._bg((10,5,5))
        pxt(screen,"ENDING: Dikalahkan",F_XL,C["red"],SW//2,40,center=True)
        draw_player(screen,SW//2,SH//2+20)
        if self.state["has_friend_a"]: draw_friend_a(screen,SW//2-80,SH//2+20)
        if self.state["has_friend_b"]: draw_friend_b(screen,SW//2+80,SH//2+20)
        draw_demon_king(screen,SW//2,SH//2-100)
        if not self.dialog.visible and not self.state["flags"].get("el_d"): self.state["flags"]["el_d"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

if __name__=="__main__":
    Game().run()