from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

S = 2
W, H = 1200*S, 630*S
BG_TOP = (250, 251, 247)
BG_BOT = (232, 240, 233)
GREEN = (22, 131, 75)
DEEP = (13, 88, 51)
INK = (20, 30, 25)
MUTED = (96, 108, 100)
HAIR = (206, 217, 209)
CARD = (255, 255, 255)

random.seed(7)
FB = '/usr/share/fonts/adobe-source-han-sans/SourceHanSansCN-'
FM = '/usr/share/fonts/noto/NotoSansMono-'
def F(p, s): return ImageFont.truetype(p, s*S)
f_display = F(FB+'Heavy.otf', 94)
f_sub = F(FB+'Bold.otf', 40)
f_body = F(FB+'Medium.otf', 28)
f_small = F(FB+'Regular.otf', 25)
f_mono = F(FM+'Bold.ttf', 20)
f_monor = F(FM+'Regular.ttf', 21)

img = Image.new('RGB', (W, H))
px = img.load()
for y in range(H):
    t = y/(H-1)
    c = tuple(int(BG_TOP[i]+(BG_BOT[i]-BG_TOP[i])*t) for i in range(3))
    for x in range(W): px[x,y] = c
d = ImageDraw.Draw(img, 'RGBA')

def soft_circle(box, fill, blur=40*S):
    lay = Image.new('RGBA', (W,H), (0,0,0,0))
    ImageDraw.Draw(lay).ellipse(box, fill=fill)
    return lay.filter(ImageFilter.GaussianBlur(blur))
img = Image.alpha_composite(img.convert('RGBA'),
    Image.alpha_composite(soft_circle([950*S,-220*S,1440*S,270*S], (190,225,198,150)),
                          soft_circle([-160*S,470*S,260*S,890*S], (190,225,198,120)))).convert('RGB')
d = ImageDraw.Draw(img, 'RGBA')

grid = Image.new('RGBA', (W,H), (0,0,0,0))
gd = ImageDraw.Draw(grid)
for x in range(-H, W, 46*S):
    gd.line([(x,0),(x+H,H)], fill=(13,88,51,10), width=1)
img = Image.alpha_composite(img.convert('RGBA'), grid).convert('RGB')
d = ImageDraw.Draw(img, 'RGBA')

grain = Image.effect_noise((W//3, H//3), 14).convert('L').resize((W,H), Image.BILINEAR)
gpts = grain.load(); ipx = img.load()
for y in range(0,H,2):
    for x in range(0,W,2):
        n = (gpts[x,y]-128)//9
        if n:
            r,g,b = ipx[x,y]
            ipx[x,y] = (max(0,min(255,r+n)), max(0,min(255,g+n)), max(0,min(255,b+n)))
d = ImageDraw.Draw(img, 'RGBA')

def shadowed_paste(base, im, pos, radius, blur=24*S, alpha=70, dy=10*S):
    sh = Image.new('RGBA', base.size, (0,0,0,0))
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0,0,im.size[0],im.size[1]], radius, fill=255)
    black = Image.new('RGBA', im.size, (13,40,26,alpha))
    sh.paste(black, (pos[0], pos[1]+dy), m)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base.convert('RGBA'), sh).convert('RGB')

GX, GY = 88*S, 96*S
card_w, card_h, card_r = 196*S, 196*S, 46*S
img = shadowed_paste(img, Image.new('RGBA',(card_w,card_h),(0,0,0,0)), (GX,GY), card_r)
d = ImageDraw.Draw(img, 'RGBA')
d.rounded_rectangle([GX,GY,GX+card_w,GY+card_h], card_r, fill=CARD, outline=HAIR, width=2*S)
logo = Image.open('/tmp/ls_logo.png').convert('RGBA').resize((156*S,156*S), Image.LANCZOS)
img.paste(logo, (GX+20*S, GY+20*S), logo)

TX = GX + 236*S
d.text((TX, GY+6*S), 'LetSeries', font=f_display, fill=INK)
d.text((TX, GY+112*S), '正式成立', font=f_display, fill=GREEN)
d.rounded_rectangle([TX, GY+212*S, TX+140*S, GY+220*S], 4*S, fill=GREEN)
d.text((TX, GY+234*S), '让服务器好用一点。', font=f_sub, fill=DEEP)
d.text((GX, GY+362*S), 'CubeXMC 研究院旗下开发组织', font=f_body, fill=MUTED)
d.text((GX, GY+400*S), 'MINECRAFT SERVER PLUGINS · 2026.09.09', font=f_monor, fill=MUTED)
d.line([(GX, GY+448*S), (GX+540*S, GY+448*S)], fill=HAIR, width=2*S)

PX, PY, PW, PH = 816*S, 88*S, 296*S, 454*S
img = shadowed_paste(img, Image.new('RGBA',(PW,PH),(0,0,0,0)), (PX,PY), 28*S, blur=30*S, alpha=60)
d = ImageDraw.Draw(img, 'RGBA')
d.rounded_rectangle([PX,PY,PX+PW,PY+PH], 28*S, fill=CARD, outline=HAIR, width=2*S)
d.text((PX+28*S, PY+20*S), 'OPEN SOURCE PROJECTS', font=f_mono, fill=MUTED)
items = ['LetMeDo · 多功能插件', 'LetMeSee · 只读容器查看', 'LetMeAsk · 答题活动',
         'Server-AI · 服内 AI 问答', 'HumanVerify · 人机验证', 'LetMePaytaxes · 税务系统']
y = PY+58*S
for it in items:
    name, desc = it.split(' · ')
    d.ellipse([PX+28*S, y+8*S, PX+38*S, y+18*S], fill=GREEN)
    d.text((PX+50*S, y), name, font=f_body, fill=INK)
    d.text((PX+50*S, y+32*S), desc, font=f_small, fill=MUTED)
    y += 60*S
d.line([(PX+28*S, PY+PH-54*S), (PX+PW-28*S, PY+PH-54*S)], fill=HAIR, width=2*S)
d.text((PX+28*S, PY+PH-42*S), 'github.com/LetSeries', font=f_monor, fill=GREEN)

img = img.resize((1200, 630), Image.LANCZOS)
img.save('/tmp/cover_v2.png')
print('saved v2', img.size)
