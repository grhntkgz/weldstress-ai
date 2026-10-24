from common_e14 import *
from PIL import Image,ImageDraw
def main():
 paths=sorted((R/'18_figures').glob('*.png'));assert len(paths)==36
 for page,start in enumerate([0,18],1):
  canvas=Image.new('RGB',(1800,1620),'white');draw=ImageDraw.Draw(canvas)
  for j,p in enumerate(paths[start:start+18]):
   with Image.open(p) as im:t=im.convert('RGB');t.thumbnail((580,230))
   x=(j%3)*600+(600-t.width)//2;y=(j//3)*270;canvas.paste(t,(x,y));draw.text(((j%3)*600+5,y+240),p.stem[:78],fill='black')
  canvas.save(R/'17_independent_audits'/f'FIGURE_CONTACT_{page}.png')
 write(R/'17_independent_audits/VISUAL_INVENTORY.json',dict(UTC=now(),primary_pairs=36,supplemental_pairs=26,contacts=2));print('CONTACT_SHEETS_READY',flush=True)
if __name__=='__main__':main()
