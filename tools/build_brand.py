#!/usr/bin/env python3
"""Gera os arquivos derivados da marca Konnen a partir das artes-mestre do repositório.

Gera:
  - variantes de logo (wordmark preto e wordmark sans branco);
  - ícones em vários tamanhos + favicon.ico para a marca e para cada app;
  - imagens do guia de marca em docs/img/ e o PDF docs/konnen-brand-guidelines.pdf.

Uso:
  uv run --with pillow python tools/build_brand.py            # tudo
  uv run --with pillow python tools/build_brand.py --icons    # só logos e ícones (sem Chrome)

As imagens e o PDF usam o Google Chrome (headless) e baixam as fontes do Google Fonts.
"""
import json
import pathlib
import shutil
import subprocess
import sys

from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parent.parent
LOGO = RAIZ / 'logo'
ICONES = RAIZ / 'icons'
DOCS = RAIZ / 'docs'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

TAMANHOS = [1024, 512, 192, 180, 128, 64, 48, 32, 16]
APPS = {
    'analytics': 'Konnen Analytics',
    'ads': 'Konnen Ads',
    'chat': 'Konnen Chat',
    'threads': 'Konnen Threads',
}


def recolorir(origem: pathlib.Path, destino: pathlib.Path, cor: tuple) -> None:
    """Mantém o alfa da arte e troca todas as cores por uma cor sólida."""
    im = Image.open(origem).convert('RGBA')
    sol = Image.new('RGBA', im.size, cor + (255,))
    sol.putalpha(im.getchannel('A'))
    sol.save(destino, optimize=True)


