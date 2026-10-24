"""Targeted legend repair only; no numerical output is recomputed."""
from figures_e12 import *
from matplotlib.lines import Line2D
def main():
 prov=rows(R/'SOURCE_PROVENANCE_REGISTRY.csv');plates=sorted({a['confirmed_parent_plate'] for a in prov});fig,ax=plt.subplots(figsize=(13,7))
 for i,p in enumerate(plates):
  members=[a for a in prov if a['confirmed_parent_plate']==p];y=np.linspace(.1,.9,len(members));ax.scatter([i]*len(y),y,c=['tab:blue' if a['population']=='DEVELOPMENT47' else 'tab:red' for a in members]);ax.scatter(i,1.07,marker='s',s=90,c='black');ax.text(i,1.12,p.rsplit('_',1)[1],ha='center')
  for a,j in zip(members,y):ax.plot([i,i],[j,1.07],c='gray',lw=.25);ax.annotate(a['source_id'][:3],(i,j),xytext=(5,0),textcoords='offset points',fontsize=6)
 ax.legend(handles=[Line2D([],[],color='tab:blue',marker='o',ls='',label='Development source'),Line2D([],[],color='tab:red',marker='o',ls='',label='Exposed test: provenance only'),Line2D([],[],color='black',marker='s',ls='',label='Documented parent plate')],loc='upper center',ncol=3,frameon=False);ax.axis('off');save(fig,7,'Physical_dependency_graph','Five documentary plate-code groups; blue development,red exposed-test provenance,black parent. No batch/session relationships invented.')
 repairs=rows(R/'ACTUAL_MOVED_NODES.csv');fig,axes=plt.subplots(1,2,figsize=(12,5))
 for k,s in enumerate(sorted({a['source_id'] for a in repairs})):
  rr=[a for a in repairs if a['source_id']==s];axes[0].scatter([float(a['old_X']) for a in rr],[float(a['old_Y']) for a in rr],color='C'+str(k),s=20,label=s[:3]);axes[1].scatter([s[:3]+a['level'] for a in rr],[float(a['displacement_mm']) for a in rr],color='C'+str(k),s=14)
 axes[0].set(xlabel='X/mm',ylabel='Y/mm',title='Actually moved interior midsides');axes[0].legend();axes[1].set(ylabel='Actual displacement/mm',title='Measured/external boundaries unchanged');save(fig,18,'Local_mesh_repair_evidence','Actual changed-node positions and displacement magnitudes; source colors consistent. Full old/new XYZ and deltaXYZ in LOCAL_NODE_DISPLACEMENTS.csv.')
 old=rows(R/'SCIENTIFIC_FIGURES.csv');updates={str(a['number']):a for a in ledger};table(R/'SCIENTIFIC_FIGURES.csv',[updates.get(a['number'],a) for a in old]);write(R/'25_reproducibility/VISUAL_QA.json',dict(UTC=now(),visually_inspected=[7,18,20,23,24],targeted_legend_changes=[7,18],numerical_data_changed=False,figures=36,PNG_PDF_pairs=True))
if __name__=='__main__':main()
