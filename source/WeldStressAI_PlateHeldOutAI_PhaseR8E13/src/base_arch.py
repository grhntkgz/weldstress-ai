"""Untrained, inspectable static field regressors. No pretrained stress accuracy is implied.
MGN-inspired graph model; vector-attention Point Transformer; explicit GNO/FNO/GNO
geometry-aware operator alternative (unsigned surface-distance encoding, not a full official GINO reproduction).
"""
import torch
from torch import nn
def mlp(a,b,c):return nn.Sequential(nn.Linear(a,b),nn.GELU(),nn.Linear(b,c))
class GeometryMLP(nn.Module):
 def __init__(self,features=12,width=64):super().__init__();self.net=nn.Sequential(mlp(features,width,width),nn.GELU(),nn.Linear(width,1))
 def forward(self,features,**kw):return self.net(features).squeeze(-1)
class MeshGraphStress(nn.Module):
 def __init__(self,features=12,width=48,layers=6):
  super().__init__();self.encoder=mlp(features,width,width);self.messages=nn.ModuleList([mlp(width*2+4,width,width) for _ in range(layers)]);self.updates=nn.ModuleList([mlp(width*3,width,width) for _ in range(layers)]);self.norms=nn.ModuleList([nn.LayerNorm(width) for _ in range(layers)]);self.out=mlp(width,width,1)
 def forward(self,features,xyz,edge_index,**kw):
  h=self.encoder(features);i,j=edge_index;delta=xyz[j]-xyz[i];ef=torch.cat([delta,delta.norm(dim=-1,keepdim=True)],-1)
  for msg,update,norm in zip(self.messages,self.updates,self.norms):
   m=msg(torch.cat([h[i],h[j],ef],-1));agg=torch.zeros_like(h).index_add_(0,i,m);degree=torch.zeros(len(h),device=h.device).index_add_(0,i,torch.ones(len(i),device=h.device));agg=agg/degree.clamp_min(1)[:,None];glob=h.mean(0).expand_as(h);h=norm(h+update(torch.cat([h,agg,glob],-1)))
  return self.out(h).squeeze(-1)
class PointTransformerStress(nn.Module):
 def __init__(self,features=12,width=48,layers=4):
  super().__init__();self.encoder=mlp(features,width,width);self.q=nn.ModuleList([nn.Linear(width,width) for _ in range(layers)]);self.k=nn.ModuleList([nn.Linear(width,width) for _ in range(layers)]);self.v=nn.ModuleList([nn.Linear(width,width) for _ in range(layers)]);self.pos=nn.ModuleList([mlp(3,width,width) for _ in range(layers)]);self.att=nn.ModuleList([mlp(width,width,width) for _ in range(layers)]);self.up=nn.ModuleList([mlp(width*2,width,width) for _ in range(layers)]);self.norm=nn.ModuleList([nn.LayerNorm(width) for _ in range(layers)]);self.out=mlp(width,width,1)
 def forward(self,features,xyz,neighbors,**kw):
  h=self.encoder(features);delta=xyz[:,None,:]-xyz[neighbors]
  for q,k,v,pos,att,up,norm in zip(self.q,self.k,self.v,self.pos,self.att,self.up,self.norm):
   p=pos(delta);alpha=torch.softmax(att(q(h)[:,None,:]-k(h)[neighbors]+p),dim=1);local=(alpha*(v(h)[neighbors]+p)).sum(1);h=norm(h+up(torch.cat([local,h.mean(0).expand_as(h)],-1)))
  return self.out(h).squeeze(-1)
class Spectral3D(nn.Module):
 def __init__(self,width=16,modes=3):
  super().__init__();self.m=modes;self.weights=nn.Parameter(torch.randn(4,width,width,modes,modes,modes,dtype=torch.cfloat)/(width**2));self.local=nn.Conv3d(width,width,1)
 def forward(self,x):
  f=torch.fft.rfftn(x,dim=(-3,-2,-1));y=torch.zeros_like(f);m=self.m
  for z,(a,b) in enumerate([(slice(0,m),slice(0,m)),(slice(-m,None),slice(0,m)),(slice(0,m),slice(-m,None)),(slice(-m,None),slice(-m,None))]):y[:,:,a,b,:m]=torch.einsum('bixyz,ioxyz->boxyz',f[:,:,a,b,:m],self.weights[z])
  return torch.nn.functional.gelu(torch.fft.irfftn(y,s=x.shape[-3:],dim=(-3,-2,-1))+self.local(x))
class GeometryAwareOperator(nn.Module):
 def __init__(self,features=12,width=16,grid_size=8,modes=3,layers=3):
  super().__init__();self.grid=grid_size;self.width=width;self.encoder=mlp(features,width,width);self.in_kernel=mlp(4,width,width);self.geometry=mlp(1,width,width);self.spectral=nn.Sequential(*[Spectral3D(width,modes) for _ in range(layers)]);self.out_kernel=mlp(4,width,width);self.decoder=mlp(width,width,1)
 def forward(self,features,xyz,latent_xyz,input_edges,output_edges,vertex_area,latent_distance,**kw):
  h=self.encoder(features);src,dst=input_edges;delta=xyz[src]-latent_xyz[dst];kernel=self.in_kernel(torch.cat([delta,delta.norm(dim=-1,keepdim=True)],-1));w=vertex_area[src];acc=torch.zeros((len(latent_xyz),self.width),device=h.device).index_add_(0,dst,h[src]*kernel*w[:,None]);den=torch.zeros(len(latent_xyz),device=h.device).index_add_(0,dst,w);acc=acc/den.clamp_min(1e-12)[:,None]+self.geometry(latent_distance[:,None]);grid=acc.T.reshape(1,self.width,self.grid,self.grid,self.grid);lat=self.spectral(grid).reshape(self.width,-1).T;src,dst=output_edges;delta=latent_xyz[src]-xyz[dst];kernel=self.out_kernel(torch.cat([delta,delta.norm(dim=-1,keepdim=True)],-1));out=torch.zeros_like(h).index_add_(0,dst,lat[src]*kernel);den=torch.zeros(len(h),device=h.device).index_add_(0,dst,torch.ones(len(src),device=h.device));out=out/den.clamp_min(1)[:,None];return self.decoder(out).squeeze(-1)
MODELS={'baseline':GeometryMLP,'gnn':MeshGraphStress,'point_transformer':PointTransformerStress,'gino_alternative':GeometryAwareOperator}