def centralizar(arte: Image.Image, lado: int, ocupacao: float, fundo=(0, 0, 0, 0)) -> Image.Image:
    """Arte centralizada num quadrado; `ocupacao` é a fração do lado usada pela maior dimensão."""
    a = arte.copy()
    escala = lado * ocupacao / max(a.size)
    a = a.resize((round(a.width * escala), round(a.height * escala)), Image.LANCZOS)
    tela = Image.new('RGBA', (lado, lado), fundo)
    tela.alpha_composite(a, ((lado - a.width) // 2, (lado - a.height) // 2))
    return tela


def serie_de_icones(mestre: Image.Image, pasta: pathlib.Path, nome: str, opaco: Image.Image | None = None) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    for t in TAMANHOS:
        mestre.resize((t, t), Image.LANCZOS).save(pasta / f'{nome}-{t}.png', optimize=True)
    mestre.save(pasta / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    # apple-touch-icon e ícone maskable do Android pedem fundo opaco
    opaco = opaco or mestre
    fundo = Image.new('RGBA', opaco.size, (255, 255, 255, 255))
    fundo.alpha_composite(opaco)
    fundo.convert('RGB').resize((180, 180), Image.LANCZOS).save(pasta / 'apple-touch-icon.png', optimize=True)


def gerar_logos_e_icones() -> None:
    wm = LOGO / 'wordmark'
    recolorir(wm / 'konnen-wordmark-gradient.png', wm / 'konnen-wordmark-black.png', (0, 0, 0))
    recolorir(LOGO / 'wordmark-sans/konnen-wordmark-sans-black.png', LOGO / 'wordmark-sans/konnen-wordmark-sans-white.png', (255, 255, 255))

    # marca: wordmark em gradiente num quadrado (transparente) e versão opaca com zona segura
    arte = Image.open(wm / 'konnen-wordmark-gradient.png').convert('RGBA')
    mestre = centralizar(arte, 1024, 0.94)
    seguro = centralizar(arte, 1024, 0.72, (255, 255, 255, 255))
    serie_de_icones(mestre, ICONES / 'konnen', 'konnen-icon', opaco=seguro)
    seguro.convert('RGB').resize((512, 512), Image.LANCZOS).save(ICONES / 'konnen/konnen-icon-maskable-512.png', optimize=True)
    manifesto = {
        'name': 'Konnen', 'short_name': 'Konnen', 'theme_color': '#146B72', 'background_color': '#FFFFFF',
        'icons': [
            {'src': 'konnen-icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
            {'src': 'konnen-icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
            {'src': 'konnen-icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
        ],
    }
    (ICONES / 'konnen/site.webmanifest').write_text(json.dumps(manifesto, indent=2) + '\n', encoding='utf-8')

    # apps: a arte de 1024 px já é o mestre; o fundo do próprio ícone é opaco
    for app in [*APPS, 'app-base']:
        pasta = ICONES / app
        mestre_app = Image.open(pasta / f'konnen-{app}-1024.png').convert('RGBA')
        serie_de_icones(mestre_app, pasta, f'konnen-{app}')
    print('logos e ícones gerados')


# ---------- guia de marca (HTML -> PNG e PDF) ----------
FONTES = ('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,700;12..96,800'
          '&family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=block')

CORES_LOGO = [('Verde Água', 'Aqua Green', '#4B9F82'), ('Cerceta', 'Teal', '#2C7D90'), ('Azul Médio', 'Medium Blue', '#25659B'),
              ('Azul Ardósia', 'Slate Blue', '#4F6D7B'), ('Dourado', 'Bronze Gold', '#A18445')]
CORES_WEB = [('Teal', '#146B72'), ('Blue', '#0F4E86'), ('Gold', '#9C7A2E'), ('Ground', '#F6F8F7'), ('Card', '#FFFFFF'),
             ('Ink', '#142A2C'), ('Muted', '#5B6E6D'), ('Line', '#DBE4E3'), ('Accent soft', '#E1EEEC')]
CORES_WEB_ESCURO = [('Teal', '#4FC3B8'), ('Blue', '#5FA8E8'), ('Gold', '#E0BB5C'), ('Ground', '#0E1513'), ('Card', '#14201E'),
                    ('Ink', '#E8EDEC'), ('Muted', '#93A6A3'), ('Line', '#253634'), ('Accent soft', '#1A2E2B')]
CORES_APOIO = [('Verde floresta · wordmark', 'Forest green · wordmark', '#103A16')]
G_LOGO = 'linear-gradient(90deg,#4B9F82 0%,#2C7D90 25%,#25659B 50%,#4F6D7B 75%,#A18445 100%)'
G_PADRAO = 'linear-gradient(100deg,#146B72,#0F4E86 60%,#9C7A2E)'
G_ESCURO = 'linear-gradient(100deg,#4FC3B8,#5FA8E8 60%,#E0BB5C)'

CSS = """
@page{size:1600px 900px;margin:0}
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
html,body{margin:0;background:#F6F8F7}
.s{width:1600px;height:900px;padding:64px 80px;display:flex;flex-direction:column;gap:34px;background:#F6F8F7;color:#142A2C;
  font:400 18px/1.5 'Public Sans',sans-serif;position:relative;overflow:hidden;page-break-after:always}
.s::before{content:"";position:absolute;inset:0 0 auto;height:8px;background:""" + G_LOGO + """}
.hd{display:flex;justify-content:space-between;align-items:flex-end;gap:40px}
.eb{font:500 15px 'IBM Plex Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#146B72}
h1{margin:8px 0 0;font:800 60px/1 'Bricolage Grotesque',sans-serif;letter-spacing:-.025em}
h1 small{display:block;margin-top:10px;font:400 22px 'Public Sans',sans-serif;letter-spacing:0;color:#5B6E6D}
.mono{font:500 14px 'IBM Plex Mono',monospace;color:#5B6E6D}
.grid{display:grid;gap:22px;flex:1;min-height:0}
.card{border-radius:20px;border:1px solid #DBE4E3;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;position:relative;overflow:hidden}
.card img{max-width:78%;max-height:58%;object-fit:contain}
.card .cap{position:absolute;left:20px;bottom:16px;font:500 13px 'IBM Plex Mono',monospace;opacity:.75}
.no{position:absolute;right:18px;top:16px;width:44px;height:44px;border-radius:50%;background:#C2352B;color:#fff;display:grid;place-items:center;font:700 26px 'Public Sans'}
.ok{background:#2E8B57}
.sw{border-radius:18px;padding:18px 20px;display:flex;flex-direction:column;justify-content:flex-end;min-height:0}
.sw b{font:700 21px 'Public Sans'}.sw span{font:500 15px 'IBM Plex Mono',monospace;opacity:.9}
.chip{display:flex;flex-direction:column;gap:6px}
.chip i{height:84px;border-radius:14px;border:1px solid rgba(0,0,0,.08)}
.chip b{font:600 15px 'Public Sans'}.chip span{font:500 13px 'IBM Plex Mono',monospace;color:#5B6E6D}
.bar{height:96px;border-radius:18px;display:flex;align-items:flex-end;padding:14px 20px;color:#fff;font:500 15px 'IBM Plex Mono',monospace}
"""


def rgb(h: str) -> str:
    h = h.lstrip('#')
    return ', '.join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def tinta(h: str) -> str:
    h = h.lstrip('#')
    h = ''.join(c * 2 for c in h) if len(h) == 3 else h
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return '#142A2C' if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.55 else '#FFFFFF'


def secao(eyebrow: str, titulo: str, subtitulo: str, corpo: str, extra: str = '') -> str:
    return (f'<section class="s"><div class="hd"><div><div class="eb">{eyebrow}</div><h1>{titulo}<small>{subtitulo}</small></h1></div>'
            f'{extra}</div>{corpo}</section>')


def secoes(u) -> dict:
    """u(caminho) -> URI do arquivo no repositório."""
    wm = lambda v: u(f'logo/wordmark/konnen-wordmark-{v}.png')
    S = {}
    apps = ''.join(f'<img src="{u(f"icons/{a}/konnen-{a}-512.png")}" style="width:118px;height:118px">' for a in APPS)
    S['overview'] = secao('Konnen · Brand resources', 'Recursos de marca Konnen', 'Konnen brand resources · logo, cores, tipografia e ícones', f"""
<div style="flex:1;display:grid;grid-template-columns:1.5fr 1fr;gap:26px">
 <div class="card" style="background:#fff"><img src="{wm('gradient')}" style="max-width:72%;max-height:70%"></div>
 <div style="display:grid;grid-template-rows:1fr auto;gap:26px">
  <div class="card" style="background:url({u('wallpapers/konnen-wallpaper-waves-soft.jpg')}) center/cover"><img src="{wm('white')}" style="max-width:70%"></div>
  <div style="display:flex;gap:16px;justify-content:space-between">{apps}</div>
 </div>
</div>
<div style="display:flex;height:22px;border-radius:99px;overflow:hidden">{''.join(f'<i style="flex:1;background:{h}"></i>' for *_, h in CORES_LOGO)}</div>""")

    versoes = [('gradient', '#FFFFFF', 'Principal · Primary'), ('darkgreen', '#F4EEDC', 'Verde floresta · Forest green'),
               ('white', '#142A2C', 'Negativo · Reversed'), ('black', '#FFFFFF', 'Monocromático · Monochrome'),
               ('white', f'url({u("wallpapers/konnen-wallpaper-waves.jpg")}) center/cover', 'Sobre imagem · On imagery')]
    cards = ''.join(f'<div class="card" style="background:{bg};color:{tinta(bg) if bg.startswith("#") else "#fff"}"><img src="{wm(v)}">'
                    f'<span class="cap">{rot} · konnen-wordmark-{v}.png</span></div>' for v, bg, rot in versoes)
    cards += (f'<div class="card" style="background:#FFFFFF"><img src="{u("logo/wordmark-sans/konnen-wordmark-sans-black.png")}" style="max-width:66%">'
              f'<span class="cap">Alternativa sans · Sans alternate · konnen-wordmark-sans-black.png</span></div>')
    S['logo-versions'] = secao('01 · Logo', 'Versões do logo', 'Logo versions · use o gradiente sempre que o fundo permitir',
                              f'<div class="grid" style="grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr">{cards}</div>')

    S['clear-space'] = secao('02 · Logo', 'Área de proteção e tamanho mínimo', 'Clear space & minimum size · x = 1/4 da altura do logo', f"""
<div class="grid" style="grid-template-columns:1.25fr 1fr">
 <div class="card" style="background:#fff">
  <div style="position:relative;padding:55px;border:2px dashed #146B72;border-radius:6px">
   <div style="position:absolute;inset:55px;border:1px solid #9C7A2E;opacity:.5"></div>
   <img src="{wm('gradient')}" style="display:block;width:520px;max-width:none;max-height:none;position:relative">
   <span style="position:absolute;left:0;top:50%;width:55px;text-align:center;transform:translateY(-50%);font:700 22px 'IBM Plex Mono';color:#146B72">x</span>
   <span style="position:absolute;right:0;top:50%;width:55px;text-align:center;transform:translateY(-50%);font:700 22px 'IBM Plex Mono';color:#146B72">x</span>
   <span style="position:absolute;top:0;left:50%;height:55px;line-height:55px;transform:translateX(-50%);font:700 22px 'IBM Plex Mono';color:#146B72">x</span>
   <span style="position:absolute;bottom:0;left:50%;height:55px;line-height:55px;transform:translateX(-50%);font:700 22px 'IBM Plex Mono';color:#146B72">x</span>
  </div>
  <span class="cap">x = 1/4 da altura do logo · ¼ of the logo height</span>
 </div>
 <div class="card" style="background:#fff;align-items:flex-start;padding:40px 46px;gap:26px">
  <div class="eb" style="color:#5B6E6D">Mínimo · Minimum</div>
  <div style="display:flex;align-items:flex-end;gap:34px">
   <div class="chip"><img src="{wm('gradient')}" style="width:240px;max-width:none;max-height:none"><span>240 px</span></div>
   <div class="chip"><img src="{wm('gradient')}" style="width:140px;max-width:none;max-height:none"><span>140 px</span></div>
   <div class="chip"><img src="{wm('gradient')}" style="width:80px;max-width:none;max-height:none"><span>80 px · min</span></div>
  </div>
  <div style="font-size:19px;line-height:1.6">Tela: largura mínima de <b>80 px</b><br>Impressão: largura mínima de <b>20 mm</b><br>
  Abaixo disso, use o <b>ícone</b> da marca.</div>
  <div style="display:flex;align-items:flex-end;gap:22px">{''.join(f'<div class="chip"><img src="{u(f"icons/konnen/konnen-icon-{t}.png")}" style="width:{t}px;height:{t}px;max-width:none;max-height:none;border:1px solid #DBE4E3;border-radius:6px"><span>{t}</span></div>' for t in (64, 32, 16))}</div>
 </div>
</div>""")

    erro = lambda estilo, legenda, bg='#fff', img=None: (
        f'<div class="card" style="background:{bg}"><img src="{img or wm("gradient")}" style="{estilo}"><span class="no">✕</span>'
        f'<span class="cap" style="color:{tinta(bg) if bg.startswith("#") else "#fff"}">{legenda}</span></div>')
    S['misuse'] = secao('03 · Logo', 'Usos incorretos', "Don'ts · não altere, distorça nem recoloque o logo", f"""
<div class="grid" style="grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr">
{erro('transform:scaleX(1.35)', 'Não distorça · Don’t stretch')}
{erro('transform:rotate(-14deg)', 'Não gire · Don’t rotate')}
{erro('filter:hue-rotate(150deg) saturate(1.6)', 'Não troque as cores · Don’t recolor')}
{erro('filter:drop-shadow(8px 10px 0 #E0BB5C) drop-shadow(0 0 18px #ff00aa)', 'Sem sombras ou efeitos · No effects')}
{erro('', 'Sem fundos poluídos · No busy backgrounds', f'url({u("wallpapers/konnen-wallpaper-lemonade.jpg")}) center/cover')}
{erro('', 'Sem baixo contraste · No low contrast', '#F6F8F7', wm('white'))}
</div>""")

    grandes = ''.join(f'<div class="sw" style="background:{h};color:{tinta(h)}"><b>{pt} · {en}</b><span>{h} · RGB {rgb(h)}</span></div>'
                      for pt, en, h in CORES_LOGO)
    chips = lambda lst: ''.join(f'<div class="chip"><i style="background:{h}"></i><b>{n}</b><span>{h}</span></div>' for n, h in lst)
    S['colors'] = secao('04 · Cores', 'Paleta de cores', 'Color palette · cores da logo e tokens do site (claro e escuro)', f"""
<div class="grid" style="grid-template-rows:1.35fr auto auto;gap:24px">
 <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:16px">{grandes}</div>
 <div><div class="eb" style="margin-bottom:10px;color:#5B6E6D">Web · tema claro · light</div><div style="display:grid;grid-template-columns:repeat(9,1fr);gap:14px">{chips(CORES_WEB)}</div></div>
 <div><div class="eb" style="margin-bottom:10px;color:#5B6E6D">Web · tema escuro · dark</div><div style="display:grid;grid-template-columns:repeat(9,1fr);gap:14px">{chips(CORES_WEB_ESCURO)}</div></div>
</div>""".replace('height:84px', 'height:56px'))

    S['gradients'] = secao('05 · Cores', 'Gradientes', 'Gradients · do frio ao quente, sempre na horizontal', f"""
<div style="display:grid;gap:22px;flex:1;align-content:start">
 <div><div class="bar" style="background:{G_LOGO};height:150px">Logo · 90deg · #4B9F82 0% → #2C7D90 25% → #25659B 50% → #4F6D7B 75% → #A18445 100%</div></div>
 <div><div class="bar" style="background:{G_PADRAO};height:150px">Padrão web · --k-gradient · 100deg · #146B72 → #0F4E86 60% → #9C7A2E</div></div>
 <div><div class="bar" style="background:{G_ESCURO};height:150px;color:#0E1513">Modo escuro · dark mode · 100deg · #4FC3B8 → #5FA8E8 60% → #E0BB5C</div></div>
 <div style="font-size:19px;color:#5B6E6D">Use em hero, banners, botões primários e textos grandes. Evite em textos pequenos ou longos.
 <br>Use in heroes, banners, primary buttons and large text. Avoid on small or long text.</div>
</div>""")

    fonte = lambda nome, papel, pesos, estilo, amostra, uso: f"""
<div class="card" style="background:#fff;align-items:flex-start;justify-content:flex-start;padding:36px 38px;gap:16px">
 <div class="eb">{papel}</div>
 <div style="{estilo};font-size:112px;line-height:1">Aa</div>
 <div style="font:700 26px 'Public Sans'">{nome}</div>
 <div class="mono">{pesos}</div>
 <div style="{estilo};font-size:25px;line-height:1.25">{amostra}</div>
 <div style="font-size:16px;color:#5B6E6D;margin-top:auto">{uso}</div>
</div>"""
    S['typography'] = secao('06 · Tipografia', 'Tipografia', 'Typography · três famílias do Google Fonts (licença OFL)', f"""
<div class="grid" style="grid-template-columns:repeat(3,1fr)">
{fonte('Bricolage Grotesque', 'Títulos · Display', '700 Bold · 800 ExtraBold', "font-family:'Bricolage Grotesque';font-weight:800;letter-spacing:-.02em", 'Inteligência para suas redes', 'h1, h2 e chamadas. Tracking −0,02em.<br>Headlines and hero copy.')}
{fonte('Public Sans', 'Corpo · Body', '400 · 500 · 600', "font-family:'Public Sans';font-weight:400", 'Relatórios claros, com fonte e data em cada número.', 'Parágrafos e interface.<br>Paragraphs and UI text.')}
{fonte('IBM Plex Mono', 'Técnica · Technical', '400 · 500', "font-family:'IBM Plex Mono';font-weight:500;text-transform:uppercase;letter-spacing:.1em", 'Tags · badges · eyebrows', 'Rótulos em caixa alta, tracking 0,08–0,14em.<br>Uppercase labels.')}
</div>""")

    tam = ''.join(f'<div class="chip" style="align-items:center"><img src="{u(f"icons/konnen/konnen-icon-{t}.png")}" style="width:{min(t, 128)}px;height:{min(t, 128)}px;max-width:none;max-height:none;object-fit:contain;border:1px solid #DBE4E3;border-radius:{max(3, min(t, 128) // 5)}px;background:#fff"><span>{t} px</span></div>'
                  for t in (512, 192, 128, 64, 32, 16))
    app_cards = ''.join(f'<div class="chip" style="align-items:center"><img src="{u(f"icons/{a}/konnen-{a}-512.png")}" style="width:150px;height:150px"><b>{n}</b><span>icons/{a}/</span></div>'
                        for a, n in APPS.items())
    S['icons'] = secao('07 · Ícones', 'Ícones', 'Icons · marca e apps, de 16 a 1024 px, com favicon.ico', f"""
<div class="grid" style="grid-template-rows:auto 1fr;gap:26px">
 <div class="card" style="background:#fff;flex-direction:row;justify-content:space-around;align-items:flex-end;padding:30px">{tam}</div>
 <div class="card" style="background:#fff;flex-direction:row;justify-content:space-around">{app_cards}</div>
</div>""")

    masc = [('gradient', '#FFFFFF'), ('color', '#F6F8F7'), ('black', '#E1EEEC'), ('black-outline', '#F4EEDC')]
    m_cards = ''.join(f'<div class="card" style="background:{bg}"><img src="{u(f"mascot/konnen-mascot-{v}.png")}" style="max-height:64%">'
                      f'<span class="cap">konnen-mascot-{v}.png</span></div>' for v, bg in masc)
    S['mascot'] = secao('08 · Mascote secundário', 'Mascote: a onça', 'Secondary mascot · não é logo e nunca o substitui', f"""
<div class="grid" style="grid-template-columns:repeat(4,1fr);grid-template-rows:1fr auto">{m_cards}
<div style="grid-column:1/-1;font-size:19px;color:#5B6E6D">A onça é <b style="color:#142A2C">secundária</b>: ilustra conteúdos, stickers e estados vazios, sempre acompanhada do logo e nunca no lugar dele.
<br>The jaguar is <b style="color:#142A2C">secondary</b>: use it for illustrations, stickers and empty states, always alongside — never instead of — the logo.</div></div>""")

    wps = ''.join(f'<div class="card" style="background:url({u(f"wallpapers/konnen-wallpaper-{w}.jpg")}) center/cover;border:0">'
                  f'<span class="cap" style="color:#fff;background:rgba(0,0,0,.35);padding:3px 8px;border-radius:6px">konnen-wallpaper-{w}.jpg</span></div>'
                  for w in ('waves', 'waves-soft', 'glass', 'lemonade'))
    S['wallpapers'] = secao('09 · Imagens', 'Wallpapers', 'Wallpapers · fundos nas cores da marca',
                            f'<div class="grid" style="grid-template-columns:repeat(4,1fr)">{wps}</div>')
    return S


def chrome(*args) -> None:
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                    '--virtual-time-budget=15000', '--run-all-compositor-stages-before-draw', *args], check=True, capture_output=True)


def gerar_guia() -> None:
    build = RAIZ / 'tools/.build'
    build.mkdir(parents=True, exist_ok=True)
    (DOCS / 'img').mkdir(parents=True, exist_ok=True)
    S = secoes(lambda p: (RAIZ / p).as_uri())
    cabeca = f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><link rel="stylesheet" href="{FONTES}"><style>{CSS}</style></head><body>'
    for nome, html_secao in S.items():
        arq = build / f'{nome}.html'
        arq.write_text(cabeca + html_secao + '</body></html>', encoding='utf-8')
        destino = DOCS / f'img/{nome}.png'
        chrome('--window-size=1600,900', '--force-device-scale-factor=1', f'--screenshot={destino}', arq.as_uri())
        Image.open(destino).convert('RGB').save(destino, optimize=True)
    guia = build / 'guia.html'
    guia.write_text(cabeca + ''.join(S.values()) + '</body></html>', encoding='utf-8')
    chrome('--no-pdf-header-footer', f'--print-to-pdf={DOCS / "konnen-brand-guidelines.pdf"}', guia.as_uri())
    shutil.rmtree(build)
    print(f'guia gerado: {len(S)} imagens em docs/img e docs/konnen-brand-guidelines.pdf')


if __name__ == '__main__':
    gerar_logos_e_icones()
    if '--icons' not in sys.argv:
        gerar_guia()
