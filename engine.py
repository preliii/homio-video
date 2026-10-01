#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOMIO VIDEO ENGINE v12  —  clipuri 1080x1920 din pozele produsului (fără AI generativ).

UTILIZARE
  python engine.py config.json                 # randare completă + QA + contact sheet
  python engine.py config.json --sheet         # doar frame0 + contact sheet (rapid, fără video)
  python engine.py config.json --inspect       # descarcă pozele, arată indexul/tipul lor + paleta
  python engine.py config.json --times 0,1.2   # cadre PNG la momentele date (debug)
  python engine.py --example > config.json     # config de pornire

CONFIG (JSON) — tot ce e marcat * e obligatoriu
{
 "product": {"name"*, "url", "price"* (număr de pe pagină, ex. 193.19), "delivery": "Livrare în 1–2 zile" (doar dacă e pe pagină)},
 "images": [ {"src"* URL|cale, "cutout": "auto|white|card|rembg", "crop": [x0,y0,x1,y1] fracții opțional} ],
 "recipe": "wheels|toy|baby|decor|kitchen|garden|gift|set"  sau listă ["toy","gift"] (a doua dă hook-ul),
 "hook"*: "Max 7 cuvinte",  "hook_accent": "cuvintele evidențiate",  "hook_type": "intrebare|pov|problema|cifra|cadou|contrast",
 "badges": ["3 ani+", "până la 50 kg"],                 # pastile sub produs în hook
 "points": [                                             # 2–4 momente de dovadă
    {"type":"feature","title":"Se pliază","sub":"în câteva secunde","image":1,"fx":"slam","pills":["doar 2 kg"],"sweep":true},
    {"type":"detail","title":"Frână spate","image":2,"focus":[0.3,0.7],"zoom":1.6,"label":"cu piciorul"},
    {"type":"counter","value":50,"suffix":" kg","label":"sarcină maximă","image":0},
    {"type":"split","images":[0,1],"labels":["deschisă","pliată"],"title":"2 în 1"},
    {"type":"grid","images":[0,1,2,3],"title":"Tot setul"},
    {"type":"checklist","title":"De ce o aleg părinții","items":["...","..."],"image":0}
 ],
 "features": ["..."],                                    # scurtătură: adaugă o scenă checklist
 "final": {"cta":"Comandă pe homio.ro", "image":0},
 "season": null|"winter|autumn|spring|summer",
 "sfx": true, "loop": true, "duration": null (auto 12–18 s),
 "palette": {"base":"#hex","accent":"#hex","dark":false}  (opțional, altfel k-means),
 "style": { suprascrie orice cheie din rețetă: hook, fx, transitions, font_title, price, confetti, bg, sweep ... }
 "scenes": [...]  (avansat: listă explicită de scene, aceleași câmpuri ca points + "dur")
}
fx feature: slam, tilt, float, zoom_punch, pushin, mask, spin, parallax, drop, rise
hook: speed, pop, gentle, slam, gift, pan
  (v6) hook "gift": cutie închisă cu fundă (fără produs în frame 0) -> se scutură -> capacul sare -> produsul iese din cutie.
       opțional în config: "gift_box": "#hex", "gift_ribbon": "#hex"
  (v7) logo oficial PNG transparent (assets/homio_logo_4000_transparent.png): colț stânga-sus pe plăcuță crem
       fixă + logo mare direct pe fundal în cadrul signature. Căutare: $HOMIO_LOGO -> ./assets -> lângă engine.py
       -> GitHub raw -> fallback vechiul JPG de pe gomagcdn.
  (v8) "product": {"old_price": 142.34} -> prețul vechi apare tăiat deasupra prețului nou în scena finală
       (QA pret_vechi_taiat). Logo: fișierele invalide (ex. text „404" salvat de curl) sunt ignorate.
  (v9) STIL DE EDIT UNIC PER CLIP: generat automat din hash(produs + hook) (sau "edit_seed" în config), ca două clipuri
       din aceeași zi să nu aibă același edit. Controlează: ritm (±7% pe scene), set și ordine de tranziții, direcția
       tranzițiilor (mișcarea continuă dintr-o scenă în alta), tip de fundal, drift al fundalului, vignetă, grain,
       grading discret, reflexie sub produs, pitch și straturi de sunet. Se poate suprascrie în config:
       "edit": {"vignette":0.2, "grain":0.008, "reflect":0.15, "bg":"dots", "transitions":["whip","zoom"], "sfx_pitch":1.05}
       Semnătura stilului apare în journal.json ("edit").
  (v9) motion blur real (supraeșantionare temporală) la intrări și tranziții; fundal pe 2 straturi (parallax opus);
       umbră de contact + reflexie slabă; decupaj alb fără halou (decontaminare culoare pe margini);
       sunet în straturi (sub-bas la impact, riser înainte de preț, variație de pitch); tranziții noi: zoomout.
  (v10) CLIPURI CU MAI MULTE PRODUSE (2–4 linkuri). În loc de "product" pui "products":
       "products": [ {"name":"Pijama Minnie", "url":"...", "price":72.9, "old_price":null, "label":"Minnie", "images":[0,1]}, ... ],
       "multi": "collection" | "combo"      # collection = același tip de produs (pijamale, ghiozdane, penare)
                                            # combo = produse diferite care merg împreună (ghiozdan + penar + cutie + bidon)
       "character": "Spiderman"             # opțional, doar dacă TOATE produsele au același personaj pe pagină
       "price_label": "De la" | "Tot setul" # implicit: collection -> "De la" (cel mai mic preț), combo -> "Tot setul" (suma)
       "title": "Set școală Spiderman"      # opțional, numele clipului în jurnal
       Motorul face automat: un sprite de grup cu toate produsele (folosit în hook și la final, ca frame 0 să arate tot),
       o scenă "lineup" (collection: produsele intră pe rând, cu etichetă; "numbers": true => 1, 2, 3 pentru „Tu pe care o alegi?")
       sau "combo" (produsele apar ca A + B + C, apoi se strâng într-un singur set), plus prețul cu eticheta potrivită.
       În points/scenes, "image": "group" = toate produsele împreună.
       Scene noi: {"type":"lineup","title":"...","numbers":true}  {"type":"combo","title":"...","pill":"3 piese"}
  (v11) combo cu 3 produse: erou mare sus + 2 dedesubt (înainte: 3 în rând, prea mici).
  (v12) TRANZIȚII PROFESIONALE (19 tipuri). Fiecare clip primește o FAMILIE coerentă de 3–4 tranziții din pool-ul rețetei
       (cum lucrează un editor: un limbaj vizual unitar per clip, variat de la clip la clip), fără aceeași tranziție de 2 ori la rând.
       Intrarea în cadrul signature folosește mereu o tranziție curată (dip / iris / circle / shape / fade).
       Rețetele calme (baby, decor) primesc doar tranziții calme; tranzițiile cu shake/glitch doar la rețetele cu shake.
       Variație față de clipurile anterioare: "edit": {"avoid_transitions": ["flash", "slide", ...]} (scoase din pool dacă rămân ≥ 3).
tranziții: cut, flash, fade, whip, slide, zoom, zoomout                                (v1–v9)
           spin      — whip rotațional cu blur de rotație (±28°), energic            (v12)
           zoomblur  — zoom-through cu blur radial: camera trece „prin" cadru         (v12)
           stretch   — squash & stretch elastic, intrare cu overshoot                (v12)
           blur      — defocus: cadrul iese din focus, următorul intră în focus      (v12, calm)
           punch     — tăietură pe impact: scale 1.14→1 + shake scurt + split RGB    (v12, doar cu shake)
           iris      — dezvăluire circulară cu inel în culoarea accent               (v12, calm)
           wipe      — ștergere diagonală cu margine moale și dâră de lumină         (v12, calm)
           shape     — bandă oblică în culoarea accent, cu margini deschise, acoperă tăietura   (v12)
           circle    — cerc accent care acoperă cadrul, apoi se deschide spre scena nouă         (v12)
           dip       — dip to color (accent închis; crem la rețetele calme)          (v12, calm)
           lightleak — light leak cald (screen blend), ascunde tăietura în lumină    (v12, calm)
           glitch    — 3–4 cadre de split RGB + felii decalate, foarte scurt          (v12, doar cu shake)
           (whip/slide/wipe/shape/circle au direcție L|R|U|D, setată automat; mișcarea continuă dintr-o scenă în alta)
price: stamp, elegant, soft                    bg: stripes, dots, grid, blobs, rays

IEȘIRE în --out (implicit ./out_<slug>): video.mp4, frame0.png, sheet.jpg, qa.json, journal.json
QA afișează doar PASS/FAIL/WARN.
"""
import unicodedata, os, sys, json, math, random, re, subprocess, hashlib, wave, argparse, colorsys, shutil, urllib.request, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SAFE = (60, 150, 960, 1570)
CX_TEXT = 510                     # centrul zonei sigure pe orizontală
TEXT_MAXW = 860
CACHE = os.path.expanduser('~/.cache/homio_engine')
LOGO_URL = 'https://gomagcdn.ro/domains3/homio.ro/files/company/logo9150.jpg'   # fallback (v6)
LOGO_FILE = 'homio_logo_4000_transparent.png'                                     # v7: logo oficial, fundal transparent
LOGO_GH = 'https://raw.githubusercontent.com/preliii/homio-video/main/assets/' + LOGO_FILE
LOGO_PLATE = (255, 249, 238)       # plăcuța crem din colț (aceeași ca fundalul signature)
UA = {'User-Agent': 'Mozilla/5.0 (homio-engine)'}
LOGO_XY = (48, 36)                 # colțul stânga-sus al plăcuței cu logo (fix, tot clipul)
HI = 1.35                          # rezervă de rezoluție pentru zoom

GF = 'https://raw.githubusercontent.com/google/fonts/main/ofl/'
FONTS = {  # key: (file, url, weight for variable fonts or None)
    'poppins-xb': ('Poppins-ExtraBold.ttf', GF + 'poppins/Poppins-ExtraBold.ttf', None),
    'poppins-b':  ('Poppins-Bold.ttf', GF + 'poppins/Poppins-Bold.ttf', None),
    'poppins-sb': ('Poppins-SemiBold.ttf', GF + 'poppins/Poppins-SemiBold.ttf', None),
    'baloo':      ('Baloo2.ttf', GF + 'baloo2/Baloo2%5Bwght%5D.ttf', 800),
    'baloo-sb':   ('Baloo2.ttf', GF + 'baloo2/Baloo2%5Bwght%5D.ttf', 600),
    'playfair':   ('PlayfairDisplay.ttf', GF + 'playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf', 700),
    'montserrat': ('Montserrat.ttf', GF + 'montserrat/Montserrat%5Bwght%5D.ttf', 800),
    'montserrat-sb': ('Montserrat.ttf', GF + 'montserrat/Montserrat%5Bwght%5D.ttf', 600),
    'dmserif':    ('DMSerifDisplay-Regular.ttf', GF + 'dmserifdisplay/DMSerifDisplay-Regular.ttf', None),
}
FALLBACK_FONT = 'poppins-xb'

# ------------------------------------------------------------------ rețete
RECIPES = {
    'wheels':  dict(hook='speed', fx=['slam', 'tilt', 'zoom_punch', 'float'], transitions=['whip', 'flash', 'whip', 'zoom', 'whip'],
                    bg='stripes', price='stamp', confetti=True, shake=True, speedlines=True, stickers=False, sweep=False,
                    font_title='poppins-xb', font_body='poppins-sb', theme='light', tone='energic'),
    'toy':     dict(hook='pop', fx=['tilt', 'spin', 'slam', 'float'], transitions=['zoom', 'flash', 'slide', 'zoom', 'flash'],
                    bg='dots', price='stamp', confetti=True, shake=True, speedlines=False, stickers=True, sweep=False,
                    font_title='baloo', font_body='baloo-sb', theme='light', tone='jucăuș'),
    'baby':    dict(hook='gentle', fx=['float', 'pushin', 'mask', 'float'], transitions=['fade', 'slide', 'fade', 'fade'],
                    bg='blobs', price='soft', confetti=False, shake=False, speedlines=False, stickers=False, sweep=True,
                    font_title='poppins-b', font_body='poppins-sb', theme='pastel', tone='liniștitor'),
    'decor':   dict(hook='gentle', fx=['pushin', 'parallax', 'mask', 'pushin'], transitions=['fade', 'zoom', 'fade', 'fade'],
                    bg='blobs', price='elegant', confetti=False, shake=False, speedlines=False, stickers=False, sweep=True,
                    font_title='playfair', font_body='montserrat-sb', theme='light', tone='elegant'),
    'kitchen': dict(hook='slam', fx=['zoom_punch', 'tilt', 'slam', 'float'], transitions=['whip', 'cut', 'flash', 'whip'],
                    bg='grid', price='stamp', confetti=False, shake=True, speedlines=False, stickers=False, sweep=True,
                    font_title='montserrat', font_body='montserrat-sb', theme='light', tone='practic'),
    'garden':  dict(hook='pan', fx=['parallax', 'float', 'tilt', 'pushin'], transitions=['slide', 'fade', 'whip', 'fade'],
                    bg='blobs', price='stamp', confetti=False, shake=False, speedlines=False, stickers=False, sweep=True,
                    font_title='poppins-xb', font_body='poppins-sb', theme='light', tone='relaxat'),
    'gift':    dict(hook='gift', fx=['tilt', 'float', 'spin', 'slam'], transitions=['zoom', 'flash', 'zoom', 'fade'],
                    bg='rays', price='stamp', confetti=True, shake=True, speedlines=False, stickers=True, sweep=True,
                    font_title='poppins-xb', font_body='poppins-sb', theme='light', tone='festiv'),
    'set':     dict(hook='pop', fx=['slam', 'tilt', 'float', 'spin'], transitions=['flash', 'zoom', 'whip', 'flash'],
                    bg='dots', price='stamp', confetti=True, shake=True, speedlines=False, stickers=True, sweep=False,
                    font_title='poppins-xb', font_body='poppins-sb', theme='light', tone='jucăuș'),
}
# v9: seturi permise per rețetă (păstrează tonul rețetei, dar schimbă combinația de la clip la clip)
TR_POOL = {   # v12: pool-uri lărgite; make_edit alege o familie de 3–4 per clip
    'wheels':  ['whip', 'zoomblur', 'spin', 'punch', 'shape', 'glitch', 'slide', 'flash', 'zoom'],
    'toy':     ['zoom', 'spin', 'circle', 'shape', 'stretch', 'iris', 'flash', 'slide', 'punch', 'zoomout'],
    'baby':    ['fade', 'blur', 'lightleak', 'iris', 'dip', 'slide', 'zoomout'],
    'decor':   ['fade', 'blur', 'lightleak', 'wipe', 'dip', 'zoomout', 'iris'],
    'kitchen': ['whip', 'wipe', 'shape', 'zoomblur', 'cut', 'slide', 'dip', 'zoom'],
    'garden':  ['slide', 'wipe', 'lightleak', 'blur', 'whip', 'zoomout', 'dip'],
    'gift':    ['zoom', 'lightleak', 'circle', 'iris', 'spin', 'flash', 'stretch', 'zoomout'],
    'set':     ['flash', 'zoom', 'shape', 'stretch', 'circle', 'glitch', 'whip', 'punch', 'zoomblur'],
}
# (ieșire, intrare) în secunde
TR_TIME = {'cut': (0, 0), 'flash': (0, .2), 'fade': (.12, .2), 'whip': (.12, .2), 'slide': (.12, .2), 'zoom': (.12, .2),
           'zoomout': (.12, .2), 'spin': (.14, .24), 'zoomblur': (.12, .22), 'stretch': (.12, .24), 'blur': (.16, .26),
           'punch': (0, .2), 'iris': (0, .34), 'wipe': (0, .32), 'shape': (.16, .22), 'circle': (.16, .28), 'dip': (.13, .24),
           'lightleak': (.2, .32), 'glitch': (.07, .1)}
TR_FG_OUT = {'whip', 'zoom', 'zoomout', 'fade', 'slide', 'spin', 'zoomblur', 'stretch', 'blur'}   # scena veche iese animat
TR_MASK = {'iris', 'wipe'}                                      # scena veche rămâne sub mască, cea nouă se dezvăluie
TR_OVL = {'shape', 'circle', 'dip', 'lightleak', 'glitch', 'punch'}   # overlay pe tot cadrul, peste tăietură
TR_CALM = {'fade', 'blur', 'lightleak', 'wipe', 'iris', 'dip', 'zoomout', 'slide', 'cut'}
TR_SHAKE = {'punch', 'glitch'}
TR_ACCENT = {'punch', 'glitch', 'flash'}                     # efecte de accent: max 1 tip per clip
TR_MAX2 = TR_ACCENT | {'shape', 'circle', 'lightleak', 'spin'}   # tranziții foarte vizibile: max 2 utilizări per clip
TR_SIG = ['dip', 'iris', 'circle', 'shape', 'fade']             # intrarea în cadrul signature: curată
# (sunet, câștig, decalaj față de tăietură)
TR_SFX = {'whip': ('whoosh_s', .8, -.13), 'zoom': ('whoosh_s', .8, -.13), 'zoomout': ('whoosh_s', .7, -.13), 'slide': ('whoosh_s', .7, -.13),
          'spin': ('whoosh', .75, -.21), 'zoomblur': ('whoosh', .8, -.21), 'stretch': ('whoosh_s', .7, -.13), 'wipe': ('whoosh_s', .6, -.1),
          'iris': ('whoosh_s', .55, -.06), 'shape': ('whoosh', .8, -.21), 'circle': ('whoosh_s', .8, -.13), 'blur': ('swish', .6, -.17),
          'lightleak': ('swish', .7, -.17), 'dip': ('swish', .5, -.17), 'glitch': ('glitch', .7, -.03), 'punch': ('impact', .85, 0),
          'flash': ('tick', .7, 0), 'fade': ('swish', .4, -.17)}
def tr_time(kind): return TR_TIME.get(kind, (.12, .2))
BG_POOL = {
    'wheels': ['stripes', 'grid', 'dots'], 'toy': ['dots', 'blobs', 'stripes'], 'baby': ['blobs', 'dots'],
    'decor': ['blobs', 'grid'], 'kitchen': ['grid', 'dots', 'stripes'], 'garden': ['blobs', 'stripes'],
    'gift': ['rays', 'dots', 'blobs'], 'set': ['dots', 'stripes', 'grid'],
}
DIRS = ['L', 'R', 'U', 'D']
DIRV = {'L': (-1, 0), 'R': (1, 0), 'U': (0, -1), 'D': (0, 1)}
DUR = dict(lineup=2.6, combo=2.8, signature=2.2, hook=2.2, feature=1.9, detail=2.1, counter=2.0, split=2.2, grid=2.4, checklist=2.6, final=3.7)

# ------------------------------------------------------------------ utilitare
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def seg(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def lerp(a, b, p): return a + (b - a) * p
def e_out(p): return 1 - (1 - p) ** 3
def e_in(p): return p ** 3
def e_inout(p): return 4 * p ** 3 if p < .5 else 1 - (-2 * p + 2) ** 3 / 2
def e_back(p, s=1.9): c = s + 1; return 1 + c * (p - 1) ** 3 + s * (p - 1) ** 2
def e_elastic(p):
    if p in (0, 1): return p
    return 2 ** (-10 * p) * math.sin((p * 10 - .75) * (2 * math.pi) / 3) + 1

def fix_ro(s):
    return (s or '').replace('ş', 'ș').replace('ţ', 'ț').replace('Ş', 'Ș').replace('Ţ', 'Ț')

def hx(c):
    if isinstance(c, (tuple, list)): return tuple(int(v) for v in c[:3])
    c = c.lstrip('#'); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
def tohex(c): return '#%02x%02x%02x' % tuple(int(clamp(v, 0, 255)) for v in c[:3])
def mix(a, b, t): a, b = hx(a), hx(b); return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))
def lum(c):
    def ch(v):
        v /= 255.0; return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = hx(c); return .2126 * ch(r) + .7152 * ch(g) + .0722 * ch(b)
def contrast(a, b):
    la, lb = lum(a), lum(b); return (max(la, lb) + .05) / (min(la, lb) + .05)
def ensure_contrast(fg, bgs, target=4.6, toward=(0, 0, 0)):
    c = hx(fg)
    for _ in range(40):
        if min(contrast(c, b) for b in bgs) >= target: return c
        c = mix(c, toward, .08)
    return c
def rgba(c, a=255): c = hx(c); return (c[0], c[1], c[2], int(a))

def slug(s): return re.sub(r'[^a-z0-9]+', '-', (s or 'clip').lower())[:40].strip('-') or 'clip'

def fetch(src):
    if os.path.exists(src): return src
    os.makedirs(os.path.join(CACHE, 'img'), exist_ok=True)
    p = os.path.join(CACHE, 'img', hashlib.sha1(src.encode()).hexdigest()[:16] + os.path.splitext(src.split('?')[0])[1][:5])
    if not os.path.exists(p):
        req = urllib.request.Request(src, headers=UA)
        with urllib.request.urlopen(req, timeout=40) as r, open(p, 'wb') as f: f.write(r.read())
    return p

# ------------------------------------------------------------------ fonturi
_font_cache, _font_ok = {}, {}
def font_path(key):
    fn, url, _ = FONTS[key]
    d = os.path.join(CACHE, 'fonts'); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, fn)
    if not os.path.exists(p):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r, open(p, 'wb') as f: f.write(r.read())
        except Exception:
            return None
    return p

def font_has_ro(f):
    nd = bytes(f.getmask('\uffff'))
    for c in 'șțȘȚăâîĂÂÎ':
        m = f.getmask(c)
        if m.getbbox() is None or bytes(m) == nd: return False
    return True

def get_font(key, size):
    size = int(size)
    k = (key, size)
    if k in _font_cache: return _font_cache[k]
    if key not in FONTS: key = FALLBACK_FONT
    p = font_path(key)
    f = None
    if p:
        try:
            f = ImageFont.truetype(p, size)
            wt = FONTS[key][2]
            if wt:
                axes = f.get_variation_axes()
                f.set_variation_by_axes([wt if b'eight' in a['name'] or a['name'] == b'wght' else a['default'] for a in axes])
        except Exception:
            f = None
    if f is None or not _font_ok.setdefault(key, font_has_ro(f)):
        if key != FALLBACK_FONT: return get_font(FALLBACK_FONT, size)
        f = ImageFont.truetype('DejaVuSans-Bold.ttf', size)
    _font_cache[k] = f
    return f

# ------------------------------------------------------------------ imagini
def load_rgb(p):
    im = Image.open(p)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg
    return im.convert('RGB')

def is_white_bg(im):
    a = np.asarray(im).astype(np.int16)
    b = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    return float(((b.min(1) > 232) & (b.max(1) - b.min(1) < 18)).mean()) > .85

def cutout_white(im):
    from scipy import ndimage
    a = np.asarray(im).astype(np.int16)
    near = (a.min(2) > 228) & ((a.max(2) - a.min(2)) < 22)
    lab, n = ndimage.label(near)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    # goluri închise de fundal alb pur (spațiu între piese)
    pure = (a.min(2) > 246) & ((a.max(2) - a.min(2)) < 8)
    lab2, n2 = ndimage.label(pure & ~bg)
    if n2:
        sizes = ndimage.sum(np.ones_like(lab2), lab2, range(1, n2 + 1))
        big = [i + 1 for i, s in enumerate(sizes) if s > near.size * .004]
        if big: bg |= np.isin(lab2, big)
    fgm = ~bg
    fgm = ndimage.binary_opening(fgm, iterations=1)
    alpha = ndimage.gaussian_filter(fgm.astype(np.float32), 1.1)
    alpha = np.clip((alpha - .22) / .66, 0, 1)
    rgb = a.astype(np.float32)
    al = alpha[..., None]
    # scoate halo-ul alb de pe margini
    rgb = np.where(al > .02, (rgb - (1 - al) * 255) / np.maximum(al, .02), rgb)
    # v9: decontaminare — pixelii de margine iau culoarea celui mai apropiat pixel interior (fără franjuri deschise)
    interior = alpha >= .97
    if interior.any():
        _, (iy, ix) = ndimage.distance_transform_edt(~interior, return_indices=True)
        edge = (alpha > .01) & ~interior
        rgb[edge] = a[iy[edge], ix[edge]].astype(np.float32)
    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')

def cutout_rembg(im):
    try:
        from rembg import remove
    except Exception:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'rembg', 'onnxruntime', '--break-system-packages'], check=False)
        from rembg import remove
    return remove(im).convert('RGBA')

def trim(im, pad=4):
    bb = im.getchannel('A').point(lambda v: 255 if v > 12 else 0).getbbox()
    if not bb: return im
    x0, y0, x1, y1 = bb
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))

def rounded_mask(size, r):
    m = Image.new('L', size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255); return m

_logo_src = None
def logo_rgba():
    """v7: logo-ul oficial transparent, decupat la conținut. Fallback: JPG-ul vechi (fundal alb)."""
    global _logo_src
    if _logo_src is None:
        here = os.path.dirname(os.path.abspath(__file__))
        cands = [os.environ.get('HOMIO_LOGO', ''), os.path.join('assets', LOGO_FILE), LOGO_FILE,
                 os.path.join(here, 'assets', LOGO_FILE), os.path.join(here, LOGO_FILE)]
        def _ok(p):
            try:
                with Image.open(p) as _im: _im.verify()
                return True
            except Exception: return False
        src = next((c for c in cands if c and os.path.exists(c) and _ok(c)), None)
        if src is None:
            try: src = fetch(LOGO_GH); src = src if _ok(src) else None
            except Exception: src = None
        if src:
            im = Image.open(src).convert('RGBA'); bb = im.getchannel('A').getbbox()
            _logo_src = (im.crop(bb) if bb else im, True)
        else:
            print('[WARN] logo PNG negăsit (assets/%s) — folosesc JPG-ul vechi' % LOGO_FILE)
            _logo_src = (load_rgb(fetch(LOGO_URL)).convert('RGBA'), False)
    return _logo_src

def logo_fit(w):
    im, transparent = logo_rgba()
    h = max(1, round(im.height * w / im.width))
    return im.resize((int(w), h), Image.LANCZOS), transparent

def logo_badge():
    """Logo-ul fix din colțul stânga-sus: plăcuță crem cu colțuri rotunjite + logo transparent. ~112x106 px."""
    lg, transparent = logo_fit(96)
    if not transparent:
        lg = logo_fit(92)[0]; lg.putalpha(rounded_mask(lg.size, 16).point(lambda v: int(v * .95))); return lg
    pad = 8; w, h = lg.width + 2 * pad, lg.height + 2 * pad
    b = Image.new('RGBA', (w + 16, h + 18), (0, 0, 0, 0))
    sh = Image.new('RGBA', b.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((8, 11, w + 7, h + 10), 18, fill=(60, 35, 10, 60))
    b.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    plate = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(plate).rounded_rectangle((0, 0, w - 1, h - 1), 18, fill=LOGO_PLATE + (245,))
    plate.alpha_composite(lg, (pad, pad)); b.alpha_composite(plate, (8, 8))
    return b

def make_card(im, border=16, r=46):
    w, h = im.size
    card = Image.new('RGBA', (w + 2 * border, h + 2 * border), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), r + border // 2, fill=(255, 255, 255, 255))
    inner = im.convert('RGBA'); inner.putalpha(rounded_mask(im.size, r))
    card.alpha_composite(inner, (border, border))
    return card

def fit_scale(size, box):
    return min(box[0] / size[0], box[1] / size[1])

_soft_cache = {}
def soft_disc(r, color, a=255):
    r = max(2, int(r)); k = (r, hx(color), a)
    if k in _soft_cache: return _soft_cache[k]
    s = 2 * r
    yy, xx = np.mgrid[0:s, 0:s]
    d = np.sqrt((xx - r + .5) ** 2 + (yy - r + .5) ** 2) / r
    al = np.clip(1 - d, 0, 1) ** 1.6 * a
    c = hx(color)
    im = Image.fromarray(np.dstack([np.full((s, s), c[0]), np.full((s, s), c[1]), np.full((s, s), c[2]), al]).astype(np.uint8), 'RGBA')
    if len(_soft_cache) < 400: _soft_cache[k] = im
    return im

def paste(layer, im, x, y):
    x, y = int(round(x)), int(round(y))
    w, h = im.size
    x0, y0, x1, y1 = max(0, x), max(0, y), min(layer.width, x + w), min(layer.height, y + h)
    if x1 <= x0 or y1 <= y0: return
    layer.alpha_composite(im, dest=(x0, y0), source=(x0 - x, y0 - y, x1 - x, y1 - y))

def mul_alpha(im, a):
    if a >= .999: return im
    im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * max(0, a)))); return im

def motion_blur_x(im, px):
    px = int(abs(px))
    if px < 3: return im, 0
    a = np.asarray(im).astype(np.float32)
    al = a[..., 3:4] / 255.0
    pm = np.concatenate([a[..., :3] * al, a[..., 3:4]], 2)
    n = min(14, 2 + px // 5)
    out = np.zeros((a.shape[0], a.shape[1] + px, 4), np.float32)
    for k in range(n):
        s = int(round(px * k / (n - 1)))
        out[:, s:s + a.shape[1]] += pm
    out /= n
    al2 = np.clip(out[..., 3:4], 1e-3, 255) / 255.0
    rgb = np.where(al2 > 1e-3, out[..., :3] / al2, 0)
    res = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), out[..., 3]]).astype(np.uint8), 'RGBA')
    return res, -px // 2

def motion_blur_dir(im, px, dirn='L'):
    """v9: motion blur pe orizontală (L/R) sau verticală (U/D). Întoarce (imagine, ox, oy)."""
    if dirn in ('L', 'R'):
        r, ox = motion_blur_x(im, px); return r, ox, 0
    t = im.transpose(Image.ROTATE_90)
    r, o = motion_blur_x(t, px)
    return r.transpose(Image.ROTATE_270), 0, o

def light_sweep(im, p, strength=.55):
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    pos = (xx + .45 * yy) / (w + .45 * h)
    c = lerp(-.25, 1.25, p)
    band = np.exp(-((pos - c) / .06) ** 2) * strength
    a[..., :3] = a[..., :3] + (255 - a[..., :3]) * band[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')

# ------------------------------------------------------------------ paletă
def extract_palette(sprites):
    from sklearn.cluster import KMeans
    px = []
    for i, s in enumerate(sprites):
        a = np.asarray(s.convert('RGBA').resize((160, int(160 * s.height / max(1, s.width)) or 1)))
        m = a[..., 3] > 200
        p = a[..., :3][m]
        if len(p): px.append(np.repeat(p, 3 if i == 0 else 1, 0))
    px = np.concatenate(px) if px else np.array([[200, 80, 80]])
    sel = px[(px.max(1) < 245) | (px.min(1) < 200)]
    if len(sel) > 200: px = sel
    if len(px) > 20000: px = px[np.random.RandomState(1).choice(len(px), 20000, replace=False)]
    k = min(5, max(1, len(np.unique(px, axis=0))))
    km = KMeans(k, n_init=4, random_state=0).fit(px)
    counts = np.bincount(km.labels_, minlength=k)
    cols = []
    for i in np.argsort(-counts):
        c = km.cluster_centers_[i]
        h, s, v = colorsys.rgb_to_hsv(*(c / 255))
        cols.append(dict(rgb=tuple(int(x) for x in c), share=float(counts[i] / counts.sum()), h=h, s=s, v=v))
    sat = [c for c in cols if c['s'] > .28 and .2 < c['v'] < .97]
    dom = sat[0] if sat else cols[0]
    acc = None
    for c in sorted(sat, key=lambda c: -c['s'] * c['share'] ** .3):
        dh = min(abs(c['h'] - dom['h']), 1 - abs(c['h'] - dom['h']))
        if dh > .1: acc = c; break
    if acc is None:
        h = (dom['h'] + .5) % 1
        acc = dict(rgb=tuple(int(v * 255) for v in colorsys.hsv_to_rgb(h, .7, .75)))
    return dict(colors=[c['rgb'] for c in cols], base=dom['rgb'], accent=acc['rgb'])

def build_theme(pal, recipe, override):
    base = hx(override.get('base', pal['base'])); acc = hx(override.get('accent', pal['accent']))
    kind = recipe.get('theme', 'light')
    dark = override.get('dark', kind == 'dark')
    th = dict(dark=dark)
    if dark:
        th['bg_top'] = mix(base, (8, 10, 16), .82); th['bg_bot'] = mix(base, (8, 10, 16), .9)
        th['text'] = (250, 247, 240)
        th['accent'] = ensure_contrast(mix(acc, (255, 255, 255), .25), [th['bg_top'], th['bg_bot']], toward=(255, 255, 255))
    else:
        t1, t2 = (.86, .72) if kind != 'pastel' else (.9, .8)
        th['bg_top'] = mix(base, (255, 255, 255), t1); th['bg_bot'] = mix(base, (255, 255, 255), t2)
        th['text'] = ensure_contrast(mix(base, (14, 16, 26), .86), [th['bg_top'], th['bg_bot']], 7)
        th['accent'] = ensure_contrast(acc, [th['bg_top'], th['bg_bot'], mix(acc, th['bg_top'], .5)])
    th['accent_soft'] = mix(th['accent'], th['bg_top'], .6) if not dark else mix(acc, th['bg_top'], .6)
    th['pill'] = ensure_contrast(mix(base, (20, 20, 30), .35) if not dark else mix(acc, (0, 0, 0), .2), [(255, 255, 255)], 4.8)
    th['pill_text'] = (255, 255, 255)
    th['blobs'] = [mix(c, th['bg_top'], .55 if not dark else .75) for c in [base, acc] + [hx(c) for c in pal['colors'][:3]]]
    th['fx'] = [hx(c) for c in pal['colors'][:4]] + [acc, base]
    th['dust'] = mix(th['bg_bot'], th['text'], .22) if not dark else (200, 200, 210)
    th['base'], th['acc_raw'] = base, acc
    return th

# ------------------------------------------------------------------ fundal
class Background:
    def __init__(self, th, kind, season, rng, edit=None):
        self.th, self.kind, self.season = th, kind, season
        self.edit = edit or {}
        g = np.linspace(0, 1, H)[:, None, None]
        a, b = np.array(th['bg_top'], np.float32), np.array(th['bg_bot'], np.float32)
        base = (a * (1 - g) + b * g).repeat(W, 1)
        self.base = Image.fromarray(base.astype(np.uint8), 'RGB').convert('RGBA')
        M = 260
        self.M = M
        lay = Image.new('RGBA', (W + 2 * M, H + 2 * M), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        lc = mix(th['bg_top'], th['text'], .07 if not th['dark'] else .12)
        if kind == 'dots':
            for y in range(0, lay.height, 70):
                for x in range((y // 70) % 2 * 35, lay.width, 70):
                    d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=rgba(lc, 150))
        elif kind == 'grid':
            for x in range(0, lay.width, 90): d.line((x, 0, x, lay.height), fill=rgba(lc, 110), width=2)
            for y in range(0, lay.height, 90): d.line((0, y, lay.width, y), fill=rgba(lc, 110), width=2)
        elif kind == 'stripes':
            for x in range(-lay.height, lay.width, 120):
                d.line((x, lay.height, x + lay.height * .45, 0), fill=rgba(lc, 90), width=34)
        for i in range(5):
            c = th['blobs'][i % len(th['blobs'])]
            r = rng.randint(260, 460)
            x, y = rng.randint(0, lay.width), rng.randint(0, lay.height)
            lay.alpha_composite(soft_disc(r, c, 170), (x - r, y - r))
        self.lay = lay
        # v9: strat îndepărtat (blobs mari, estompate) care se mișcă invers => adâncime
        self.M2 = 320
        far = Image.new('RGBA', (W + 2 * self.M2, H + 2 * self.M2), (0, 0, 0, 0))
        for i in range(4):
            c = mix(th['blobs'][(i + 1) % len(th['blobs'])], th['bg_top'], .35)
            r = rng.randint(420, 700)
            x, y = rng.randint(0, far.width), rng.randint(0, far.height)
            far.alpha_composite(soft_disc(r, c, 120), (x - r, y - r))
        self.far = far
        self.rays = None
        if kind == 'rays':
            R = 1500
            ry = Image.new('RGBA', (2 * R, 2 * R), (0, 0, 0, 0)); dr = ImageDraw.Draw(ry)
            for k in range(18):
                a0 = k * 20
                dr.pieslice((0, 0, 2 * R, 2 * R), a0, a0 + 10, fill=rgba(mix(th['bg_top'], (255, 255, 255), .6), 90))
            self.rays = ry.resize((R, R), Image.BILINEAR)
        self.flakes = [(rng.random(), rng.random(), rng.uniform(.6, 1.4), rng.random()) for _ in range(45)] if season else []

    def frame(self, t, par=0.0):
        f = self.base.copy()
        if self.rays is not None:
            r = self.rays.rotate(t * 8, resample=Image.BILINEAR)
            paste(f, r, W / 2 - r.width / 2, H * .42 - r.height / 2)
        e = self.edit
        vx, vy = e.get('bg_vx', 0.0), e.get('bg_vy', -10.0); ph = e.get('bg_phase', 0.0)
        ox = self.M + math.sin(t * .5 + ph) * 55 + t * vx + par
        oy = self.M + math.cos(t * .4 + ph) * 45 + t * vy
        ox = clamp(ox, 0, 2 * self.M); oy = clamp(oy, 0, 2 * self.M)
        # strat îndepărtat: sens opus, mai lent
        fx2 = clamp(self.M2 - (ox - self.M) * .55, 0, 2 * self.M2); fy2 = clamp(self.M2 - (oy - self.M) * .55, 0, 2 * self.M2)
        f.alpha_composite(self.far, (0, 0), (int(fx2), int(fy2), int(fx2) + W, int(fy2) + H))
        f.alpha_composite(self.lay, (0, 0), (int(ox), int(oy), int(ox) + W, int(oy) + H))
        if self.season:
            d = ImageDraw.Draw(f)
            for (x0, y0, sp, ph) in self.flakes:
                y = ((y0 + t * .06 * sp) % 1.1 - .05) * H
                x = x0 * W + math.sin(t * 1.3 * sp + ph * 6) * 30
                if self.season == 'winter':
                    r = 5 * sp; d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 210))
                elif self.season == 'autumn':
                    c = [(214, 120, 40), (190, 70, 40), (230, 170, 60)][int(ph * 3) % 3]
                    ang = t * 2 * sp + ph * 6
                    pts = [(x + math.cos(ang + k * math.pi / 2) * (14 if k % 2 == 0 else 6) * sp,
                            y + math.sin(ang + k * math.pi / 2) * (14 if k % 2 == 0 else 6) * sp) for k in range(4)]
                    d.polygon(pts, fill=c + (220,))
                elif self.season == 'spring':
                    r = 7 * sp; d.ellipse((x - r, y - r * .6, x + r, y + r * .6), fill=(255, 190, 210, 200))
                else:
                    r = 3 + 3 * sp * abs(math.sin(t * 2 + ph * 9)); d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 245, 200, 170))
        return f

# ------------------------------------------------------------------ text
class TextBlock:
    def __init__(self, ctx, text, key, size, cx, y, maxw=TEXT_MAXW, color=None, accent='', accent_style='marker',
                 min_size=44, max_lines=3, align='center', name='text'):
        text = fix_ro(text).strip()
        self.ctx, self.key = ctx, key
        acc = set(w.strip('.,!?:;„”"').lower() for w in fix_ro(accent).split())
        while True:
            f = get_font(key, size)
            lines = self._wrap(text, f, maxw)
            wmax = max(f.getlength(' '.join(l)) for l in lines)
            if (wmax <= maxw and len(lines) <= max_lines) or size <= min_size: break
            size -= 3
        self.size, self.font = size, f
        asc, desc = f.getmetrics()
        self.lh = int(size * 1.16)
        self.words = []
        sp = f.getlength(' ')
        for li, l in enumerate(lines):
            lw = f.getlength(' '.join(l))
            x = cx - lw / 2 if align == 'center' else cx
            for w in l:
                ww = f.getlength(w)
                self.words.append(dict(w=w, x=x, y=y + li * self.lh, ww=ww, acc=w.strip('.,!?:;„”"').lower() in acc))
                x += ww + sp
        self.h = len(lines) * self.lh
        self.color = color or ctx.th['text']
        self.accent_style = accent_style
        xs = [w['x'] for w in self.words]; xe = [w['x'] + w['ww'] for w in self.words]
        self.bbox = (min(xs), y + int(size * .12), max(xe), y + self.h)
        self.text = text
        ctx.qa_text(name, self.bbox, text)

    @staticmethod
    def _wrap(text, f, maxw):
        lines = []
        for para in text.split('\n'):
            cur = []
            for w in para.split():
                if cur and f.getlength(' '.join(cur + [w])) > maxw: lines.append(cur); cur = [w]
                else: cur.append(w)
            if cur: lines.append(cur)
        return lines or [['']]

    def word_img(self, w, color):
        k = ('w', w, self.key, self.size, color)
        c = self.ctx.cache
        if k not in c:
            f = self.font; asc, desc = f.getmetrics()
            im = Image.new('RGBA', (int(f.getlength(w)) + 24, asc + desc + 16), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((12, 6), w, font=f, fill=rgba(color))
            c[k] = im
        return c[k]

    def draw(self, layer, t, anim='pop', start=0.0, stagger=.07, dur=.28, marker_at=None, out=None):
        """anim: none|pop|kinetic|slide|fade|rise. out=(t0,t1) animă ieșirea."""
        th = self.ctx.th
        d = ImageDraw.Draw(layer)
        oa = 1.0
        if out: oa = 1 - seg(t, out[0], out[1])
        if oa <= 0: return
        for i, wd in enumerate(self.words):
            st = start + (i * stagger if anim in ('kinetic', 'pop', 'rise') else 0)
            p = 1.0 if anim == 'none' else seg(t, st, st + dur)
            if p <= 0: continue
            col = th['accent'] if wd['acc'] else self.color
            if wd['acc'] and self.accent_style == 'marker' and not th['dark']:
                mp = 1.0 if marker_at is None else e_out(seg(t, marker_at, marker_at + .3))
                if mp > 0:
                    x0 = wd['x'] - 10; y0 = wd['y'] + self.size * .52
                    d.rounded_rectangle((x0, y0, x0 + (wd['ww'] + 20) * mp, wd['y'] + self.size * 1.12), 10,
                                        fill=rgba(th['accent_soft'], 255 * oa))
            im = self.word_img(wd['w'], col)
            if anim in ('pop', 'kinetic'):
                s = e_back(p) if anim == 'pop' else lerp(.6, 1, e_back(p)); a = min(1, p * 2.5)
                dy = 0 if anim == 'pop' else (1 - e_out(p)) * 40
            elif anim == 'rise':
                s = 1; a = p; dy = (1 - e_out(p)) * 60
            elif anim == 'slide':
                s = 1; a = min(1, p * 2); dy = 0
            elif anim == 'fade':
                s = 1; a = p; dy = 0
            else:
                s, a, dy = 1, 1, 0
            a *= oa
            x = wd['x'] - 12 + (1 - e_out(p)) * (-120 if anim == 'slide' else 0)
            y = wd['y'] - 6 + dy
            if abs(s - 1) > .01:
                im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
                x += (im.width - im2.width) / 2; y += (im.height - im2.height) / 2
            else:
                im2 = im
            paste(layer, mul_alpha(im2, a), x, y)

def draw_pill(ctx, layer, text, cx, y, p=1.0, size=46, fill=None, fg=None, name='pill', register=True, key=None):
    text = fix_ro(text)
    f = get_font(key or ctx.body_font, size)
    tw = f.getlength(text); asc, desc = f.getmetrics()
    w, h = int(tw + 64), int(size * 1.7)
    if register: ctx.qa_text(name, (cx - w / 2, y, cx + w / 2, y + h), text)
    if p <= 0: return (cx - w / 2, y, cx + w / 2, y + h)
    k = ('pill', text, size, fill, fg, key)
    if k not in ctx.cache:
        im = Image.new('RGBA', (w + 4, h + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((2, 2, w + 1, h + 1), h // 2, fill=rgba(fill or ctx.th['pill']))
        d.text((w / 2 + 2, h / 2 + 2), text, font=f, fill=rgba(fg or ctx.th['pill_text']), anchor='mm')
        ctx.cache[k] = im
    im = ctx.cache[k]
    s = e_back(clamp(p))
    if s < .999:
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    paste(layer, mul_alpha(im, min(1, p * 2)), cx - im.width / 2, y + h / 2 - im.height / 2)
    return (cx - w / 2, y, cx + w / 2, y + h)

# ------------------------------------------------------------------ particule / grafică
def fx_speedlines(layer, t, color, rng_seed=3, n=26, y0=500, y1=1550, speed=2600, alpha=150, direction=1):
    d = ImageDraw.Draw(layer); r = random.Random(rng_seed)
    for i in range(n):
        y = r.uniform(y0, y1); L = r.uniform(120, 380); wd = r.choice([3, 4, 6, 8]); ph = r.random()
        x = ((ph * (W + 800) - direction * speed * t * r.uniform(.7, 1.3)) % (W + 800)) - 400
        d.line((x, y, x + L, y), fill=rgba(color, alpha * r.uniform(.5, 1)), width=wd)

def fx_dust(layer, t, x, y, color, n=16, spread=260, seed=5, size=1.0):
    if t < 0 or t > 1.1: return
    r = random.Random(seed)
    for i in range(n):
        ang = r.uniform(-math.pi, 0); side = 1 if math.cos(ang) >= 0 else -1
        dist = e_out(clamp(t / .9)) * spread * r.uniform(.4, 1.1)
        px = x + math.cos(ang) * dist * 1.4 + side * 20; py = y + math.sin(ang) * dist * .35 - t * 30 * r.random()
        rad = (30 + 70 * e_out(clamp(t / .8))) * r.uniform(.6, 1.2) * size
        a = int(245 * (1 - clamp(t / 1.1)) ** 1.1)
        disc = soft_disc(rad, color, a)
        paste(layer, disc, px - rad, py - rad)

def fx_burst(layer, t, cx, cy, color, n=12, r0=120, r1=300, width=10, seed=1):
    if t < 0 or t > .45: return
    d = ImageDraw.Draw(layer); p = t / .45
    for i in range(n):
        a = i / n * 2 * math.pi + seed
        s = r0 + (r1 - r0) * e_out(p); e = r0 + (r1 - r0) * e_out(clamp(p * 1.6))
        s = r0 + (r1 - r0) * e_out(clamp(p * 1.6 - .6)) if p > .375 else r0
        d.line((cx + math.cos(a) * s, cy + math.sin(a) * s, cx + math.cos(a) * e, cy + math.sin(a) * e),
               fill=rgba(color, 255 * (1 - p * .6)), width=width)

def fx_confetti(layer, t, colors, n=90, seed=7, cx=W / 2, cy=H * .55, power=1.0):
    if t < 0 or t > 3: return
    d = ImageDraw.Draw(layer); r = random.Random(seed)
    for i in range(n):
        ang = r.uniform(-math.pi * .95, -math.pi * .05); v = r.uniform(900, 2200) * power
        vx, vy = math.cos(ang) * v, math.sin(ang) * v
        x = cx + vx * t * .55; y = cy + vy * t * .55 + 1500 * t * t * .5 - 200 * t
        x += math.sin(t * 6 + i) * 20
        if y > H + 40 or x < -40 or x > W + 40: continue
        rot = t * r.uniform(4, 12) + i; s = r.uniform(10, 20); c = colors[i % len(colors)]
        sx = abs(math.cos(rot)) * s + 2
        pts = [(x + math.cos(rot * .7) * dx - math.sin(rot * .7) * dy, y + math.sin(rot * .7) * dx + math.cos(rot * .7) * dy)
               for dx, dy in ((-sx, -s * .45), (sx, -s * .45), (sx, s * .45), (-sx, s * .45))]
        d.polygon(pts, fill=rgba(c, 255 * (1 - clamp((t - 2.3) / .7))))

def star_pts(x, y, r, n=4, inner=.38, rot=0):
    pts = []
    for k in range(n * 2):
        rr = r if k % 2 == 0 else r * inner; a = rot + k * math.pi / n
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    return pts

def fx_sparkles(layer, t, pts, color, size=26):
    d = ImageDraw.Draw(layer)
    for i, (x, y) in enumerate(pts):
        s = abs(math.sin(t * 3.2 + i * 1.7)) ** 2 * size
        if s > 2: d.polygon(star_pts(x, y, s, 4, .3, t * .5 + i), fill=rgba(color, 235))

def fx_ring(layer, p, cx, cy, r, color, width=10):
    if p <= 0: return
    d = ImageDraw.Draw(layer)
    d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * e_out(p), fill=rgba(color), width=width)

def fx_arrow(layer, p, x0, y0, x1, y1, color, width=9):
    if p <= 0: return
    d = ImageDraw.Draw(layer); q = e_out(p)
    xe, ye = lerp(x0, x1, q), lerp(y0, y1, q)
    d.line((x0, y0, xe, ye), fill=rgba(color), width=width)
    if p > .7:
        a = math.atan2(ye - y0, xe - x0); L = 34
        for s in (-1, 1):
            d.line((xe, ye, xe - math.cos(a + s * .5) * L, ye - math.sin(a + s * .5) * L), fill=rgba(color), width=width)

def sticker(kind, color, size=120):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = size / 2
    if kind == 'star': d.polygon(star_pts(c, c, size * .46, 5, .45, -math.pi / 2), fill=rgba(color))
    elif kind == 'circle': d.ellipse((size * .2, size * .2, size * .8, size * .8), fill=rgba(color))
    elif kind == 'ring': d.ellipse((size * .15, size * .15, size * .85, size * .85), outline=rgba(color), width=int(size * .1))
    elif kind == 'plus':
        w = size * .14; d.rounded_rectangle((c - w, size * .15, c + w, size * .85), 8, fill=rgba(color)); d.rounded_rectangle((size * .15, c - w, size * .85, c + w), 8, fill=rgba(color))
    elif kind == 'squiggle':
        pts = [(size * .08 + k * size * .84 / 20, c + math.sin(k / 20 * 3 * math.pi) * size * .18) for k in range(21)]
        d.line(pts, fill=rgba(color), width=int(size * .1), joint='curve')
    elif kind == 'spark': d.polygon(star_pts(c, c, size * .46, 4, .3, 0), fill=rgba(color))
    return im

# ------------------------------------------------------------------ context
class Ctx:
    def __init__(self, cfg, out, rec):
        self.cfg, self.out, self.rec = cfg, out, rec
        self.cache, self.texts, self.sfx_events, self.effects = {}, [], [], set()
        self.qa_enabled = True
        self.title_font, self.body_font = rec['font_title'], rec['font_body']
        self.frame0_boxes = []
        self.edit = {}

    def qa_text(self, name, bbox, text):
        if self.qa_enabled: self.texts.append(dict(name=name, bbox=[round(v) for v in bbox], text=text))

    def sfx(self, t, kind, gain=1.0): self.sfx_events.append((t, kind, gain))

    # --- produs
    def sprite(self, idx):
        if idx == 'group': idx = getattr(self, 'group_idx', 0)
        idx = int(idx) % len(self.sprites); return self.sprites[idx]

    def draw_product(self, layer, idx, cx, gy, box=(860, 860), s=1.0, rot=0.0, alpha=1.0, blur=0.0, lift=0.0,
                     sweep=None, sx=1.0, sy=1.0, shadow=True, mask_r=None):
        sp = self.sprite(idx)
        im0 = sp['img']
        base = fit_scale((im0.width / HI, im0.height / HI), box) / HI
        sc = base * s
        k = ('prod', idx, round(sc * sx, 3), round(sc * sy, 3))
        if k in self.cache: im = self.cache[k]
        else:
            im = im0.resize((max(1, int(im0.width * sc * sx)), max(1, int(im0.height * sc * sy))), Image.BICUBIC)
            if len(self.cache) < 900: self.cache[k] = im
        if sweep is not None and 0 <= sweep <= 1: im = light_sweep(im, sweep)
        if abs(rot) > .05: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
        ox = 0
        if blur: im, ox = motion_blur_x(im, blur)
        w, h = im.size
        x, y = cx - w / 2 + ox, gy - h - lift
        if shadow and sp['kind'] != 'card':
            sw = im0.width * sc * .9 * (1 - clamp(lift / 600) * .45)
            sh_im = self.shadow_img(int(sw))
            paste(layer, mul_alpha(sh_im, alpha * (1 - clamp(lift / 700) * .7)), cx - sh_im.width / 2, gy - sh_im.height / 2)
        refl = getattr(self, 'edit', {}).get('reflect', 0.0)
        if refl > 0 and sp['kind'] != 'card' and lift < 40 and alpha > .3 and abs(rot) < 12:
            rh = int(min(h * .20, 170))
            if rh > 20:
                flip = im.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, w, rh))
                grad = np.linspace(1, 0, rh)[:, None] ** 1.6
                ra = (np.asarray(flip.getchannel('A')).astype(np.float32) * grad * refl * alpha)
                flip = flip.copy(); flip.putalpha(Image.fromarray(np.clip(ra, 0, 255).astype(np.uint8)))
                paste(layer, flip, x, y + h + 3)
        if mask_r is not None:
            tmp = Image.new('RGBA', layer.size, (0, 0, 0, 0)); paste(tmp, mul_alpha(im, alpha), x, y)
            m = Image.new('L', layer.size, 0); ImageDraw.Draw(m).ellipse((cx - mask_r, gy - h / 2 - mask_r, cx + mask_r, gy - h / 2 + mask_r), fill=255)
            a = np.minimum(np.asarray(tmp.getchannel('A')), np.asarray(m)); tmp.putalpha(Image.fromarray(a))
            layer.alpha_composite(tmp)
        else:
            paste(layer, mul_alpha(im, alpha), x, y)
        return (x, y, x + w, y + h)

    def shadow_img(self, w):
        w = max(40, int(w // 8 * 8)); k = ('shadow', w)
        if k not in self.cache:
            h = max(20, int(w * .09)); pad = 40
            im = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
            c = mix(self.th['bg_bot'], (0, 0, 0), .55)
            ImageDraw.Draw(im).ellipse((pad, pad, pad + w, pad + h), fill=rgba(c, 120))
            self.cache[k] = im.filter(ImageFilter.GaussianBlur(18))
        return self.cache[k]

    def prod_size(self, idx, box):
        im0 = self.sprite(idx)['img']; b = fit_scale((im0.width / HI, im0.height / HI), box)
        return im0.width / HI * b, im0.height / HI * b

# ------------------------------------------------------------------ scene
class Scene:
    kind = 'scene'
    def __init__(self, ctx, spec, dur):
        self.ctx, self.spec, self.dur = ctx, spec, dur
        self.tin = spec.get('tin', 'cut'); self.tdir = spec.get('tdir', 'L'); self.t0 = 0
        self.setup()
    def setup(self): pass
    def events(self): return []
    def render(self, fg, t): return {}
    def idle(self, t, amp=10): return math.sin(t * 2 * math.pi / 2.4) * amp, math.sin(t * 2 * math.pi / 3.3) * 1.3

class HookScene(Scene):
    kind = 'hook'
    def setup(self):
        c, s, th = self.ctx, self.spec, self.ctx.th
        self.style = s.get('style', 'pop'); self.img = s.get('image', 0)
        self.tb = TextBlock(c, s['text'], c.title_font, s.get('size', 104), CX_TEXT, 205, accent=s.get('accent', ''),
                            max_lines=3, name='hook', min_size=80)
        self.gy = 1390 if s.get('badges') else 1480
        top = self.tb.bbox[3] + 50
        self.box = (840, self.gy - top)
        self.badges = [fix_ro(b) for b in s.get('badges', [])][:3]
        c.effects.add('hook:' + self.style)
        if self.style == 'gift':
            self.gift_colors = (hx(s['gift_box']) if s.get('gift_box') else th['acc_raw'],
                                hx(s['gift_ribbon']) if s.get('gift_ribbon') else mix(th['base'], (255, 255, 255), .3))
        if c.rec.get('stickers'):
            r = random.Random(11); cols = th['fx']
            kinds = ['star', 'circle', 'plus', 'squiggle', 'ring', 'spark']
            self.stk = []
            pos = [(130, 700), (950, 760), (120, 1180), (960, 1250), (200, 950), (900, 1010)]
            for i, (x, y) in enumerate(pos):
                self.stk.append((sticker(kinds[i % 6], cols[i % len(cols)], r.randint(90, 130)), x, y, r.uniform(-1, 1)))
            c.effects.add('stickers')

    def events(self):
        st = self.style
        ev = {'speed': [(.1, 'whoosh'), (.78, 'impact')], 'pop': [(.08, 'pop'), (.62, 'impact'), (.75, 'pop')],
              'slam': [(.12, 'whoosh'), (.45, 'impact')], 'gift': [(.32, 'pop'), (.95, 'pop'), (1.0, 'impact'), (1.1, 'sparkle'), (2.1, 'whoosh_s')],
              'gentle': [(.3, 'sparkle')], 'pan': [(.1, 'whoosh')]}.get(st, [])
        if self.badges: ev.append((1.25, 'pop'))
        return ev

    def render(self, fg, t):
        c, th = self.ctx, self.ctx.th
        st = self.style; res = {}
        cx, gy = 540, self.gy
        s, rot, blur, lift, alpha, sweep, sx, sy = 1, 0, 0, 0, 1, None, 1, 1
        fy, fr = self.idle(t, 8)
        pw, ph = c.prod_size(self.img, self.box)
        if st == 'speed':
            if c.rec.get('speedlines'):
                fx_speedlines(fg, t, mix(th['text'], th['bg_top'], .55), n=24, alpha=160 * (1 - seg(t, 1.2, 1.8)) if t > .08 else 0)
                c.effects.add('speedlines')
            if t < .1: pass
            elif t < .3:
                p = e_in(seg(t, .1, .3)); cx = 540 + p * 1100; blur = p * 160
            elif t < .78:
                p = e_out(seg(t, .3, .78)); cx = -700 + p * 1280; blur = (1 - p) * 180 + 10; rot = -4 * (1 - p)
            else:
                p = seg(t, .78, 1.3); cx = 580 - 40 * e_back(p); rot = 7 * math.sin(p * math.pi) * (1 - p)
                cx += 0 if p < 1 else 0
            if t >= .78:
                fx_dust(fg, t - .78, cx - pw * .38, gy, th['dust'], seed=3); fx_dust(fg, t - .78, cx + pw * .35, gy, th['dust'], seed=8, size=.8)
                res['shake'] = 26 * (1 - seg(t, .78, 1.15)) if t < 1.15 else 0
                c.effects.update(['dust', 'shake', 'motion_blur'])
            if t > 1.3: lift = -fy * .0 + max(0, fy); rot = fr
        elif st == 'pop':
            if t < .08: pass
            elif t < .22:
                p = seg(t, .08, .22); sx, sy = 1 + .1 * p, 1 - .12 * p
            elif t < .62:
                p = seg(t, .22, .62); lift = math.sin(p * math.pi) * 230; sx, sy = 1 - .05 * math.sin(p * math.pi), 1 + .06 * math.sin(p * math.pi); rot = 8 * math.sin(p * math.pi * 2)
            elif t < .9:
                p = seg(t, .62, .9); b = math.sin(p * math.pi * 2) * (1 - p); sx, sy = 1 + .1 * b, 1 - .1 * b
            else:
                lift = max(0, fy); rot = fr
            if t >= .62:
                fx_burst(fg, t - .62, cx, gy - ph * .5, th['accent'], r0=ph * .45, r1=ph * .65, width=12)
                res['shake'] = 14 * (1 - seg(t, .62, .85)) if c.rec.get('shake') and t < .85 else 0
                c.effects.add('burst')
        elif st == 'slam':
            if t < .12: pass
            elif t < .35:
                p = e_out(seg(t, .12, .35)); lift = p * 200; s = 1 + .06 * p; rot = -3 * p
            elif t < .45:
                p = e_in(seg(t, .35, .45)); lift = 200 * (1 - p); s = 1.06 - .06 * p; rot = -3 * (1 - p)
            else:
                p = seg(t, .45, .75); b = math.sin(p * math.pi * 2) * (1 - p); sx, sy = 1 + .06 * b, 1 - .06 * b
                if t > .9: lift = max(0, fy); rot = fr
            if t >= .45:
                fx_dust(fg, t - .45, cx, gy, th['dust'], n=18, spread=360, seed=4)
                fx_burst(fg, t - .45, cx, gy - ph * .45, th['accent'], r0=ph * .5, r1=ph * .7)
                res['shake'] = 22 * (1 - seg(t, .45, .8)) if t < .8 else 0
                c.effects.update(['dust', 'shake', 'burst'])
        elif st == 'gentle':
            s = 1 + .07 * e_inout(seg(t, 0, self.dur)); lift = max(0, fy * .6); rot = fr * .5
            sweep = seg(t, .35, 1.4) if c.rec.get('sweep') else None
            fx_sparkles(fg, t, [(cx - pw * .45, gy - ph * .8), (cx + pw * .42, gy - ph * .6), (cx + pw * .3, gy - ph * .15)], (255, 255, 255))
            c.effects.update(['pushin', 'sparkles'] + (['light_sweep'] if sweep is not None else []))
        elif st == 'pan':
            cx = 540 + lerp(-40, 40, e_inout(seg(t, 0, self.dur))); res['par'] = -t * 60; lift = max(0, fy * .5)
            c.effects.update(['pan', 'parallax'])
        elif st == 'gift':
            res.update(self.render_gift(fg, t, cx, gy))
            c.effects.update(['gift_box', 'lid_pop', 'reveal_from_box', 'confetti'])
        if c.rec.get('stickers') and hasattr(self, 'stk') and st != 'gift':
            for i, (im, x, y, sp) in enumerate(self.stk):
                p = 1.0 if i < 2 else e_back(seg(t, .5 + i * .08, .8 + i * .08))
                if p <= 0: continue
                im2 = im.rotate(t * 25 * sp, resample=Image.BICUBIC, expand=True)
                if p < .999: im2 = im2.resize((max(1, int(im2.width * p)), max(1, int(im2.height * p))))
                paste(fg, im2, x - im2.width / 2, y - im2.height / 2 + math.sin(t * 2 + i) * 10)
        if st == 'gift':
            bb = self.gift_bb
        else:
            bb = c.draw_product(fg, self.img, cx, gy, self.box, s, rot, alpha, blur, lift, sweep, sx, sy)
        if t == 0: c.frame0_boxes.append(('produs', bb))
        self.tb.draw(fg, t, anim='none', marker_at=.55 if st != 'gentle' else .4)
        if t == 0: c.frame0_boxes.append(('hook', self.tb.bbox))
        # pastile
        if self.badges:
            f = get_font(c.body_font, 46)
            widths = [f.getlength(b) + 64 for b in self.badges]; gap = 20
            x = CX_TEXT - (sum(widths) + gap * (len(widths) - 1)) / 2
            for i, b in enumerate(self.badges):
                draw_pill(c, fg, b, x + widths[i] / 2, gy + 60, seg(t, 1.1 + i * .12, 1.4 + i * .12), 46, name='badge', register=(t == 0))
                x += widths[i] + gap
        return res

    # ---- v6: cutie cadou cu deschidere și ieșirea produsului din cutie
    def _box_parts(self):
        if hasattr(self, '_bp'): return self._bp
        bc, rc = self.gift_colors
        dk = mix(bc, (0, 0, 0), .22); lt = mix(bc, (255, 255, 255), .18)
        BW, BH, LH = 600, 360, 110            # corp, înălțime corp, înălțime capac
        LW = BW + 44
        # corp (față): gradient vertical + umbrire pe margini + panglică, totul mascat rotunjit
        yy, xx = np.mgrid[0:BH, 0:BW]
        g = (yy / BH)[..., None]
        top_c = np.array(mix(bc, (255, 255, 255), .10), float); bot_c = np.array(mix(bc, (0, 0, 0), .18), float)
        col = top_c * (1 - g) + bot_c * g
        edge = np.minimum(xx, BW - 1 - xx) / 70.0
        col = col * (0.82 + 0.18 * np.clip(edge, 0, 1))[..., None]
        arr = np.dstack([col, np.full((BH, BW), 255.0)]).astype(np.uint8)
        body = Image.fromarray(arr, 'RGBA')
        rib = Image.new('RGBA', (BW, BH), (0, 0, 0, 0)); rd = ImageDraw.Draw(rib)
        rd.rectangle((BW // 2 - 42, 0, BW // 2 + 42, BH), fill=rgba(rc))
        rd.rectangle((BW // 2 - 42, 0, BW // 2 - 32, BH), fill=rgba(mix(rc, (0, 0, 0), .10)))
        rd.rectangle((BW // 2 + 32, 0, BW // 2 + 42, BH), fill=rgba(mix(rc, (0, 0, 0), .10)))
        rd.rounded_rectangle((30, 26, 44, BH - 80), 7, fill=(255, 255, 255, 70))
        body.alpha_composite(rib)
        m = Image.new('L', (BW, BH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, BW - 1, BH - 1), 28, fill=255)
        body.putalpha(m)
        # interior (gura cutiei, vedere de sus)
        mouth = Image.new('RGBA', (BW - 20, 70), (0, 0, 0, 0)); md = ImageDraw.Draw(mouth)
        md.ellipse((0, 0, BW - 21, 69), fill=rgba(mix(bc, (0, 0, 0), .62)))
        # capac cu fundă
        lid = Image.new('RGBA', (LW, LH + 150), (0, 0, 0, 0)); ld = ImageDraw.Draw(lid)
        ly = 150
        ld.rounded_rectangle((0, ly, LW - 1, ly + LH - 1), 24, fill=rgba(lt))
        ld.rectangle((0, ly + LH - 26, LW, ly + LH - 1), fill=rgba(dk, 60))
        ld.rectangle((LW // 2 - 42, ly, LW // 2 + 42, ly + LH), fill=rgba(rc))
        m = LW // 2
        for sgn in (-1, 1):   # două bucle de fundă
            x0 = m - 190 if sgn < 0 else m + 12
            ld.ellipse((x0, 6, x0 + 178, ly + 26), outline=rgba(rc), width=30)
            ld.ellipse((x0 + 34, 40, x0 + 144, ly + 6), outline=rgba(mix(rc, (0, 0, 0), .1), 90), width=8)
        ld.ellipse((m - 34, ly - 40, m + 34, ly + 26), fill=rgba(mix(rc, (0, 0, 0), .08)))
        self._bp = dict(body=body, mouth=mouth, lid=lid, BW=BW, BH=BH, LH=LH, LW=LW, ly=ly, rc=rc, bc=bc)
        return self._bp

    def _glow(self, r):
        k = ('glow', r // 8)
        c = self.ctx
        if k not in c.cache:
            n = 256; yy, xx = np.mgrid[0:n, 0:n]; dd = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (n / 2)
            a = np.clip(1 - dd, 0, 1) ** 1.8
            im = np.zeros((n, n, 4), np.uint8); im[..., :3] = 255; im[..., 3] = (a * 255).astype(np.uint8)
            c.cache[k] = Image.fromarray(im, 'RGBA').resize((int(r * 2), int(r * 2)), Image.BICUBIC)
        return c.cache[k]

    def render_gift(self, fg, t, cx, gy):
        c, th = self.ctx, self.ctx.th
        P = self._box_parts(); BW, BH, LH, LW, ly = P['BW'], P['BH'], P['LH'], P['LW'], P['ly']
        pw, ph = c.prod_size(self.img, self.box)
        top = self.tb.bbox[3] + 50
        base_y0 = (top + gy) / 2 + BH * .5 + LH * .3        # baza cutiei în starea închisă
        base_y = base_y0
        # --- cronologie
        T_SHAKE, T_POP, T_RISE, T_OUT, T_SETTLE = .30, .95, 1.05, 1.9, 2.0
        # cutia: scuturare (anticipare) -> squash la deschidere -> alunecă în jos și dispare
        rot = 0.0; sx = sy = 1.0; dy = 0.0; balpha = 1.0
        if T_SHAKE <= t < T_POP:
            p = seg(t, T_SHAKE, T_POP); amp = 2 + 5 * p
            rot = amp * math.sin(p * math.pi * 7); sy = 1 - .05 * math.sin(p * math.pi * 2) * p; sx = 1 + .03 * math.sin(p * math.pi * 2) * p
        elif T_POP <= t < T_POP + .35:
            p = seg(t, T_POP, T_POP + .35); b = math.sin(p * math.pi * 2) * (1 - p)
            sx, sy = 1 + .07 * b, 1 - .09 * b
        SINK = min(260, 1545 - base_y0)                     # cutia coboară când iese produsul
        if T_POP <= t:
            dy = SINK * e_out(seg(t, T_POP + .05, T_POP + .75))
        if t >= T_OUT:
            p = seg(t, T_OUT, T_OUT + .5); dy = SINK + e_in(p) * 700; balpha = 1 - e_in(seg(t, T_OUT + .15, T_OUT + .5))
        # geometria cutiei (față + gură)
        bx0 = cx - BW / 2; by0 = base_y - BH + dy
        mouth_y = by0 - 28
        # transform simplu pentru cutie + capac: desenăm pe strat, apoi rotim în jurul bazei
        pivot = (cx, base_y + dy)
        def place(layer_im, x, y):
            return layer_im, x, y
        box = Image.new('RGBA', fg.size, (0, 0, 0, 0))
        # umbra cutiei
        sh = c.shadow_img(int(BW * 1.05)); paste(box, mul_alpha(sh, balpha * (1 - clamp(dy / 500))), cx - sh.width / 2, base_y + dy - sh.height / 2 + 14)
        # interior
        paste(box, mul_alpha(P['mouth'], balpha), cx - P['mouth'].width / 2, mouth_y)
        # produs (dacă a început să iasă)
        prod_layer = None; bb_prod = None
        if t >= T_RISE - .02:
            p_up = e_back(seg(t, T_RISE, T_OUT - .1), 1.3) if t < T_OUT - .1 else 1.0
            sc_p = lerp(.45, .58, e_out(seg(t, T_RISE, T_OUT - .1)))
            peak_bottom = min(by0 - 40, base_y0 + SINK - BH - 40)   # talpa produsului la vârf, deasupra ramei
            start_bottom = by0 + 150                   # ascuns în cutie
            bottom = lerp(start_bottom, peak_bottom, clamp(p_up, 0, 1.04))
            prot = 5 * math.sin(seg(t, T_RISE, T_OUT) * math.pi * 2) * (1 - seg(t, T_RISE + .5, T_OUT))
            pcx = cx
            lift = 0
            if t >= T_SETTLE:
                q = e_inout(seg(t, T_SETTLE, T_SETTLE + .75))
                bottom = lerp(peak_bottom, gy, q); sc_p = lerp(.58, 1.0, q)
                fy, fr = self.idle(max(0, t - T_SETTLE - .75), 8)
                lift = max(0, fy) * seg(t, T_SETTLE + .75, T_SETTLE + 1.0)
                prot = fr * seg(t, T_SETTLE + .75, T_SETTLE + 1.0)
                shadow_lift = (gy - bottom) * 1.0 + lift
            tmp = Image.new('RGBA', fg.size, (0, 0, 0, 0))
            emerging = t < T_SETTLE
            if emerging:
                bb_prod = c.draw_product(tmp, self.img, pcx, bottom, self.box, sc_p, prot, 1.0, 0, 0, None, 1, 1, shadow=False)
                clipy = int(by0 + 6)                    # rama din față a cutiei
                arr = np.asarray(tmp.getchannel('A')).copy(); arr[clipy:, :] = 0; tmp.putalpha(Image.fromarray(arr))
            else:
                bb_prod = c.draw_product(tmp, self.img, pcx, gy, self.box, sc_p, prot, 1.0, 0, gy - bottom + lift, None, 1, 1)
            prod_layer = tmp
        # --- ordine: interior -> produs (tăiat) -> față cutie -> capac
        fg.alpha_composite(box)
        if prod_layer is not None and t < T_SETTLE: fg.alpha_composite(prod_layer)
        # rotire/squash în jurul bazei aplicat doar feței cutiei
        front = Image.new('RGBA', fg.size, (0, 0, 0, 0))
        paste(front, mul_alpha(P['body'], balpha), bx0, by0)
        # lumină din interior la deschidere
        gl_p = seg(t, T_POP, T_POP + .55)
        if 0 < gl_p < 1:
            g = self._glow(int(520 * (0.5 + gl_p)))
            paste(fg, mul_alpha(g, (1 - gl_p) * .95), cx - g.width / 2, mouth_y + 30 - g.height / 2)
            fx_burst(fg, t - T_POP, cx, mouth_y + 20, (255, 255, 255), n=14, r0=260, r1=560, width=14, seed=.3)
        if abs(rot) > .05 or abs(sx - 1) > .001 or abs(sy - 1) > .001:
            w0, h0 = front.size
            fr_im = front.resize((int(w0 * sx), int(h0 * sy)), Image.BICUBIC) if (sx != 1 or sy != 1) else front
            fr_im = fr_im.rotate(rot, center=(cx * sx, (base_y + dy) * sy), resample=Image.BICUBIC) if abs(rot) > .05 else fr_im
            # recentrare după resize
            ox = cx - cx * sx; oy = (base_y + dy) - (base_y + dy) * sy
            paste(fg, fr_im, ox, oy)
        else:
            fg.alpha_composite(front)
        # produsul deasupra cutiei după ce a ieșit complet
        if prod_layer is not None and t >= T_SETTLE: fg.alpha_composite(prod_layer)
        # capac: sare în sus cu rotire, apoi iese din cadru
        lid = P['lid']
        lid_cy0 = by0 + 6 - (ly + LH) + lid.height / 2      # centrul capacului când stă pe cutie
        if t < T_POP:
            im = lid.rotate(rot, resample=Image.BICUBIC, expand=True) if abs(rot) > .05 else lid
            paste(fg, im, cx - im.width / 2, lid_cy0 - im.height / 2)
        else:
            p = seg(t, T_POP, T_POP + .8)
            if p < 1:
                x = cx + e_out(p) * 430
                y = lid_cy0 - e_out(p) * 1050 - math.sin(min(1, p * 1.6) * math.pi) * 110
                im = lid.rotate(-e_out(p) * 55, resample=Image.BICUBIC, expand=True)
                paste(fg, mul_alpha(im, 1 - e_in(seg(p, .6, 1))), x - im.width / 2, y - im.height / 2)
        # confetti din gura cutiei la deschidere
        if t >= T_POP:
            fx_confetti(fg, t - T_POP, th['fx'] + [(255, 255, 255)], n=90, cx=cx, cy=mouth_y, power=.85)
            res_shake = 16 * (1 - seg(t, T_POP, T_POP + .3)) if t < T_POP + .3 else 0
        else:
            res_shake = 0
        # frame 0: bbox = cutia închisă (obiectul principal din thumbnail)
        self.gift_bb = (bx0 - 22, by0 - LH - 60, bx0 + BW + 22, base_y)
        if t > T_SETTLE and bb_prod is not None: self.gift_bb = bb_prod
        return {'shake': res_shake} if res_shake else {}

class FeatureScene(Scene):
    kind = 'feature'
    def setup(self):
        c, s = self.ctx, self.spec
        self.fx = s.get('fx', 'float'); self.img = s.get('image', 0)
        self.tt = TextBlock(c, s.get('title', ''), c.title_font, s.get('size', 96), CX_TEXT, 205, accent=s.get('accent', ''),
                            max_lines=2, name='titlu', min_size=72) if s.get('title') else None
        y2 = (self.tt.bbox[3] + 12) if self.tt else 205
        self.st = TextBlock(c, s['sub'], c.title_font, 72, CX_TEXT, y2, color=c.th['accent'], max_lines=2, name='sub', min_size=56) if s.get('sub') else None
        top = (self.st.bbox[3] if self.st else (self.tt.bbox[3] if self.tt else 200)) + 50
        self.pills = [fix_ro(p) for p in s.get('pills', [])][:2]
        self.gy = 1400 if self.pills else 1480
        self.box = (840, self.gy - top)
        self.focus = s.get('focus', [.5, .5])
        self.sweep = s.get('sweep', c.rec.get('sweep') and self.fx in ('pushin', 'float', 'parallax', 'mask'))
        c.effects.add('fx:' + self.fx)
        if self.sweep: c.effects.add('light_sweep')

    def events(self):
        ev = {'slam': [(.28, 'impact')], 'drop': [(.35, 'impact')], 'zoom_punch': [(.55, 'whoosh_s')],
              'spin': [(.05, 'whoosh_s')], 'tilt': [(.05, 'pop')], 'mask': [(.05, 'whoosh_s')]}.get(self.fx, [])
        if self.pills: ev.append((.75, 'pop'))
        return ev

    def render(self, fg, t):
        c, th = self.ctx, self.ctx.th; res = {}
        cx, gy = 540, self.gy
        s, rot, lift, sx, sy, blur, mask_r = 1, 0, 0, 1, 1, 0, None
        fy, fr = self.idle(t, 8)
        pw, ph = c.prod_size(self.img, self.box)
        fx = self.fx
        if fx in ('slam', 'drop'):
            T = .28 if fx == 'slam' else .35
            if t < T: p = e_in(seg(t, 0, T)); lift = (1 - p) * 1300; rot = (1 - p) * (-10)
            else:
                p = seg(t, T, T + .35); b = math.sin(p * math.pi * 2) * (1 - p); sx, sy = 1 + .08 * b, 1 - .08 * b
                fx_dust(fg, t - T, cx, gy, th['dust'], seed=9)
                if c.rec.get('shake'): res['shake'] = 20 * (1 - seg(t, T, T + .3)) if t < T + .3 else 0
                if t > T + .4: lift = max(0, fy); rot = fr
                c.effects.add('dust')
        elif fx == 'tilt':
            p = seg(t, 0, .5); s = lerp(.82, 1, e_back(p)); rot = -12 * (1 - e_back(p)) + (fr if t > .5 else 0); lift = max(0, fy) if t > .5 else 0
        elif fx == 'spin':
            p = seg(t, 0, .55); sx = max(.04, abs(math.cos((1 - e_out(p)) * math.pi))); lift = max(0, fy) if t > .55 else 0
        elif fx == 'zoom_punch':
            p = e_out(seg(t, .55, .75)) * (1 - e_inout(seg(t, 1.45, self.dur)))
            s = 1 + .4 * p; fxp, fyp = self.focus
            cx = 540 - (fxp - .5) * pw * .4 * p; gy = self.gy + (fyp - .5) * ph * .4 * p * 1.0 + ph * .4 * p * (1 - fyp) * 0
            lift = max(0, fy) * (1 - p)
            if p > .05: fx_ring(fg, seg(t, .75, 1.15), cx + (fxp - .5) * pw * s, gy - ph * s * (1 - fyp), 120, th['accent'], 11)
            c.effects.add('ring')
        elif fx == 'pushin':
            s = 1 + .1 * e_inout(seg(t, 0, self.dur)); lift = max(0, fy * .5)
        elif fx == 'parallax':
            cx = 540 + lerp(50, -50, e_inout(seg(t, 0, self.dur))); res['par'] = t * 80; lift = max(0, fy * .5)
        elif fx == 'mask':
            mask_r = 60 + e_out(seg(t, 0, .6)) * 1100 if t < .6 else None; lift = max(0, fy * .5)
        elif fx == 'rise':
            p = e_out(seg(t, 0, .5)); lift = max(0, fy); gy += (1 - p) * 500; s = lerp(.9, 1, p)
        else:  # float
            lift = max(0, fy); rot = fr * 1.5; s = lerp(.94, 1, e_out(seg(t, 0, .4)))
        sweep = seg(t, .5, 1.5) if self.sweep else None
        c.draw_product(fg, self.img, cx, gy, self.box, s, rot, 1, blur, lift, sweep, sx, sy, mask_r=mask_r)
        if self.tt: self.tt.draw(fg, t, 'kinetic', start=.05, stagger=.08)
        if self.st: self.st.draw(fg, t, 'pop', start=.35, stagger=.06)
        if self.pills:
            f = get_font(c.body_font, 46); ws = [f.getlength(p) + 64 for p in self.pills]; x = CX_TEXT - (sum(ws) + 20 * (len(ws) - 1)) / 2
            for i, p in enumerate(self.pills):
                draw_pill(c, fg, p, x + ws[i] / 2, self.gy + 60, seg(t, .7 + i * .12, 1.0 + i * .12), 46, fill=th['pill'], register=(t == 0))
                x += ws[i] + 20
        return res

class DetailScene(Scene):
    kind = 'detail'
    def setup(self):
        c, s = self.ctx, self.spec
        self.img = s.get('image', 0)
        self.tt = TextBlock(c, s.get('title', ''), c.title_font, s.get('size', 92), CX_TEXT, 205, accent=s.get('accent', ''), max_lines=2, name='titlu', min_size=72) if s.get('title') else None
        self.focus = s.get('focus', [.5, .5]); self.zoom = s.get('zoom', 1.7)
        top = (self.tt.bbox[3] if self.tt else 200) + 50
        self.cs = min(880, 1330 - top); self.cy = top + self.cs / 2
        self.label = fix_ro(s.get('label', ''))
        src = self.ctx.sprite(self.img)['src']
        self.src = src
        c.effects.add('zoom_detail')
    def events(self): return [(.05, 'whoosh_s'), (.7, 'pop')]
    def render(self, fg, t):
        c, th = self.ctx, self.ctx.th
        src = self.src; sw, sh = src.size; side = min(sw, sh)
        p = e_out(seg(t, .1, .7)); z = lerp(1.0, self.zoom, p) + .06 * seg(t, .7, self.dur)
        fx_, fy_ = self.focus
        cw = side / z
        x0 = clamp(fx_ * sw - cw / 2, 0, sw - cw); y0 = clamp(fy_ * sh - cw / 2, 0, sh - cw)
        cs = int(self.cs)
        crop = src.crop((int(x0), int(y0), int(x0 + cw), int(y0 + cw))).resize((cs, cs), Image.BICUBIC)
        card = make_card(crop, 14, 42)
        sh_ = self.ctx.cache.get(('cardshadow', cs))
        if sh_ is None:
            sh_ = Image.new('RGBA', (cs + 140, cs + 140), (0, 0, 0, 0))
            ImageDraw.Draw(sh_).rounded_rectangle((70, 90, cs + 70, cs + 90), 50, fill=rgba(mix(th['bg_bot'], (0, 0, 0), .5), 110))
            sh_ = sh_.filter(ImageFilter.GaussianBlur(26)); self.ctx.cache[('cardshadow', cs)] = sh_
        s = lerp(.88, 1, e_back(seg(t, 0, .35)))
        if s < .999: card = card.resize((int(card.width * s), int(card.height * s)), Image.BILINEAR)
        paste(fg, sh_, 540 - sh_.width / 2, self.cy - sh_.height / 2)
        paste(fg, card, 540 - card.width / 2, self.cy - card.height / 2)
        rx = 540 - cs / 2 + (fx_ * sw - x0) / cw * cs; ry = self.cy - cs / 2 + (fy_ * sh - y0) / cw * cs
        # v2: cercul e opțional. "ring": true|false (implicit false); "ring_at": [x,y] în coordonate poză (0-1); "ring_r": rază px
        if self.spec.get('ring', False) or self.spec.get('ring_at'):
            ax, ay = self.spec.get('ring_at', self.focus)
            rx = 540 - cs / 2 + (ax * sw - x0) / cw * cs; ry = self.cy - cs / 2 + (ay * sh - y0) / cw * cs
            fx_ring(fg, seg(t, .75, 1.15), rx, ry, self.spec.get('ring_r', 110), th['accent'], 12)
        if self.label:
            ly = min(self.cy + cs / 2 - 40, 1440)
            bb = draw_pill(c, fg, self.label, CX_TEXT, ly, seg(t, 1.0, 1.3), 48, name='eticheta', register=(t == 0))
        if self.tt: self.tt.draw(fg, t, 'kinetic', start=.05)
        return {}

class CounterScene(Scene):
    kind = 'counter'
    def setup(self):
        c, s = self.ctx, self.spec
        self.val = float(s['value']); self.suffix = fix_ro(s.get('suffix', '')); self.prefix = fix_ro(s.get('prefix', ''))
        self.dec = 0 if self.val == int(self.val) else 1
        f = get_font(c.title_font, 110)
        final = self.fmt(self.val)
        self.size = 110
        while f.getlength(final) > TEXT_MAXW and self.size > 72: self.size -= 4; f = get_font(c.title_font, self.size)
        c.qa_text('counter', (CX_TEXT - f.getlength(final) / 2, 230, CX_TEXT + f.getlength(final) / 2, 230 + self.size * 1.1), final)
        self.lab = TextBlock(c, s.get('label', ''), c.body_font, 52, CX_TEXT, 250 + self.size * 1.1, color=c.th['text'], name='eticheta', max_lines=2) if s.get('label') else None
        top = (self.lab.bbox[3] if self.lab else 380) + 50
        self.img = s.get('image', 0); self.box = (820, 1480 - top)
        c.effects.add('counter')
    def fmt(self, v):
        n = ('%.' + str(self.dec) + 'f') % v
        return self.prefix + n.replace('.', ',') + self.suffix
    def events(self): return [(.1 + k * .09, 'tick', .5) for k in range(7)] + [(.8, 'pop')]
    def render(self, fg, t):
        c, th = self.ctx, self.ctx.th
        p = e_out(seg(t, .1, .8)); v = self.val * p
        if self.dec == 0: v = round(v)
        txt = self.fmt(v); f = get_font(c.title_font, self.size)
        pulse = 1 + .12 * math.sin(seg(t, .8, 1.05) * math.pi)
        k = ('ctr', txt, self.size)
        im = Image.new('RGBA', (int(f.getlength(txt)) + 40, int(self.size * 1.4)), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((20, 4), txt, font=f, fill=rgba(th['accent']))
        if pulse > 1.001: im = im.resize((int(im.width * pulse), int(im.height * pulse)), Image.BILINEAR)
        paste(fg, im, CX_TEXT - im.width / 2, 222 - (im.height - self.size * 1.4) / 2)
        if self.lab: self.lab.draw(fg, t, 'rise', start=.5)
        fy, fr = self.idle(t, 8)
        c.draw_product(fg, self.img, 540, 1480, self.box, lerp(.9, 1, e_back(seg(t, 0, .45))), fr, 1, 0, max(0, fy))
        return {}

class SplitScene(Scene):
    kind = 'split'
    def setup(self):
        c, s = self.ctx, self.spec
        self.imgs = (s.get('images', [0, 1]) + [1])[:2]
        self.labels = [fix_ro(x) for x in s.get('labels', [])][:2]
        self.tt = TextBlock(c, s.get('title', ''), c.title_font, 92, CX_TEXT, 205, accent=s.get('accent', ''), max_lines=2, name='titlu', min_size=72) if s.get('title') else None
        c.effects.add('split_screen')
    def events(self): return [(.05, 'whoosh_s'), (.2, 'whoosh_s'), (.75, 'pop')]
    def render(self, fg, t):
        c, th = self.ctx, self.ctx.th
        top = (self.tt.bbox[3] if self.tt else 200) + 60
        cw, chh = 440, 1400 - top
        for i, idx in enumerate(self.imgs):
            p = e_out(seg(t, .05 + i * .15, .5 + i * .15))
            x = (80 if i == 0 else 560) + (1 - p) * (-700 if i == 0 else 700)
            d = ImageDraw.Draw(fg)
            d.rounded_rectangle((x, top, x + cw, top + chh), 40, fill=rgba(mix(th['bg_top'], (255, 255, 255), .7)))
            fy, fr = self.idle(t + i, 6)
            c.draw_product(fg, idx, x + cw / 2, top + chh - 50, (cw - 60, chh - 120), 1, 0, 1, 0, max(0, fy), shadow=True)
            if i < len(self.labels):
                draw_pill(c, fg, self.labels[i], x + cw / 2 if p >= 1 else x + cw / 2, top + chh + 25, seg(t, .7 + i * .12, 1.0 + i * .12), 44, register=(t == 0))
        if self.tt: self.tt.draw(fg, t, 'kinetic', start=.1)
        return {}

class GridScene(Scene):
    kind = 'grid'
    def setup(self):
        c, s = self.ctx, self.spec
        self.imgs = s.get('images', list(range(len(c.sprites))))[:9]
        self.tt = TextBlock(c, s.get('title', ''), c.title_font, 92, CX_TEXT, 205, accent=s.get('accent', ''), max_lines=2, name='titlu', min_size=72) if s.get('title') else None
        c.effects.add('grid_fill')
    def events(self): return [(.15 + i * .18, 'pop', .8) for i in range(len(self.imgs))]
    def render(self, fg, t):
        c, th = self.ctx, self.ctx.th
        n = len(self.imgs); cols = 2 if n <= 4 else 3
        rows = math.ceil(n / cols)
        top = (self.tt.bbox[3] if self.tt else 200) + 50
        gw, gh = 900, 1480 - top
        cw, chh = gw / cols, min(gh / rows, gw / cols * 1.15)
        for i, idx in enumerate(self.imgs):
            r_, c_ = divmod(i, cols)
            p = seg(t, .15 + i * .18, .5 + i * .18)
            if p <= 0: continue
            x = 90 + c_ * cw + cw / 2; gy = top + (r_ + 1) * chh - 30
            lift = (1 - e_out(p)) * 900 if p < 1 else 0
            b = math.sin(seg(t, .5 + i * .18, .8 + i * .18) * math.pi) * .08
            c.draw_product(fg, idx, x, gy, (cw - 50, chh - 60), 1, (1 - p) * 20, 1, 0, lift, None, 1 + b, 1 - b)
        if self.tt: self.tt.draw(fg, t, 'kinetic', start=.05)
        return {}

class ChecklistScene(Scene):
    kind = 'checklist'
    def setup(self):
        c, s = self.ctx, self.spec
        self.tt = TextBlock(c, s.get('title', ''), c.title_font, 88, CX_TEXT, 205, accent=s.get('accent', ''), max_lines=2, name='titlu', min_size=72) if s.get('title') else None
        y = (self.tt.bbox[3] if self.tt else 205) + 50
        self.items = []
        for it in s.get('items', [])[:3]:
            tb = TextBlock(c, it, c.body_font, 50, 180, y, maxw=780, align='left', max_lines=2, name='item', min_size=44)
            self.items.append((tb, y)); y = tb.bbox[3] + 34
        self.img = s.get('image', 0); self.gy = 1490; self.box = (720, self.gy - y - 40)
        c.effects.add('checklist')
    def events(self): return [(.45 + i * .35, 'pop') for i in range(len(self.items))]
    def render(self, fg, t):
        c, th = self.ctx, self.ctx.th
        fy, fr = self.idle(t, 10)
        c.draw_product(fg, self.img, 540, self.gy, self.box, lerp(.9, 1, e_out(seg(t, 0, .5))), fr * 1.5, 1, 0, max(0, fy),
                       seg(t, 1.2, 2.2) if c.rec.get('sweep') else None)
        if self.tt: self.tt.draw(fg, t, 'kinetic', start=.05)
        d = ImageDraw.Draw(fg)
        for i, (tb, y) in enumerate(self.items):
            st = .45 + i * .35; p = seg(t, st, st + .3)
            if p <= 0: continue
            r = 30 * e_back(p); cx_, cy_ = 128, y + tb.size * .62
            d.ellipse((cx_ - r, cy_ - r, cx_ + r, cy_ + r), fill=rgba(th['pill']))
            if p > .5:
                q = seg(p, .5, 1)
                pts = [(cx_ - 13, cy_), (cx_ - 4, cy_ + 10), (cx_ + 14, cy_ - 10)]
                if q < .5: pts = [pts[0], (lerp(pts[0][0], pts[1][0], q * 2), lerp(pts[0][1], pts[1][1], q * 2))]
                else: pts = [pts[0], pts[1], (lerp(pts[1][0], pts[2][0], (q - .5) * 2), lerp(pts[1][1], pts[2][1], (q - .5) * 2))]
                d.line(pts, fill=(255, 255, 255, 255), width=7, joint='curve')
            tb.draw(fg, t, 'slide', start=st + .05, dur=.3)
        return {}

class FinalScene(Scene):
    kind = 'final'
    def setup(self):
        c, s = self.ctx, self.spec
        self.img = s.get('image', 0); self.style = s.get('price_style', 'stamp')
        self.price = int(s['price_round']); self.ptxt = f'{self.price} lei'
        self.psize = 110; f = get_font(c.title_font, self.psize)
        pw = f.getlength(self.ptxt)
        self.py = 1000
        c.qa_text('pret', (CX_TEXT - pw / 2, self.py + 10, CX_TEXT + pw / 2, self.py + self.psize * 1.15), self.ptxt)
        self.old = int(s['old_price_round']) if s.get('old_price_round') else None
        if self.old:
            self.otxt = f'{self.old} lei'; self.osize = 64; fo = get_font(c.title_font, self.osize)
            ow = fo.getlength(self.otxt); self.oy = self.py - 78
            c.qa_text('pret_vechi', (CX_TEXT - ow / 2 - 24, self.oy, CX_TEXT + ow / 2 + 24, self.oy + self.osize * 1.3), self.otxt)
        self.plabel = fix_ro(s.get('price_label') or '')
        if self.plabel:   # v10: „De la" / „Tot setul" deasupra prețului (sau deasupra prețului vechi)
            self.ly = (self.oy - 92) if self.old else (self.py - 84)
            fl = get_font(c.body_font, 46); lw_ = fl.getlength(self.plabel) + 64
            c.qa_text('pret_eticheta', (CX_TEXT - lw_ / 2, self.ly, CX_TEXT + lw_ / 2, self.ly + 78), self.plabel)
        self.deliv = fix_ro(s.get('delivery', '') or '')
        self.cta = TextBlock(c, s.get('cta', 'Comandă pe homio.ro'), c.title_font, 72, CX_TEXT, 1330 if self.deliv else 1210,
                             color=c.th['text'], max_lines=1, name='cta', min_size=56)
        self.box = (700, 560)
        c.effects.add('price:' + self.style)
        if s.get('confetti'): c.effects.add('confetti')
    def events(self):
        ev = [(.05, 'whoosh_s')]
        ev += [(.3 + k * .06, 'tick', .45) for k in range(6)] if self.style == 'stamp' else []
        ev += [(.7, 'impact' if self.style == 'stamp' else 'sparkle')]
        if self.deliv: ev.append((1.1, 'pop'))
        ev.append((1.35, 'pop', .8))
        return ev
    def render(self, fg, t):
        c, th = self.ctx, self.ctx.th; res = {}
        fy, fr = self.idle(t, 8)
        pgy = min(900, self.ly - 26) if self.plabel else 900
        c.draw_product(fg, self.img, 540, pgy, (self.box[0], self.box[1] - (900 - pgy)), lerp(.7, 1, e_back(seg(t, 0, .45))), fr, 1, 0, max(0, fy),
                       seg(t, 1.6, 2.6) if c.rec.get('sweep') else None)
        if self.old:
            pa = e_out(seg(t, .05, .3))
            if pa > 0:
                fo = get_font(c.title_font, self.osize); ow = fo.getlength(self.otxt)
                im = Image.new('RGBA', (int(ow) + 60, int(self.osize * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.height // 2, fill=rgba(th['pill'], 235))
                d.text((30, self.osize * .12), self.otxt, font=fo, fill=rgba(th['pill_text'], 215))
                lw = (ow + 24) * e_out(seg(t, .3, .55))
                if lw > 1:
                    yy = im.height * .52
                    d.line((18, yy + 8, 18 + lw, yy - 8), fill=rgba(th['pill_text']), width=7)
                paste(fg, mul_alpha(im, pa), CX_TEXT - im.width / 2, self.oy + (1 - pa) * 30)
        f = get_font(c.title_font, self.psize)
        if self.style == 'stamp':
            if t < .7:
                v = int(round(self.price * e_out(seg(t, .25, .7)))); txt = f'{v} lei'; s = 1; a = min(1, seg(t, .2, .3) * 3)
            else:
                txt = self.ptxt; p = seg(t, .7, .85); s = lerp(1.7, 1, e_in(p)) if p < 1 else 1 + .04 * math.sin((t - .85) * 5); a = 1
            if t >= .82:
                fx_burst(fg, t - .82, CX_TEXT, self.py + self.psize * .6, th['accent'], n=14, r0=240, r1=420, width=10)
                if c.rec.get('shake'): res['shake'] = 18 * (1 - seg(t, .82, 1.05)) if t < 1.05 else 0
        elif self.style == 'elegant':
            txt = self.ptxt; p = e_out(seg(t, .5, 1.1)); s = 1; a = p
            d = ImageDraw.Draw(fg); lw = f.getlength(txt) * e_out(seg(t, .9, 1.4))
            d.line((CX_TEXT - lw / 2, self.py + self.psize * 1.25, CX_TEXT + lw / 2, self.py + self.psize * 1.25), fill=rgba(th['accent']), width=4)
        else:
            txt = self.ptxt; p = seg(t, .6, .95); s = e_back(p) if p < 1 else 1; a = min(1, p * 2)
            fx_sparkles(fg, t, [(CX_TEXT - 260, self.py + 10), (CX_TEXT + 270, self.py + 40), (CX_TEXT + 200, self.py + 150)], th['accent'])
        if a > 0 and s > .01:
            im = self.ctx.cache.get(('price', txt))
            if im is None:
                im = Image.new('RGBA', (int(f.getlength(txt)) + 40, int(self.psize * 1.45)), (0, 0, 0, 0))
                ImageDraw.Draw(im).text((20, 4), txt, font=f, fill=rgba(th['accent'])); self.ctx.cache[('price', txt)] = im
            if abs(s - 1) > .005: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
            dy = (1 - a) * 40 if self.style == 'elegant' else 0
            paste(fg, mul_alpha(im, a), CX_TEXT - im.width / 2, self.py + self.psize * .72 - im.height / 2 + dy)
        if self.plabel: draw_pill(c, fg, self.plabel, CX_TEXT, self.ly, seg(t, .1, .4), 46, fill=th['accent'], fg=ensure_contrast((255, 255, 255), [th['accent']]), register=False)
        if self.deliv: draw_pill(c, fg, self.deliv, CX_TEXT, 1200, seg(t, 1.1, 1.4), 46, register=(t == 0))
        self.cta.draw(fg, t, 'kinetic', start=1.35, stagger=.09)
        if self.spec.get('confetti') and t > .82: fx_confetti(fg, t - .82, th['fx'] + [(255, 255, 255)], n=80, cy=self.py)
        return res


# ------------------------------------------------------------------ v3: cadrul final fix (signature homio)
SIG_DELIVERY = 'Livrare în 1–2 zile'      # mereu, indiferent de produs
SIG_BG_TOP, SIG_BG_BOT = (255, 249, 238), (247, 228, 200)
SIG_TEXT, SIG_ACCENT = (58, 34, 14), (186, 108, 44)   # maro închis / portocaliu din logo
SIG_LOGO_W, SIG_LOGO_CY = 460, 760       # v7: logo transparent mare, centrat pe zona sigură (x=CX_TEXT)
SIG_SITE_Y, SIG_PILL_Y = 1045, 1205
class SignatureScene(Scene):
    """Același template la fiecare clip: logo mare + homio.ro + livrare. Ignoră paleta produsului."""
    kind = 'signature'
    def setup(self):
        c = self.ctx
        g = np.linspace(0, 1, H)[:, None, None]
        a, b = np.array(SIG_BG_TOP, np.float32), np.array(SIG_BG_BOT, np.float32)
        self.bg = Image.fromarray((a * (1 - g) + b * g).repeat(W, 1).astype(np.uint8), 'RGB').convert('RGBA')
        big, self.transparent = logo_fit(SIG_LOGO_W)
        if not self.transparent: big = logo_fit(280)[0]; big.putalpha(rounded_mask(big.size, 52))
        self.logo = big
        sh = Image.new('RGBA', (big.width + 160, big.height + 160), (0, 0, 0, 0))
        a = big.getchannel('A').point(lambda v: int(v * .28))
        tint = Image.new('RGBA', big.size, (90, 50, 10, 255)); tint.putalpha(a)
        sh.alpha_composite(tint, (80, 96)); self.shadow = sh.filter(ImageFilter.GaussianBlur(18))
        ly0 = SIG_LOGO_CY - big.height / 2
        c.qa_text('sig_logo', (CX_TEXT - big.width / 2, ly0, CX_TEXT + big.width / 2, ly0 + big.height), 'homio')
        self.name = TextBlock(c, 'homio.ro', 'poppins-xb', 104, CX_TEXT, SIG_SITE_Y, color=SIG_TEXT, max_lines=1, name='sig_site', min_size=90)
        self.deliv = fix_ro(SIG_DELIVERY)
        pw = get_font(c.body_font, 54).getlength(self.deliv) + 64
        c.qa_text('sig_livrare', (CX_TEXT - pw / 2, SIG_PILL_Y, CX_TEXT + pw / 2, SIG_PILL_Y + 92), self.deliv)
        c.effects.add('signature')
    def events(self): return [(.1, 'pop'), (.75, 'pop', .8)]
    def render(self, fg, t):
        fg.alpha_composite(self.bg)
        p = e_back(seg(t, .05, .55)); s = max(.01, lerp(.6, 1, p)); al = min(1, p * 2)
        if abs(s - 1) < .002: lg, sh = self.logo, self.shadow
        else:
            lg = self.logo.resize((max(1, int(self.logo.width * s)), max(1, int(self.logo.height * s))), Image.BILINEAR)
            sh = self.shadow.resize((max(1, int(self.shadow.width * s)), max(1, int(self.shadow.height * s))), Image.BILINEAR)
        paste(fg, mul_alpha(sh, al), CX_TEXT - sh.width / 2, SIG_LOGO_CY - sh.height / 2)
        paste(fg, mul_alpha(lg, al), CX_TEXT - lg.width / 2, SIG_LOGO_CY - lg.height / 2)
        hw, hh = self.logo.width / 2, self.logo.height / 2
        fx_sparkles(fg, t, [(CX_TEXT - hw - 50, SIG_LOGO_CY - hh + 40), (CX_TEXT + hw + 45, SIG_LOGO_CY + hh - 30),
                            (CX_TEXT + hw + 30, SIG_LOGO_CY - hh + 10)], SIG_ACCENT)
        self.name.draw(fg, t, 'kinetic', start=.45, stagger=.06)
        draw_pill(self.ctx, fg, self.deliv, CX_TEXT, SIG_PILL_Y, seg(t, .9, 1.2), 54, fill=SIG_ACCENT, fg=(255, 255, 255), name='sig_livrare', register=False)
        return {}
SCENES_EXTRA = dict(signature=SignatureScene)

def pill_box(ctx, text, size, cx, y, name):
    """v10: înregistrează în QA o pastilă care se desenează mai târziu (aceeași geometrie ca draw_pill)."""
    text = fix_ro(text); f = get_font(ctx.body_font, size)
    w, h = int(f.getlength(text) + 64), int(size * 1.7)
    ctx.qa_text(name, (cx - w / 2, y, cx + w / 2, y + h), text)
    return w, h

def multi_rows(n):
    return {1: [1], 2: [2], 3: [2, 1], 4: [2, 2]}.get(n, [3, 3])

class LineupScene(Scene):
    """v10 (collection): produsele intră pe rând, fiecare cu eticheta lui; opțional numerotate (1, 2, 3) pentru „pe care o alegi?"."""
    kind = 'lineup'
    def setup(self):
        c, s = self.ctx, self.spec
        self.items = s.get('items') or [p['hero'] for p in c.multi['products']]
        self.items = self.items[:6]
        labs = s.get('labels') or [p['label'] for p in c.multi['products']]
        self.labels = [fix_ro(x) for x in labs][:len(self.items)]
        self.numbers = bool(s.get('numbers', False))
        self.tt = TextBlock(c, s.get('title', ''), c.title_font, 88, CX_TEXT, 205, accent=s.get('accent', ''), max_lines=2, name='titlu', min_size=72) if s.get('title') else None
        top = (self.tt.bbox[3] if self.tt else 190) + 50
        rows = multi_rows(len(self.items)); rh = (1500 - top) / len(rows)
        self.cells, k = [], 0
        for r, ncol in enumerate(rows):
            cw = 880 / ncol
            for j in range(ncol):
                if k >= len(self.items): break
                cx = 70 + cw * j + cw / 2 if ncol > 1 else CX_TEXT
                gy = top + rh * (r + 1) - 92
                self.cells.append((cx, gy, (cw - 30, rh - 100)))
                k += 1
        for i, (cx, gy, box) in enumerate(self.cells):
            if i < len(self.labels) and self.labels[i]:
                pill_box(c, self.labels[i], 44, cx, gy + 14, 'eticheta')
        self.step = .26
        c.effects.add('lineup' + ('_numerotat' if self.numbers else ''))
    def events(self):
        ev = [(.12 + i * self.step, 'pop', .9) for i in range(len(self.items))]
        if self.numbers: ev += [(.25 + i * self.step, 'tick', .6) for i in range(len(self.items))]
        return ev
    def render(self, fg, t):
        c, th = self.ctx, self.ctx.th
        n = len(self.items); tall = .12 + n * self.step + .3
        hi = int((t - tall) / .5) % n if t > tall else -1
        d = ImageDraw.Draw(fg)
        for i, idx in enumerate(self.items):
            cx, gy, box = self.cells[i]
            st = .12 + i * self.step; p = seg(t, st, st + .35)
            if p <= 0: continue
            s = lerp(.4, 1, e_back(p)) * (1 + .06 * math.sin(seg(t, tall + hi * .5, tall + hi * .5 + .5) * math.pi) if i == hi else 1)
            lift = (1 - e_out(p)) * 160
            fy, fr = self.idle(t + i * .7, 5)
            c.draw_product(fg, idx, cx, gy, box, s, fr, min(1, p * 2), 0, lift + max(0, fy) if p >= 1 else lift)
            if i < len(self.labels) and self.labels[i]:
                draw_pill(c, fg, self.labels[i], cx, gy + 14, seg(t, st + .2, st + .45), 44, register=False)
            if self.numbers:
                q = seg(t, st + .12, st + .4)
                if q > 0:
                    w_, h_ = c.prod_size(idx, box)
                    r = 46 * e_back(q); bx = cx - min(w_, box[0]) / 2 + 30; by = gy - h_ + 20
                    bx = max(bx, 70 + r); by = max(by, 200 + r)
                    d.ellipse((bx - r, by - r, bx + r, by + r), fill=rgba(th['accent']), outline=(255, 255, 255, 255), width=5)
                    if q > .4:
                        f = get_font(c.title_font, 58)
                        d.text((bx, by + 2), str(i + 1), font=f, fill=rgba(ensure_contrast((255, 255, 255), [th['accent']])), anchor='mm')
        if self.tt: self.tt.draw(fg, t, 'kinetic', start=.05)
        return {}

class ComboScene(Scene):
    """v10 (combo): produsele apar ca A + B + C, apoi se strâng într-un singur set (sprite-ul de grup)."""
    kind = 'combo'
    def setup(self):
        c, s = self.ctx, self.spec
        self.meta = c.group_meta
        self.items = [m['idx'] for m in self.meta]
        self.tt = TextBlock(c, s.get('title', ''), c.title_font, 88, CX_TEXT, 205, accent=s.get('accent', ''), max_lines=2, name='titlu', min_size=72) if s.get('title') else None
        top = (self.tt.bbox[3] if self.tt else 190) + 60
        self.gy = 1390; self.gbox = (880, self.gy - top - 20)
        n = len(self.items); rows = [n] if n <= 2 else ([1, 2] if n == 3 else [2, n - 2])   # v11: la 3 produse, erou mare sus + 2 jos
        self.row, self.plus, k = [], [], 0
        rh = 470 if n == 3 else (380 if len(rows) > 1 else 460)
        y0 = top + 60
        for r, ncol in enumerate(rows):
            cw = 880 / ncol; gb = y0 + rh * (r + 1)
            for j in range(ncol):
                idx = self.items[k]
                w_, h_ = c.prod_size(idx, (cw - 110, rh - 60))
                self.row.append((70 + cw * j + cw / 2, gb, w_))
                if j > 0: self.plus.append(((70 + cw * j), gb - (rh - 60) / 2, k))
                k += 1
            if r > 0: self.plus.append((CX_TEXT, y0 + rh * r + 10, k - ncol))
        gw, gh = c.prod_size('group', self.gbox)
        k = gw / c.sprite('group')['img'].width
        gx0, gy0 = 540 - gw / 2, self.gy - gh
        self.tgt = [(gx0 + m['cx'] * k, gy0 + m['bottom'] * k, m['w'] * k) for m in self.meta]
        self.pill = fix_ro(s.get('pill', ''))
        if self.pill: pill_box(c, self.pill, 48, CX_TEXT, 1420, 'eticheta')
        self.step = .3; self.a_end = .15 + n * self.step + .1; self.b_end = self.a_end + .5
        c.effects.add('combo_asamblare')
    def events(self):
        ev = [(.15 + i * self.step, 'pop') for i in range(len(self.items))]
        ev += [(self.a_end, 'whoosh_s'), (self.b_end - .02, 'impact' if self.ctx.rec.get('shake') else 'sparkle', .9)]
        if self.pill: ev.append((self.b_end + .25, 'pop', .8))
        return ev
    def render(self, fg, t):
        c, th = self.ctx, self.ctx.th; res = {}
        n = len(self.items)
        if t < self.b_end:
            pb = e_inout(seg(t, self.a_end, self.b_end))
            # „+" între produse
            if pb < 1:
                f = get_font(c.title_font, 96); d = ImageDraw.Draw(fg)
                for (x, y, kk) in self.plus:
                    q = seg(t, .15 + kk * self.step - .08, .15 + kk * self.step + .1)
                    if q <= 0: continue
                    d.text((x, y), '+', font=f, fill=rgba(th['accent'], 255 * min(1, q * 2) * (1 - pb)), anchor='mm')
            order = [m['order'] for m in self.meta]
            for i in sorted(range(n), key=lambda j: order[j]):
                idx = self.items[i]
                st = .15 + i * self.step; p = seg(t, st, st + .3)
                if p <= 0: continue
                rx, rb, rw = self.row[i]; tx, tb, tw = self.tgt[i]
                cx = lerp(rx, tx, pb); gb = lerp(rb, tb, pb); w_ = lerp(rw, tw, pb)
                s = lerp(.5, 1, e_back(p))
                c.draw_product(fg, idx, cx, gb, (w_, 4000), s, (1 - p) * 12, min(1, p * 2), 0, 0, shadow=pb < .9)
        else:
            fy, fr = self.idle(t - self.b_end, 6)
            pop = 1 + .07 * math.sin(seg(t, self.b_end, self.b_end + .3) * math.pi)
            c.draw_product(fg, 'group', 540, self.gy, self.gbox, pop, fr * .6, 1, 0, max(0, fy))
            if c.rec.get('confetti'): fx_burst(fg, t - self.b_end, 540, self.gy - 380, th['accent'], n=14, r0=300, r1=520, width=10)
            else: fx_sparkles(fg, t - self.b_end, [(160, self.gy - 600), (900, self.gy - 520), (860, self.gy - 160)], th['accent'])
            if c.rec.get('shake') and t < self.b_end + .25: res['shake'] = 14 * (1 - seg(t, self.b_end, self.b_end + .25))
            if self.pill: draw_pill(c, fg, self.pill, CX_TEXT, 1420, seg(t, self.b_end + .25, self.b_end + .5), 48, register=False)
        if self.tt: self.tt.draw(fg, t, 'kinetic', start=.05)
        return res


SCENES = dict(hook=HookScene, feature=FeatureScene, detail=DetailScene, counter=CounterScene, split=SplitScene,
              grid=GridScene, checklist=ChecklistScene, final=FinalScene, signature=SignatureScene,
              lineup=LineupScene, combo=ComboScene)

# ------------------------------------------------------------------ sunet
SR = 48000
def synth(kind):
    r = np.random.RandomState(hash(kind) % 1000)
    def env(n, a, d):
        e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
        e[na:] = np.exp(-np.linspace(0, d, n - na)); return e
    def lp(x, cut):
        y = np.zeros_like(x); acc = 0.0
        cut = np.broadcast_to(cut, x.shape)
        al = 1 - np.exp(-2 * np.pi * cut / SR)
        for i in range(len(x)): acc += al[i] * (x[i] - acc); y[i] = acc
        return y
    if kind in ('whoosh', 'whoosh_s'):
        d = .42 if kind == 'whoosh' else .26; n = int(d * SR); tt = np.linspace(0, 1, n)
        x = r.randn(n); cut = 600 + 5000 * np.sin(np.pi * tt) ** 2
        y = lp(x, cut) - lp(x, cut * .25); e = np.sin(np.pi * tt) ** 1.5
        return y * e * (.9 if kind == 'whoosh' else .6)
    if kind == 'impact':
        n = int(.45 * SR); tt = np.arange(n) / SR
        f = 90 * np.exp(-tt * 6) + 42; ph = 2 * np.pi * np.cumsum(f) / SR
        body = np.sin(ph) * np.exp(-tt * 7)
        click = lp(r.randn(n), 2500) * np.exp(-tt * 45) * 1.5
        return (body + click) * .95
    if kind == 'pop':
        n = int(.1 * SR); tt = np.arange(n) / SR
        f = 1100 * np.exp(-tt * 30) + 300; ph = 2 * np.pi * np.cumsum(f) / SR
        return np.sin(ph) * np.exp(-tt * 40) * .6
    if kind == 'tick':
        n = int(.03 * SR); tt = np.arange(n) / SR
        return np.sin(2 * np.pi * 2200 * tt) * np.exp(-tt * 180) * .35
    if kind == 'sparkle':
        n = int(.7 * SR); tt = np.arange(n) / SR; y = np.zeros(n)
        for k, f in enumerate([1760, 2349, 2960, 3520]):
            st = int(k * .06 * SR); seg_ = tt[:n - st]
            y[st:] += np.sin(2 * np.pi * f * seg_) * np.exp(-seg_ * 7) * .18
        return y
    if kind == 'sub':   # v9: sub-bas scurt sub impact
        n = int(.38 * SR); tt = np.arange(n) / SR
        f = 62 * np.exp(-tt * 5) + 38; ph = 2 * np.pi * np.cumsum(f) / SR
        return np.sin(ph) * np.exp(-tt * 6.5) * .9
    if kind == 'riser':  # v9: zgomot filtrat care urcă (înainte de preț)
        n = int(.8 * SR); tt = np.linspace(0, 1, n)
        x = r.randn(n); cut = 300 + 6500 * tt ** 2
        y = lp(x, cut) - lp(x, cut * .3)
        return y * (tt ** 2.2) * .55
    if kind == 'swish':   # v12: suflu moale (blur, dip, light leak)
        n = int(.34 * SR); tt = np.linspace(0, 1, n)
        x = r.randn(n); cut = 250 + 1700 * np.sin(np.pi * tt) ** 2
        y = lp(x, cut) - lp(x, cut * .3); e = np.sin(np.pi * tt) ** 2
        return y * e * .5
    if kind == 'glitch':  # v12: rafale digitale scurte (pătrat + zgomot decimat)
        n = int(.14 * SR); tt = np.arange(n) / SR; y = np.zeros(n)
        for k, (f, a0, a1) in enumerate([(1250, 0, .03), (520, .045, .075), (2100, .09, .12)]):
            i0, i1 = int(a0 * SR), int(a1 * SR)
            y[i0:i1] = np.sign(np.sin(2 * np.pi * f * tt[i0:i1])) * .22
        z = r.randn(n); z = np.repeat(z[::24], 24)[:n] * .12
        return (y + z * (np.abs(y) > 0)) * np.exp(-tt * 6)
    return np.zeros(10)

def build_audio(events, total, path, peak_db=-4.0, pitch=1.0, seed=1):
    n = int(total * SR); buf = np.zeros(n)
    cache = {}
    rr = random.Random(seed)
    for t, kind, g in events:
        if kind not in cache: cache[kind] = synth(kind)
        s0 = cache[kind]
        pf = pitch * rr.uniform(.96, 1.04)          # v9: variație mică la fiecare eveniment (nu sună a mașină)
        if abs(pf - 1) > .005 and len(s0) > 20:
            s0 = np.interp(np.arange(0, len(s0) - 1, pf), np.arange(len(s0)), s0)
        s = s0 * g; i = int(t * SR)
        if i >= n: continue
        m = min(len(s), n - i); buf[i:i + m] += s[:m]
    pk = np.abs(buf).max()
    if pk > 0: buf *= (10 ** (peak_db / 20)) / pk
    pcm = (buf * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.repeat(pcm, 2).tobytes())

# ------------------------------------------------------------------ construcție
def r_lei(x): return int(math.floor(float(str(x).replace(',', '.')) + .5))

def normalize_multi(cfg):
    """v10: „products" -> „product" sintetic (nume, preț de la / total) + cfg['_multi']. Idempotent."""
    if not cfg.get('products') or cfg.get('_multi'): return cfg
    ps = cfg['products']
    mode = cfg.get('multi') or 'collection'
    plabel = cfg.get('price_label') or ('Tot setul' if mode == 'combo' else 'De la')
    prods = []
    for i, p in enumerate(ps):
        imgs = p.get('images') or [i]
        lab = p.get('label') or ' '.join(fix_ro(p['name']).split()[:2])
        prods.append(dict(name=p['name'], url=p.get('url', ''), price=float(str(p['price']).replace(',', '.')),
                          old=p.get('old_price'), label=lab, images=imgs, hero=imgs[0]))
    if plabel == 'Tot setul':
        price = sum(p['price'] for p in prods)
        olds = [p['old'] for p in prods]
        old = sum(float(str(o).replace(',', '.')) for o in olds) if all(olds) else None
    else:
        price = min(p['price'] for p in prods); old = None
    name = cfg.get('title') or ' + '.join(p['name'] for p in prods)
    cfg['product'] = dict(name=name, url=prods[0]['url'], price=round(price, 2), old_price=old)
    cfg['_multi'] = dict(mode=mode, products=prods, price_label=plabel, character=cfg.get('character', ''))
    return cfg

def build_group(ctx, mode):
    """v10: un singur sprite cu toate produsele (hook, final, combo). collection = rând/grilă egală; combo = erou + accesorii în față."""
    prods = ctx.multi['products']
    ims = [ctx.sprite(p['hero'])['img'] for p in prods]
    n = len(ims); H0 = 1000
    meta = []
    if mode == 'combo':
        def by_area(im, T):
            f = T / math.sqrt(im.width * im.height)
            return im.resize((max(1, int(im.width * f)), max(1, int(im.height * f))), Image.LANCZOS)
        hero = by_area(ims[0], H0 * .9)
        acc = [by_area(im, H0 * .5) for im in ims[1:]]
        gap = int(H0 * .04)
        roww = sum(a.width for a in acc) + gap * max(0, len(acc) - 1)
        lim = max(hero.width * 1.7, H0 * 1.3)
        if roww > lim:                       # rândul de accesorii nu e mai lat decât ~1.7 × eroul
            k = lim / roww; acc = [a.resize((max(1, int(a.width * k)), max(1, int(a.height * k))), Image.LANCZOS) for a in acc]
            roww = sum(a.width for a in acc) + gap * max(0, len(acc) - 1)
        acch = max([a.height for a in acc] or [0])
        cw = int(max(hero.width, roww)) + 20
        base = hero.height + int(acch * .55) if acc else hero.height     # accesoriile stau în fața eroului, mai jos
        ch = base + 10
        canvas = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        hx = (cw - hero.width) / 2
        canvas.alpha_composite(hero, (int(hx), 5))
        meta.append(dict(idx=prods[0]['hero'], cx=hx + hero.width / 2, bottom=5 + hero.height, w=hero.width, order=0))
        x = (cw - roww) / 2
        for j, a in enumerate(acc):
            canvas.alpha_composite(a, (int(x), int(base - a.height) + 5))
            meta.append(dict(idx=prods[j + 1]['hero'], cx=x + a.width / 2, bottom=base + 5, w=a.width, order=j + 1))
            x += a.width + gap
    else:
        rows = multi_rows(n); gap = int(H0 * .06)
        sc = [im.resize((max(1, int(im.width * H0 / im.height)), H0), Image.LANCZOS) for im in ims]
        cellw = max(s.width for s in sc)
        cw = max(rows) * cellw + (max(rows) - 1) * gap; ch = len(rows) * H0 + (len(rows) - 1) * gap
        canvas = Image.new('RGBA', (cw + 20, ch + 10), (0, 0, 0, 0))
        k = 0
        for r, ncol in enumerate(rows):
            roww = ncol * cellw + (ncol - 1) * gap; x0 = (cw - roww) / 2
            for j in range(ncol):
                if k >= n: break
                s = sc[k]; cx = x0 + j * (cellw + gap) + cellw / 2; bottom = (r + 1) * H0 + r * gap
                canvas.alpha_composite(s, (int(cx - s.width / 2) + 10, int(bottom - s.height) + 5))
                meta.append(dict(idx=prods[k]['hero'], cx=cx + 10, bottom=bottom + 5, w=s.width, order=k)); k += 1
    tgt = 1180 * HI; f = min(tgt / canvas.width, tgt / canvas.height)
    big = canvas.resize((max(1, int(canvas.width * f)), max(1, int(canvas.height * f))), Image.LANCZOS)
    for m in meta: m['cx'] *= f; m['bottom'] *= f; m['w'] *= f
    flat = Image.new('RGB', big.size, (255, 255, 255)); flat.paste(big, (0, 0), big)
    ctx.sprites.append(dict(img=big, kind='group', src=flat, white=True))
    ctx.group_idx = len(ctx.sprites) - 1; ctx.group_meta = meta

def merge_recipe(cfg):
    r = cfg.get('recipe', 'toy')
    rs = r if isinstance(r, list) else [r]
    rec = dict(RECIPES.get(rs[0], RECIPES['toy']))
    if len(rs) > 1 and rs[1] in RECIPES:
        o = RECIPES[rs[1]]
        rec['hook'] = o['hook']; rec['confetti'] = rec['confetti'] or o['confetti']; rec['stickers'] = rec['stickers'] or o['stickers']
        rec['fx'] = rec['fx'][:2] + o['fx'][:2]
    rec.update(cfg.get('style', {}))
    rec['name'] = '+'.join(rs)
    return rec

def make_edit(cfg, rec):
    """v9: stil de edit unic per clip, determinist din produs + hook (sau edit_seed)."""
    seed = str(cfg.get('edit_seed') or (cfg['product']['name'] + '|' + cfg.get('hook', '')))
    r = random.Random(int(hashlib.md5(seed.encode('utf-8')).hexdigest()[:12], 16))
    base = rec['name'].split('+')[0]
    pool = list(dict.fromkeys(TR_POOL.get(base, TR_POOL['toy'])))
    if len(rec['name'].split('+')) > 1:
        pool = list(dict.fromkeys(pool + TR_POOL.get(rec['name'].split('+')[1], [])))
    # v12: reguli de ton — calm = fără tranziții agresive; fără shake în rețetă = fără punch/glitch
    if base in ('baby', 'decor'): pool = [x for x in pool if x in TR_CALM]
    if not rec.get('shake'): pool = [x for x in pool if x not in TR_SHAKE]
    avoid = set((cfg.get('edit') or {}).get('avoid_transitions', []))
    p2 = [x for x in pool if x not in avoid]
    if len(p2) >= 3: pool = p2
    # v12: o familie de 3–4 tranziții per clip (limbaj vizual unitar), apoi secvență fără repetiții consecutive
    # familia: 2–3 tranziții de bază + max 1 tranziție foarte vizibilă (spin/shape/circle/lightleak) + max 1 accent (glitch/punch/flash)
    base_ = [x for x in pool if x not in TR_MAX2]; feat = [x for x in pool if x in TR_MAX2 and x not in TR_ACCENT]
    accs = [x for x in pool if x in TR_ACCENT]
    fam = r.sample(base_, min(len(base_), 2 + (r.random() < .4)))
    if feat and r.random() < .8: fam.append(r.choice(feat))
    if accs and r.random() < .6: fam.append(r.choice(accs))
    rest = [x for x in pool if x not in fam]
    while len(fam) < 3 and rest: fam.append(rest.pop(r.randrange(len(rest))))
    seq, prev, used = [], None, {}
    for _ in range(8):
        ch = [x for x in fam if x != prev and not (x in TR_MAX2 and used.get(x, 0) >= 2)] or [x for x in fam if x != prev] or fam
        prev = r.choice(ch); seq.append(prev); used[prev] = used.get(prev, 0) + 1
    sig_ok = [x for x in TR_SIG if x in pool or x in ('dip', 'fade')]
    if base in ('baby', 'decor'): sig_ok = [x for x in sig_ok if x in TR_CALM]
    sig_ok = [x for x in sig_ok if not (x in TR_MAX2 and seq.count(x) >= 2)] or ['dip']
    sig_tr = r.choice(sig_ok)
    dirs, pd = [], None
    for _ in range(8):
        ch = [x for x in DIRS if x != pd]
        pd = r.choice(ch); dirs.append(pd)
    calm = base in ('baby', 'decor')
    ed = dict(
        transitions=seq, dirs=dirs, family=fam, sig_tr=sig_tr,
        bg=r.choice(BG_POOL.get(base, [rec['bg']])),
        bg_vx=r.choice([-1, 1]) * r.uniform(4, 10), bg_vy=r.choice([-1, 1]) * r.uniform(3, 10), bg_phase=r.uniform(0, 6.28),
        vignette=round(r.uniform(.10, .20 if calm else .28), 2),
        grain=round(r.choice([0, 0, .006, .010]), 3),
        sat=round(r.uniform(1.0, 1.08), 3), contrast=round(r.uniform(1.0, 1.05), 3), warm=r.choice([-4, 0, 3, 6]),
        reflect=r.choice([0, .12, .16, .20]),
        tempo=[round(r.uniform(.93, 1.07), 3) for _ in range(12)],
        fx_order=r.sample(range(4), 4),
        sfx_pitch=round(r.uniform(.93, 1.09), 3), sfx_layers=True,
        motion_blur=5,
    )
    ed.update({k: v for k, v in cfg.get('edit', {}).items() if k != 'avoid_transitions'})
    ed['sig'] = 'tr:' + ed.get('sig_tr', '') + '|%s|%s|vig%.2f|grain%.3f|refl%.2f|pitch%.2f' % ('/'.join(ed['transitions'][:5]), ed['bg'], ed['vignette'], ed['grain'], ed['reflect'], ed['sfx_pitch'])
    return ed

def prepare_images(cfg, ctx):
    sprites = []
    for i, spec in enumerate(cfg['images']):
        if isinstance(spec, str): spec = {'src': spec}
        im = load_rgb(fetch(spec['src']))
        if spec.get('crop'):
            x0, y0, x1, y1 = spec['crop']; im = im.crop((int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height)))
        mode = spec.get('cutout', 'auto')
        white = is_white_bg(im)
        if mode == 'auto': mode = 'white' if white else 'card'
        if mode == 'white': spr = trim(cutout_white(im)); kind = 'cut'
        elif mode == 'rembg': spr = trim(cutout_rembg(im)); kind = 'cut'
        else: spr = make_card(im); kind = 'card'
        tgt = 1180 * HI
        f = min(tgt / spr.width, tgt / spr.height)
        spr = spr.resize((max(1, int(spr.width * f)), max(1, int(spr.height * f))), Image.LANCZOS)
        if f > 1.2: spr = spr.filter(ImageFilter.UnsharpMask(2, 60, 2))
        sprites.append(dict(img=spr, kind=kind, src=im, white=white))
    ctx.sprites = sprites

def auto_scenes(cfg, rec):
    sc = []
    mu = cfg.get('_multi')
    hook = dict(type='hook', text=cfg['hook'], accent=cfg.get('hook_accent', ''), style=rec['hook'],
                image=cfg.get('hook_image', 'group' if mu else 0), badges=cfg.get('badges', []),
                gift_box=cfg.get('gift_box'), gift_ribbon=cfg.get('gift_ribbon'))
    if rec['hook'] == 'gift': hook['dur'] = 3.0
    sc.append(hook)
    if mu and cfg.get('multi_scene', True) and not any(p.get('type') in ('lineup', 'combo') for p in cfg.get('points', [])):
        if mu['mode'] == 'combo':
            sc.append(dict(type='combo', title=cfg.get('combo_title', ''), pill=cfg.get('combo_pill', '')))
        else:
            sc.append(dict(type='lineup', title=cfg.get('lineup_title', ''), numbers=cfg.get('numbers', False)))
    fxs = rec['fx']; k = 0
    for p in cfg.get('points', []):
        p = dict(p); p.setdefault('type', 'feature')
        if p['type'] == 'feature' and 'fx' not in p: p['fx'] = fxs[k % len(fxs)]; k += 1
        sc.append(p)
    if cfg.get('features'):
        sc.append(dict(type='checklist', title=cfg.get('features_title', ''), items=cfg['features'], image=cfg.get('features_image', 0)))
    fin = dict(cfg.get('final', {}))
    if mu: fin.setdefault('image', 'group'); fin.setdefault('price_label', mu['price_label'])
    sc.append(dict(type='final', **fin))
    if cfg.get('signature', True): sc.append(dict(type='signature'))
    return sc

def build(cfg, out):
    normalize_multi(cfg)
    rec = merge_recipe(cfg)
    ctx = Ctx(cfg, out, rec)
    prepare_images(cfg, ctx)
    ctx.multi = cfg.get('_multi')
    if ctx.multi: build_group(ctx, ctx.multi['mode'])
    pal = extract_palette([s['img'] for s in ctx.sprites if s['kind'] == 'cut'] or [ctx.sprites[0]['img']])
    ctx.pal = pal
    ctx.th = build_theme(pal, rec, cfg.get('palette', {}))
    rng = random.Random(slug(cfg['product']['name']))
    ctx.edit = make_edit(cfg, rec)
    if 'bg' not in cfg.get('style', {}): rec['bg'] = ctx.edit['bg']
    if 'transitions' not in cfg.get('style', {}): rec['transitions'] = ctx.edit['transitions']
    if 'fx' not in cfg.get('style', {}):
        fx0 = list(rec['fx']); rec['fx'] = [fx0[i % len(fx0)] for i in ctx.edit['fx_order']]
    ctx.bg = Background(ctx.th, rec['bg'], cfg.get('season'), rng, ctx.edit)
    price = float(str(cfg['product']['price']).replace(',', '.'))
    ctx.price_round = int(math.floor(price + .5))
    op = cfg['product'].get('old_price')
    ctx.old_round = int(math.floor(float(str(op).replace(',', '.')) + .5)) if op else None
    specs = cfg.get('scenes') or auto_scenes(cfg, rec)
    trans = rec['transitions']
    durs = [s.get('dur', DUR.get(s['type'], 2.0)) * (ctx.edit['tempo'][i % 12] if s['type'] not in ('signature', 'final', 'hook') else 1.0) for i, s in enumerate(specs)]
    tot = sum(durs); target = cfg.get('duration')
    if target: f = target / tot
    else: f = 12.5 / tot if tot < 12.5 else (17.5 / tot if tot > 17.5 else 1)
    scenes, t0 = [], 0.0
    for i, (s, d) in enumerate(zip(specs, durs)):
        s = dict(s)
        if s['type'] == 'final':
            s.setdefault('price_round', ctx.price_round); s.setdefault('price_style', rec['price'])
            s.setdefault('confetti', rec['confetti']); s['delivery'] = ''  # livrarea stă în cadrul signature
            s.setdefault('cta', 'Comandă pe homio.ro')
            if ctx.old_round and ctx.old_round > ctx.price_round: s.setdefault('old_price_round', ctx.old_round)
        if i > 0 and s['type'] == 'signature' and 'transitions' not in cfg.get('style', {}): s.setdefault('tin', ctx.edit.get('sig_tr', 'fade'))
        if i > 0: s.setdefault('tin', trans[(i - 1) % len(trans)]); s.setdefault('tdir', ctx.edit['dirs'][(i - 1) % len(ctx.edit['dirs'])])
        sc = SCENES[s['type']](ctx, s, round(d * f * FPS) / FPS)
        sc.t0 = t0; t0 += sc.dur; scenes.append(sc)
        if i > 0: ctx.effects.add('tr:' + sc.tin)
    ctx.scenes, ctx.total = scenes, t0
    for sc in scenes:
        for e in sc.events():
            ctx.sfx(sc.t0 + e[0], e[1], e[2] if len(e) > 2 else 1.0)
        if sc.t0 > 0 and sc.tin in TR_SFX:
            k_, g_, d_ = TR_SFX[sc.tin]; ctx.sfx(max(0, sc.t0 + d_), k_, g_)
    if ctx.edit.get('sfx_layers', True):   # v9: straturi de sunet
        extra = []
        for (t_, k_, g_) in ctx.sfx_events:
            if k_ == 'impact': extra.append((t_, 'sub', .8))
        for sc in scenes:
            if sc.kind == 'final': extra.append((max(0, sc.t0 - .75), 'riser', .9))
        ctx.sfx_events += extra
    ctx.logo = logo_badge()
    return ctx

# ------------------------------------------------------------------ compoziție
LOOP = .3
_grid = {}
def _xy():
    if 'xy' not in _grid:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); _grid['xy'] = (xx, yy)
    return _grid['xy']

