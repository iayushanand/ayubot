# -------------- import(s) ---------------

from PIL import Image, ImageChops, ImageDraw, ImageFont
from easy_pil import Editor,Canvas


def circle(pfp,size = (110,110)):
    
    pfp = pfp.resize(size, Image.ANTIALIAS).convert("RGBA")
    
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp


def make_banner(av,bg,lvl,xp,req,text,color,color2):

    percent=round(xp/req*100)

    if xp>=1000:
        xp=f"{round(xp/1000,1)}K"
    else:
        xp=round(xp)
    if req>=1000:
        req=f"{round(req/1000,1)}K"
    else:
        req=round(req)


    sub=f"Level: {lvl}   XP : {xp}/{req}"

    font1  = ImageFont.truetype("asset/fonts/font.otf",44)
    font2  = ImageFont.truetype("asset/fonts/font.otf",38)
    pfp    = Image.open(av)
    # bg     = Image.open(bg)


    pfp=circle(pfp)
    bg=bg.crop((0,0,800,200))
    bg.paste(pfp,(15,15),pfp)
    draw=ImageDraw.Draw(bg)
    draw.text((148,20),text,color2,font1)
    draw.text((148,75),sub,color2,font2)
    bg=Editor(bg)
    bg.rectangle((10,150),width=630,height=34,fill=color2,radius=20)
    bg.bar((10,150),max_width=630,height=34,fill=color,radius=20,percentage=percent)
    bg.rectangle((145,75),width=256,height=3,fill=color)
    border= Canvas((400,400),color=color)
    border= Editor(border)
    border.rotate(45.0,expand=True)
    bg.paste(border,(531,-290))

    return bg

def get_xp(content: str, multiplier: float) -> float:
    return round(len(content)*multiplier, 2)