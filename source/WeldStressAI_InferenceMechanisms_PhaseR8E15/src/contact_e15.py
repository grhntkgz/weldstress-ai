from common_e15 import *
from PIL import Image,ImageOps,ImageDraw

def main():
 reg=rows(R/'19_figures/FIGURE_REGISTRY.csv');assert len(reg)==38
 for part in range(2):
  subset=reg[part*19:(part+1)*19];canvas=Image.new('RGB',(2000,1200),'white');draw=ImageDraw.Draw(canvas)
  for i,a in enumerate(subset):
   with Image.open(a['PNG']) as im:thumb=ImageOps.contain(im.convert('RGB'),(395,260))
   col=i%5;row=i//5;canvas.paste(thumb,(col*400,row*300+20));draw.text((col*400+5,row*300+4),a['number']+' '+a['title'][:44],fill='black')
  canvas.save(R/'18_independent_verification'/('FIGURE_CONTACT_'+str(part+1)+'.png'))
 print('CONTACT_SHEETS_COMPLETE',flush=True)
if __name__=='__main__':main()
