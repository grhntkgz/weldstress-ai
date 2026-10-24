import numpy as np,torch
from torch import nn
from base_arch import PointTransformerStress
class SurfacePT(PointTransformerStress):
 def __init__(self,multiscale=False):
  super().__init__(features=19,width=24,layers=1);self.multiscale=multiscale
  if multiscale:self.scale_logits=nn.Parameter(torch.zeros(3))
 def forward(self,g,q):
  device=self.encoder[0].weight.device
  def t(x):return torch.as_tensor(np.asarray(x),device=device)
  f=t(g['features'][q]);h=self.encoder(f);locals=[]
  for key in (['neighbors','neighbors_1mm','neighbors_3mm'] if self.multiscale else ['neighbors']):
   nf=t(g['features'][g[key][q]]);nh=self.encoder(nf);p=self.pos[0](f[:,None,:3]-nf[:,:,:3]);alpha=torch.softmax(self.att[0](self.q[0](h)[:,None,:]-self.k[0](nh)+p),dim=1);locals.append((alpha*(self.v[0](nh)+p)).sum(1))
  local=sum(w*v for w,v in zip(torch.softmax(self.scale_logits,dim=0),locals)) if self.multiscale else locals[0]
  ctx=self.encoder(t(g['features'][g['context']])).mean(0).expand_as(h);h=self.norm[0](h+self.up[0](torch.cat([local,ctx],-1)));return self.out(h).squeeze(-1)
def build(exp,device='cpu'):return SurfacePT(exp!='S0').to(device)