def scale_center(im, sx, sy=None, cx=W / 2, cy=H / 2):
    sy = sx if sy is None else sy
    if abs(sx - 1) < 1e-3 and abs(sy - 1) < 1e-3: return im
    w, h = max(1, int(im.width * sx)), max(1, int(im.height * sy))
    big = im.resize((w, h), Image.BILINEAR)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); paste(out, big, cx - cx * sx, cy - cy * sy); return out

def avg_rgba(ims):
    """medie în spațiu premultiplicat (fără halouri negre) — folosită la blur de rotație/radial."""
    acc = None
    for im in ims:
        a = np.asarray(im).astype(np.float32); al = a[..., 3:4] / 255.0
        pm = np.concatenate([a[..., :3] * al, a[..., 3:4]], 2)
        acc = pm if acc is None else acc + pm
    acc /= len(ims)
    al2 = np.clip(acc[..., 3:4], 1e-3, 255) / 255.0
    rgb = np.where(acc[..., 3:4] > .5, acc[..., :3] / al2, 0)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), acc[..., 3]]).astype(np.uint8), 'RGBA')

def blur_rgba(im, r):
    if r < .5: return im
    return im.convert('RGBa').filter(ImageFilter.GaussianBlur(r)).convert('RGBA')

def apply_tr(fg, kind, p, direction, dirn='L'):
    """Transformă stratul unei scene. direction: 'in' (p 0->1 intrare) / 'out' (p 0->1 ieșire).
    dirn: L|R|U|D — ieșirea pleacă spre -dir, intrarea vine din +dir (mișcarea continuă dintr-o scenă în alta)."""
    if kind in ('cut', 'flash') or kind in TR_MASK or kind in ('shape', 'circle', 'dip', 'lightleak', 'glitch') or p <= 0:
        return fg
    out_ = direction == 'out'
    if kind == 'fade':
        return mul_alpha(fg, p if not out_ else 1 - p)
    dx, dy = DIRV.get(dirn, (-1, 0))
    sg = -1 if dx < 0 or dy < 0 else 1
    if kind in ('whip', 'slide'):
        mag = W * (.7 if kind == 'whip' else .5) if dx else H * (.45 if kind == 'whip' else .28)
        if out_: off = -e_in(p) * mag; bl = e_in(p) * (240 if kind == 'whip' else 0)
        else: off = (1 - e_out(p)) * mag; bl = (1 - p) * (240 if kind == 'whip' else 0)
        out = Image.new('RGBA', fg.size, (0, 0, 0, 0))
        if bl >= 3: im, bx, by = motion_blur_dir(fg, bl, dirn)
        else: im, bx, by = fg, 0, 0
        o = off * (1 if sg < 0 else -1)
        paste(out, im, (o if dx else 0) + bx, (o if dy else 0) + by)
        if kind == 'slide': out = mul_alpha(out, p if not out_ else 1 - p)
        return out
    if kind in ('zoom', 'zoomout'):
        if kind == 'zoom': s = lerp(1, 1.4, e_in(p)) if out_ else lerp(.8, 1, e_out(p))
        else: s = lerp(1, .78, e_in(p)) if out_ else lerp(1.3, 1, e_out(p))
        return mul_alpha(scale_center(fg, s), 1 - p if out_ else p)
    if kind == 'spin':
        # whip rotațional: unghi + zoom, blur de rotație din 2–6 copii rotite progresiv
        q = e_in(p) if out_ else 1 - e_out(p)
        ang = (sg if out_ else -sg) * 28 * q; s = 1 + .22 * q
        base = scale_center(fg, s)
        n = 1 + int(round(q * 3))
        ims = [base.rotate(ang * (1 - k * .07), resample=Image.BILINEAR, center=(W / 2, H / 2)) for k in range(n)]
        im = avg_rgba(ims) if n > 1 else ims[0]
        return mul_alpha(im, 1 - q * (.9 if out_ else .55))
    if kind == 'zoomblur':
        # zoom-through: scena veche crește spre cameră, cea nouă vine din mai aproape; dâră radială
        q = e_in(p) if out_ else 1 - e_out(p)
        s = 1 + (.6 if out_ else .35) * q
        n = 1 + int(round(q * 3)); st = .16 * q
        ims = [scale_center(fg, s * (1 + st * k / max(1, n - 1))) for k in range(n)]
        im = avg_rgba(ims) if n > 1 else ims[0]
        return mul_alpha(im, 1 - q * (.95 if out_ else .5))
    if kind == 'stretch':
        if out_:
            q = e_in(p); return mul_alpha(scale_center(fg, 1 - .32 * q, 1 + .5 * q), 1 - q)
        k = e_back(p, 1.5)                       # overshoot elastic la aterizare
        return mul_alpha(scale_center(fg, lerp(.72, 1, k), lerp(1.45, 1, k)), min(1, p * 2.2))
    if kind == 'blur':
        q = e_in(p) if out_ else 1 - e_out(p)
        im = blur_rgba(scale_center(fg, 1 + .045 * q), 30 * q)
        return mul_alpha(im, 1 - q * (.85 if out_ else .6))
    if kind == 'punch':
        if out_: return fg
        return scale_center(fg, 1 + .14 * (1 - e_out(p)) ** 2)
    return fg

