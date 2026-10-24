from common_e13 import *
from PIL import Image,ImageOps,ImageDraw
def main():
 paths=sorted((R/'14_figures').glob('*.png'));assert len(paths)==36
 for page,start in enumerate([0,18],1):
  panel=Image.new('RGB',(1800,6*270),'white');draw=ImageDraw.Draw(panel)
  for j,p in enumerate(paths[start:start+18]):
   with Image.open(p) as im:
    thumb=im.convert('RGB');thumb.thumbnail((580,235));x=(j%3)*600+(600-thumb.width)//2;y=(j//3)*270;panel.paste(thumb,(x,y));draw.text(((j%3)*600+8,y+240),p.stem[:75],fill='black')
  panel.save(R/'21_reproducibility'/f'FIGURE_QA_CONTACT_{page}.png')
 write(R/'21_reproducibility/VISUAL_ARTIFACT_INVENTORY.json',dict(UTC=now(),figure_pairs=36,contact_pages=2,paths=[str(p) for p in paths],scope='PNG/PDF checks plus human-readable rendered contact sheet review; no model or metric change'))
 print('VISUAL_QA_CONTACTS_READY',flush=True)
if __name__=='__main__':main()
