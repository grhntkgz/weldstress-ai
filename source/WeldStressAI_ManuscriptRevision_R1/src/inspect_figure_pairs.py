from pathlib import Path
import json,csv
import numpy as np
from PIL import Image,ImageDraw
from pypdf import PdfReader
from pdf2image import convert_from_path
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R1');F=D/'source_snapshot'/'19_scientific_figures';out=D/'qa'/'original_pdf_previews';out.mkdir(exist_ok=True)
with (D/'source_snapshot'/'SCIENTIFIC_FIGURES.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
audit=[]
for r in rows:
 p=F/Path(r['PDF']).name;png=F/Path(r['PNG']).name;reader=PdfReader(p);assert len(reader.pages)==1;im=convert_from_path(str(p),dpi=70,first_page=1,last_page=1)[0].convert('RGB');im.save(out/f"S{int(r['number']):02}.png");original=Image.open(png).convert('RGB').resize(im.size)
 a=np.asarray(im,dtype=float).ravel();b=np.asarray(original,dtype=float).ravel();corr=float(np.corrcoef(a,b)[0,1]);audit.append(dict(number=r['number'],PDF=str(p),PNG=str(png),PDF_pages=1,pair_pixel_correlation=corr,PNG_width=Image.open(png).width,PNG_height=Image.open(png).height,status='RENDERED_FOR_VISUAL_REVIEW'))
with (D/'qa'/'ALL_35_FIGURE_PAIR_AUDIT.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(audit[0]));w.writeheader();w.writerows(audit)
for batch in range(3):
 rr=rows[batch*12:(batch+1)*12];sheet=Image.new('RGB',(1800,4*370),'white');draw=ImageDraw.Draw(sheet)
 for j,r in enumerate(rr):
  im=Image.open(out/f"S{int(r['number']):02}.png");im.thumbnail((570,330));x=(j%3)*600;y=(j//3)*370;sheet.paste(im,(x+(600-im.width)//2,y+25));draw.text((x+10,y+5),f"S{int(r['number']):02} PDF preview",fill='black')
 sheet.save(D/'qa'/f'PDF_PAIRS_CONTACT_{batch+1}.png')
print(json.dumps({'PDF_pairs':len(audit),'minimum_pair_correlation':min(x['pair_pixel_correlation'] for x in audit)}))