def tr_mask(kind, p, dirn):
    """1 = scena nouă vizibilă. Întoarce (mască float HxW, dâră/inel pentru decor)."""
    xx, yy = _xy()
    if kind == 'iris':
        cx, cy = W / 2, H * .53
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        R = math.hypot(W / 2, H * .53) + 70
        r = e_inout(p) * R
        m = np.clip((r - d) / 46 + .5, 0, 1)
        edge = np.exp(-((d - r) / 7) ** 2) * (1 - p) ** .7 * (r > 4)
        return m, edge
    # wipe: front ușor oblic pe direcția de mișcare, margine moale + dâră de lumină
    if dirn in ('L', 'R'): c = (xx + .18 * (yy - H / 2)) / W; c = 1 - c if dirn == 'L' else c
    else: c = (yy + .18 * (xx - W / 2)) / H; c = 1 - c if dirn == 'U' else c
    lo, hi = -.12, 1.12
    f = lerp(lo - .05, hi + .05, e_inout(p))
    m = np.clip((f - c) * (W if dirn in ('L', 'R') else H) / 60 + .5, 0, 1)
    edge = np.exp(-((c - f) * (W if dirn in ('L', 'R') else H) / 16) ** 2) * .55 * math.sin(math.pi * clamp(p))
    return m, edge

