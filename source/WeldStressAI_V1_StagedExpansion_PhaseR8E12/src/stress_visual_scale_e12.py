"""Comparable display ranges; all stress values remain unchanged."""
from figures_e12 import *
def main():
 sids=[a['source_id'] for a in rows(R/'NEW_QUALIFIED_V1_TARGET_REGISTRY.csv')]
 for n,title,key in [(22,'Original_source_M1_T2','M1'),(23,'Original_source_M2_T2','M2'),(24,'Original_source_T2_difference','difference')]:
  fig,axes=plt.subplots(len(sids),1,figsize=(11,2.7*len(sids)),squeeze=False)
  for i,s in enumerate(sids):
   c=R/'cases'/s;d=np.load(c/'13_numerical_qualification/COMPARISON_FIELDS.npz');mask=d['common'];x=d['xyz'];t=np.load(c/'01_frozen_protocol/source/triangles.npy');a=d['M1'];b=d['M2'];v=b-a if key=='difference' else a if key=='M1' else b
   if key=='difference':m=max(float(abs(v[mask]).max()),1e-6);limits=(-m,m)
   else:limits=(min(float(a[mask].min()),float(b[mask].min())),max(float(a[mask].max()),float(b[mask].max())))
   field(axes[i,0],x,t,np.where(mask,v,np.nan),s[:3],cmap='coolwarm' if key=='difference' else 'viridis',limits=limits)
  save(fig,n,title,'Identical per-source M1/M2 color ranges; difference color scale symmetric about zero. Original data unchanged; white zero, blue negative,red positive. Actual halo/core support audited separately.')
 old=rows(R/'SCIENTIFIC_FIGURES.csv');updates={str(a['number']):a for a in ledger};table(R/'SCIENTIFIC_FIGURES.csv',[updates.get(a['number'],a) for a in old]);write(R/'25_reproducibility/STRESS_VISUAL_QA.json',dict(UTC=now(),targeted_figures=[22,23,24],changes='Common per-source mesh-comparison scales and zero-centered symmetric difference colors only',stress_values_or_targets_changed=False,native_solutions_repeated=0))
if __name__=='__main__':main()