def mask_mix(prev, new, m, edge=None, edge_color=(255, 255, 255)):
    a_p = np.asarray(prev).astype(np.float32); a_n = np.asarray(new).astype(np.float32)
    a_p[..., 3] *= (1 - m); a_n[..., 3] *= m
    out = Image.fromarray(a_p.astype(np.uint8), 'RGBA'); out.alpha_composite(Image.fromarray(a_n.astype(np.uint8), 'RGBA'))
    if edge is not None and edge.max() > .02:
        c = np.zeros((H, W, 4), np.float32); c[..., :3] = edge_color; c[..., 3] = np.clip(edge, 0, 1) * 255
        out.alpha_composite(Image.fromarray(c.astype(np.uint8), 'RGBA'))
    return out

_ovl = {}
def tr_overlay(ctx, frame, kind, phase, p, dirn, fi):
    """Overlay-uri pe tot cadrul (fundal + scenă), peste tăietură. phase: 'out' (înainte de tăietură) / 'in' (după)."""
    th = ctx.th; acc = np.array(hx(tohex(th['accent'])), np.float32)
    calm = ctx.rec['name'].split('+')[0] in ('baby', 'decor')
    xx, yy = _xy()
    if kind == 'dip':
        col = (255, 249, 238) if calm else mix(tohex(th['accent']), (0, 0, 0), .35)
        a = e_in(p) if phase == 'out' else 1 - e_out(p)
        frame.alpha_composite(Image.new('RGBA', (W, H), rgba(col, int(255 * a)))); return frame
    if kind == 'shape':
        # bandă oblică accent cu margini deschise; la tăietură acoperă tot cadrul
        u = .5 * e_in(p) if phase == 'out' else .5 + .5 * e_out(p)
        if dirn in ('L', 'R'): c = (xx + .3 * (yy - H / 2)) / W; c = 1 - c if dirn == 'L' else c; px = W
        else: c = (yy + .3 * (xx - W / 2)) / H; c = 1 - c if dirn == 'U' else c; px = H
        wd = 1.62; lead = lerp(-.33, 1.33 + wd, u)
        def band(lo_, hi_): return np.clip((c - lo_) * px / 1.5 + .5, 0, 1) * np.clip((hi_ - c) * px / 1.5 + .5, 0, 1)
        light = np.array(mix(tohex(th['accent']), (255, 255, 255), .55), np.float32)
        mB = band(lead - wd - .09, lead + .09); mA = band(lead - wd, lead)
        f = np.asarray(frame.convert('RGB')).astype(np.float32)
        f = f * (1 - mB[..., None]) + light * mB[..., None]
        f = f * (1 - mA[..., None]) + acc * mA[..., None]
        return Image.fromarray(np.clip(f, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    if kind == 'circle':
        f = np.asarray(frame.convert('RGB')).astype(np.float32)
        if phase == 'out':   # cercul crește din colțul opus direcției și acoperă cadrul
            ox = W * (1.05 if dirn in ('L', 'U') else -.05); oy = H * (1.02 if dirn in ('L', 'D') else -.02)
            r = e_in(p) * (math.hypot(W, H) * 1.08)
            m = np.clip((r - np.sqrt((xx - ox) ** 2 + (yy - oy) ** 2)) / 2 + .5, 0, 1)
        else:                # accent cu o gaură care se deschide din centru spre scena nouă
            r = e_out(p) * (math.hypot(W / 2, H / 2) + 40)
            m = 1 - np.clip((r - np.sqrt((xx - W / 2) ** 2 + (yy - H * .53) ** 2)) / 2 + .5, 0, 1)
        f = f * (1 - m[..., None]) + acc * m[..., None]
        return Image.fromarray(np.clip(f, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    if kind == 'lightleak':
        I = e_in(p) if phase == 'out' else 1 - e_out(p)
        sw, sh = 270, 480; u = (.5 * p) if phase == 'out' else .5 + .5 * p
        key = ('ll', round(u, 3))
        y_, x_ = np.mgrid[0:sh, 0:sw].astype(np.float32)
        warm = np.array([255, 176, 96], np.float32) / 255; tint = np.array(mix(tohex(th['accent']), (255, 255, 255), .45), np.float32) / 255
        def blob(cx, cy, r): return np.exp(-(((x_ - cx) / r) ** 2 + ((y_ - cy) / (r * 1.25)) ** 2))
        L = blob(lerp(-.2, 1.2, u) * sw, lerp(.15, .55, u) * sh, sw * .55)[..., None] * warm + \
            blob(lerp(1.1, -.1, u) * sw, lerp(.85, .45, u) * sh, sw * .5)[..., None] * tint
        L = np.clip(L * 1.3 + warm * .22 * I ** 2, 0, 1)
        Lb = np.asarray(Image.fromarray((L * 255).astype(np.uint8), 'RGB').resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
        f = np.asarray(frame.convert('RGB')).astype(np.float32) / 255
        A = np.clip(Lb.max(2, keepdims=True) * I * .62, 0, .8)         # colorare caldă (vizibilă și pe fundal alb)
        col = Lb / np.clip(Lb.max(2, keepdims=True), 1e-3, 1)
        f = f * (1 - A) + col * A
        f = 1 - (1 - f) * (1 - Lb * I * .35)                   # + puțin screen pentru strălucire
        return Image.fromarray(np.clip(f * 255, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    if kind in ('glitch', 'punch'):
        I = (e_in(p) if phase == 'out' else 1 - p) if kind == 'glitch' else (1 - p) ** 2
        if I < .05: return frame
        a = np.asarray(frame.convert('RGB')).copy()
        d = int(round((22 if kind == 'glitch' else 12) * I))
        if d:
            a[..., 0] = np.roll(a[..., 0], d, 1); a[..., 2] = np.roll(a[..., 2], -d, 1)
        if kind == 'glitch':
            rr = random.Random(fi * 7 + 3)
            for _ in range(int(3 + 5 * I)):
                y0 = rr.randrange(150, H - 200); hh = rr.randrange(14, 90); sh_ = int(rr.choice([-1, 1]) * rr.uniform(20, 90) * I)
                a[y0:y0 + hh] = np.roll(a[y0:y0 + hh], sh_, 1)
            a[::3] = (a[::3].astype(np.float32) * (1 - .12 * I)).astype(np.uint8)
        return Image.fromarray(a, 'RGB').convert('RGBA')
    return frame

_vig = {}
def post_fx(ctx, frame, t):
    """v9: vignetă + grading discret + grain (nu se aplică pe signature și nici pe logo)."""
    e = ctx.edit
    a = np.asarray(frame.convert('RGB')).astype(np.float32)
    if e.get('vignette', 0) > 0:
        if 'm' not in _vig:
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            d = np.sqrt(((xx - W / 2) / (W * .75)) ** 2 + ((yy - H / 2) / (H * .75)) ** 2)
            _vig['m'] = np.clip(d - .35, 0, 1)[..., None] ** 1.6
        a = a * (1 - e['vignette'] * _vig['m'])
    if e.get('sat', 1) != 1 or e.get('contrast', 1) != 1 or e.get('warm', 0):
        g = a.mean(2, keepdims=True)
        a = g + (a - g) * e.get('sat', 1)
        a = (a - 128) * e.get('contrast', 1) + 128
        w = e.get('warm', 0)
        if w: a[..., 0] += w; a[..., 2] -= w
    if e.get('grain', 0) > 0:
        # grain FIX (același tipar pe toate cadrele): codecul îl codează o singură dată; grain care variază la fiecare cadru umfla fișierul la zeci de MB
        if 'g' not in _vig:
            _vig['g'] = np.random.RandomState(7).randn(H, W, 1).astype(np.float32)
        a = a + _vig['g'] * (e['grain'] * 255)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')

def moving_window(ctx, t):
    """True dacă la momentul t e mișcare rapidă (început de scenă sau tranziție de ieșire) => se aplică motion blur temporal."""
    if t < 1e-6: return False
    for i, sc in enumerate(ctx.scenes):
        if sc.t0 <= t < sc.t0 + sc.dur:
            lt = t - sc.t0
            if sc.kind == 'signature' and lt > tr_time(sc.tin)[1]: return False
            if lt < .5 and i > 0: return True
            if i + 1 < len(ctx.scenes) and sc.dur - lt < tr_time(ctx.scenes[i + 1].tin)[0] + .03: return True
            if lt < .45 and i == 0: return True
    return False

TR_OWNBLUR = {'spin', 'zoomblur', 'blur', 'iris', 'wipe', 'shape', 'circle', 'dip', 'lightleak', 'glitch', 'stretch'}
def in_own_blur_tr(ctx, t):
    """v12: tranzițiile cu blur propriu nu mai trec prin motion blur temporal (de 5 ori mai rapid, fără dublarea blur-ului)."""
    for i, sc in enumerate(ctx.scenes):
        if sc.t0 <= t < sc.t0 + sc.dur:
            lt = t - sc.t0
            if i > 0 and sc.tin in TR_OWNBLUR and lt < tr_time(sc.tin)[1]: return True
            if i + 1 < len(ctx.scenes):
                nx = ctx.scenes[i + 1]
                if nx.tin in TR_OWNBLUR and sc.dur - lt < tr_time(nx.tin)[0]: return True
    return False

def compose_mb(ctx, t):
    """v9: motion blur real — media a n sub-cadre într-un obturator de ~0.42 cadru."""
    n = int(ctx.edit.get('motion_blur', 5))
    if n < 2 or not moving_window(ctx, t) or in_own_blur_tr(ctx, t): return compose(ctx, t)
    was = ctx.qa_enabled; ctx.qa_enabled = False
    shutter = .42 / FPS; acc = None
    for k in range(n):
        tk = max(0.0, t + (k / (n - 1) - .5) * shutter)
        f = np.asarray(compose(ctx, tk)).astype(np.float32)
        acc = f if acc is None else acc + f
    ctx.qa_enabled = was
    return Image.fromarray((acc / n).astype(np.uint8), 'RGB')

def compose(ctx, t):
    sc_i = 0
    for i, sc in enumerate(ctx.scenes):
        if t >= sc.t0 - 1e-6: sc_i = i
    sc = ctx.scenes[sc_i]; lt = t - sc.t0
    fg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    res = sc.render(fg, lt) or {}
    flash, ovl, tshake = 0, None, 0
    tin = tr_time(sc.tin)[1]
    if sc_i > 0 and tin and lt < tin:
        p = seg(lt, 0, tin)
        if sc.tin in TR_MASK:          # v12: scena veche (ultimul ei cadru) rămâne sub mască
            prev = ctx.scenes[sc_i - 1]
            pfg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            was = ctx.qa_enabled; ctx.qa_enabled = False
            prev.render(pfg, max(0, prev.dur - 1 / FPS)); ctx.qa_enabled = was
            m, edge = tr_mask(sc.tin, p, sc.tdir)
            ec = mix(tohex(ctx.th['accent']), (255, 255, 255), .2) if sc.tin == 'iris' else (255, 250, 240)
            fg = mask_mix(pfg, fg, m, edge, ec)
        else:
            fg = apply_tr(fg, sc.tin, p, 'in', sc.tdir)
        if sc.tin == 'flash': flash = [1, .75, .35, .1, 0, 0, 0][min(6, int(lt * FPS))]
        if sc.tin in TR_OVL: ovl = (sc.tin, 'in', p, sc.tdir)
        if sc.tin == 'punch': tshake = 26 * (1 - p) ** 2
    if sc_i + 1 < len(ctx.scenes):
        nx = ctx.scenes[sc_i + 1]; rem = sc.dur - lt; tout = tr_time(nx.tin)[0]
        if tout and rem < tout:
            p = 1 - rem / tout
            if nx.tin in TR_FG_OUT: fg = apply_tr(fg, nx.tin, p, 'out', nx.tdir)
            if nx.tin in TR_OVL: ovl = (nx.tin, 'out', p, nx.tdir)
    frame = ctx.bg.frame(t, res.get('par', 0))
    frame.alpha_composite(fg)
    if flash: frame.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(235 * flash))))
    sh = max(res.get('shake', 0), tshake)
    if sh > .5:
        r = random.Random(int(t * 1000))
        dx, dy = r.uniform(-sh, sh), r.uniform(-sh, sh)
        big = frame.resize((int(W * 1.05), int(H * 1.05)), Image.BILINEAR)
        ox, oy = (big.width - W) / 2 + dx, (big.height - H) / 2 + dy
        frame = big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    if ovl: frame = tr_overlay(ctx, frame, ovl[0], ovl[1], ovl[2], ovl[3], int(round(t * FPS)))
    if sc.kind != 'signature':            # cadrul signature rămâne identic la toate clipurile
        frame = post_fx(ctx, frame, t)
    frame.alpha_composite(ctx.logo, (LOGO_XY[0] - 8, LOGO_XY[1] - 8))   # v7: plăcuța are 8 px margine de umbră
    return frame.convert('RGB')

# ------------------------------------------------------------------ QA
def run_qa(ctx, motion=None, audio_peak=None):
    R = []
    def add(name, ok, info=''): R.append((name, 'PASS' if ok is True else ('WARN' if ok == 'warn' else 'FAIL'), info))
    x0, y0, x1, y1 = SAFE
    bad = [f"{t['name']}:{t['text'][:25]}{t['bbox']}" for t in ctx.texts
           if not (t['bbox'][0] >= x0 - 1 and t['bbox'][1] >= y0 - 1 and t['bbox'][2] <= x1 + 1 and t['bbox'][3] <= y1 + 1)]
    add('text_zona_sigura', not bad, '; '.join(bad[:4]))
    alltxt = ' '.join(t['text'] for t in ctx.texts)
    add('pret_rotunjit', not re.search(r'\d+[.,]\d+\s*lei', alltxt) and f'{ctx.price_round} lei' in alltxt, f'{ctx.price_round} lei')
    add('cta', 'Comandă pe homio.ro' in alltxt)
    if getattr(ctx, 'old_round', None):
        add('pret_vechi_taiat', any(t['name'] == 'pret_vechi' and t['text'] == f'{ctx.old_round} lei' for t in ctx.texts), f'{ctx.old_round} lei')
    add('diacritice_virgula', not re.search('[şţŞŢ]', alltxt))
    th = ctx.th
    cr = min(contrast(th['text'], th['bg_top']), contrast(th['text'], th['bg_bot']), contrast(th['accent'], th['bg_bot']),
             contrast(th['accent'], th['bg_top']), contrast(th['pill_text'], th['pill']))
    add('contrast_4.5', cr >= 4.5, f'min {cr:.1f}')
    hk = [t for t in ctx.texts if t['name'] == 'hook']
    if hk:
        n = len(hk[0]['text'].split()); add('hook_max7', n <= 7, f'{n} cuvinte')
    f0 = dict(ctx.frame0_boxes)
    if 'produs' in f0:
        b = f0['produs']; ok = b[0] >= 0 and b[2] <= W and b[1] >= 150 and b[3] <= H - 300
        add('frame0_produs_intreg', ok, str([round(v) for v in b]))
        if 'hook' in f0:
            hb = f0['hook']; ov = not (hb[3] <= b[1] + 10 or hb[1] >= b[3] or hb[2] <= b[0] or hb[0] >= b[2])
            add('frame0_hook_liber', not ov or 'warn', 'hook atinge produsul' if ov else '')
    # v5: aceeași specificație a produsului apare cel mult de 2 ori în tot clipul
    def _norm(x): return re.sub(r'\s+', ' ', ''.join(ch for ch in unicodedata.normalize('NFD', x.lower()) if unicodedata.category(ch) != 'Mn'))
    skip = set(_norm(ctx.cfg.get('product', {}).get('name', '')).replace(',', ' ').split()) | {'homio', 'comanda', 'livrare', 'zile', 'lei', 'pentru', 'potrivita'}
    seen, cnt = set(), {}
    for t_ in ctx.texts:
        if t_['name'] in ('pret', 'cta', 'sig_site', 'sig_livrare', 'hook'): continue
        key = (t_['name'], t_['text'])
        if key in seen: continue
        seen.add(key)
        n_ = _norm(t_['text'])
        toks = set(re.findall(r'\d+\s*x\s*\d+(?:\s*x\s*\d+)?\s*cm|\d+(?:[.,]\d+)?\s*(?:cm|mm|kg|g|l|ml|ani|luni|piese|w)\b', n_))
        toks |= {w for w in re.findall(r'[a-z]{6,}', n_) if w not in skip}
        for tk in toks: cnt.setdefault(re.sub(r'\s+', '', tk), []).append(t_['name'])
    hk_ = ' '.join(_norm(t_['text']) for t_ in ctx.texts if t_['name'] == 'hook')
    for tk in re.findall(r'\d+\s*x\s*\d+(?:\s*x\s*\d+)?\s*cm|\d+(?:[.,]\d+)?\s*(?:cm|mm|kg|g|l|ml|ani|luni|piese|w)\b', hk_):
        cnt.setdefault(re.sub(r'\s+', '', tk), []).append('hook')
    rep = {k: v for k, v in cnt.items() if len(v) > 2}
    add('repetitii_max2', not rep, '; '.join(f"{k}x{len(v)}" for k, v in list(rep.items())[:4]))
    add('livrare_1_2_zile', 'Livrare în 1–2 zile' in alltxt)
    add('fara_retur', not re.search(r'retur', alltxt, re.I))
    add('signature_final', bool(ctx.scenes) and ctx.scenes[-1].kind == 'signature' or 'warn')
    add('durata_12_18', 12 <= ctx.total <= 18, f'{ctx.total:.1f}s')
    if motion is not None:
        add('miscare_2.5s', motion <= 2.5, f'max static {motion:.2f}s')
    if audio_peak is not None:
        add('audio_varf_-3dB', audio_peak <= -3.0, f'{audio_peak:.1f} dB')
    return R

# ------------------------------------------------------------------ ieșiri
def sheet(frames, path):
    tw, th_ = 270, 480
    s = Image.new('RGB', (tw * 6, th_ * 2 + 2), (255, 255, 255))
    for i, (t, f) in enumerate(frames[:12]):
        im = f.resize((tw, th_), Image.BILINEAR)
        ImageDraw.Draw(im).text((8, th_ - 22), f'{t:.1f}s', fill=(255, 0, 0))
        s.paste(im, ((i % 6) * tw, (i // 6) * (th_ + 2)))
    s.save(path, quality=85)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('config', nargs='?'); ap.add_argument('--out'); ap.add_argument('--sheet', action='store_true')
    ap.add_argument('--inspect', action='store_true'); ap.add_argument('--times'); ap.add_argument('--example', action='store_true'); ap.add_argument('--example-multi', action='store_true')
    a = ap.parse_args()
    if a.example: print(json.dumps(EXAMPLE, ensure_ascii=False, indent=1)); return
    if a.example_multi: print(json.dumps(EXAMPLE_MULTI, ensure_ascii=False, indent=1)); return
    cfg = normalize_multi(json.load(open(a.config, encoding='utf-8')))
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.config)), 'out_' + slug(cfg['product']['name']))
    os.makedirs(out, exist_ok=True)
    if a.inspect:
        cells = []
        for i, spec in enumerate(cfg['images']):
            src = spec if isinstance(spec, str) else spec['src']
            im = load_rgb(fetch(src)); cells.append((i, im, is_white_bg(im)))
        s = Image.new('RGB', (300 * len(cells), 330), 'white'); d = ImageDraw.Draw(s)
        for i, im, wb in cells:
            im.thumbnail((290, 290)); s.paste(im, (i * 300 + 5, 5)); d.text((i * 300 + 8, 300), f'#{i} {"alb" if wb else "card"} {im.size}', fill=(200, 0, 0))
        s.save(os.path.join(out, 'inspect.jpg'), quality=85); print(os.path.join(out, 'inspect.jpg')); return
    t_start = time.time()
    ctx = build(cfg, out)
    N = int(round(ctx.total * FPS))
    if a.times:
        for tt in a.times.split(','):
            compose(ctx, float(tt)).save(os.path.join(out, f't{float(tt):05.2f}.png'))
        print('ok'); return
    idx12 = [int(round(k * (N - 1) / 11)) for k in range(12)]
    if a.sheet:
        fr = []
        for fi in idx12:
            f = compose(ctx, fi / FPS); fr.append((fi / FPS, f))
            if fi == 0: f.save(os.path.join(out, 'frame0.png'))
        sheet(fr, os.path.join(out, 'sheet.jpg'))
        for n, s, i in run_qa(ctx): print(f'{s} {n} {i}')
        return
    tmp = os.path.join(out, '_v.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp],
                         stdin=subprocess.PIPE)
    small_prev, diffs, fr = None, [], []
    q = []
    for fi in range(N):
        f = compose(ctx, 0.0) if fi == 0 else compose_mb(ctx, fi / FPS)
        if fi == 0: f.save(os.path.join(out, 'frame0.png')); ctx.qa_enabled = False; f0img = f
        if cfg.get('loop', False) and fi / FPS > ctx.total - LOOP:
            f = Image.blend(f, f0img, e_inout(seg(fi / FPS, ctx.total - LOOP, ctx.total - 1 / FPS))); ctx.effects.add('loop')
        if fi in idx12: fr.append((fi / FPS, f))
        sm = np.asarray(f.resize((108, 192), Image.BILINEAR).convert('L'), np.float32)
        q.append(sm)
        if len(q) > 6: q.pop(0)
        diffs.append(float(np.abs(sm - q[0]).mean()) if len(q) == 6 else 99)
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()
    # mișcare: cea mai lungă porțiune cu diferență mică pe 0.2 s
    run = best = 0
    for d in diffs:
        run = run + 1 if d < .35 else 0; best = max(best, run)
    motion = (best + 6) / FPS if best else 0
    final = os.path.join(out, 'video.mp4'); peak = None
    if cfg.get('sfx', True) and ctx.sfx_events:
        wav = os.path.join(out, '_sfx.wav'); build_audio(ctx.sfx_events, ctx.total, wav, pitch=ctx.edit.get('sfx_pitch', 1.0), seed=int(ctx.edit.get('sfx_pitch', 1) * 1000))
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                        '-shortest', '-movflags', '+faststart', final], check=True)
        r = subprocess.run(['ffmpeg', '-i', final, '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True)
        m = re.search(r'max_volume: (-?[\d.]+) dB', r.stderr); peak = float(m.group(1)) if m else None
        os.remove(wav); os.remove(tmp)
    else:
        os.replace(tmp, final)
    sheet(fr, os.path.join(out, 'sheet.jpg'))
    qa = run_qa(ctx, motion, peak)
    for n, s, i in qa: print(f'{s} {n} {i}')
    jr = dict(produs=cfg['product']['name'], reteta=ctx.rec['name'], hook=fix_ro(cfg.get('hook', '')), hook_type=cfg.get('hook_type', ''),
              efecte=sorted(ctx.effects), paleta=[tohex(ctx.th['bg_top']), tohex(ctx.th['accent']), tohex(ctx.th['text']), tohex(ctx.th['pill'])],
              durata=round(ctx.total, 1), pret=(ctx.multi['price_label'] + ' ' if ctx.multi else '') + f'{ctx.price_round} lei', edit=ctx.edit['sig'], tranzitii='/'.join(ctx.edit.get('family', [])))
    if ctx.multi: jr['multi'] = ctx.multi['mode']; jr['produse'] = [f"{p['name']} ({r_lei(p['price'])} lei)" for p in ctx.multi['products']]
    json.dump(dict(qa=qa, journal=jr), open(os.path.join(out, 'qa.json'), 'w'), ensure_ascii=False, indent=1)
    print('JOURNAL ' + json.dumps(jr, ensure_ascii=False))
    print(f'OUT {final} ({time.time() - t_start:.0f}s)')

EXAMPLE = {
    "product": {"name": "Trotinetă pliabilă Frozen", "url": "https://homio.ro/...", "price": 193.19, "delivery": "Livrare în 1–2 zile"},
    "images": [{"src": "https://gomagcdn.ro/.../poza1.jpg"}, {"src": "https://gomagcdn.ro/.../poza2.jpg"}],
    "recipe": "wheels", "hook": "Prima ei aventură pe 2 roți", "hook_accent": "aventură", "hook_type": "pov",
    "badges": ["3 ani+", "până la 50 kg"],
    "points": [{"type": "feature", "title": "Se pliază", "sub": "în câteva secunde", "image": 1, "pills": ["doar 2 kg"]},
               {"type": "counter", "value": 50, "suffix": " kg", "label": "sarcină maximă", "image": 0}],
    "features": ["Ghidon reglabil pe 3 înălțimi", "Frână spate cu piciorul", "Platformă antiderapantă"],
    "features_title": "De ce o aleg părinții",
    "final": {"image": 0}, "season": None, "sfx": True
}

EXAMPLE_MULTI = {
    "title": "Set școală Spiderman",
    "products": [
        {"name": "Ghiozdan Spiderman", "url": "https://homio.ro/...", "price": 129.9, "label": "Ghiozdan", "images": [0]},
        {"name": "Penar Spiderman", "url": "https://homio.ro/...", "price": 39.5, "label": "Penar", "images": [1]},
        {"name": "Cutie sandwich Spiderman", "url": "https://homio.ro/...", "price": 24.99, "label": "Cutie gustare", "images": [2]}
    ],
    "multi": "combo", "character": "Spiderman",
    "images": [{"src": "https://gomagcdn.ro/.../ghiozdan.jpg"}, {"src": "https://gomagcdn.ro/.../penar.jpg"}, {"src": "https://gomagcdn.ro/.../cutie.jpg"}],
    "recipe": ["set", "toy"], "hook": "Tot setul Spiderman pentru școală", "hook_accent": "Spiderman", "hook_type": "contrast",
    "combo_title": "Totul se potrivește", "combo_pill": "3 piese",
    "points": [{"type": "detail", "title": "Penar încăpător", "image": 1, "focus": [0.5, 0.5], "zoom": 1.5}],
    "final": {}, "sfx": True
}

if __name__ == '__main__':
    main()
