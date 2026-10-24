from setup_e11r1 import *
import numpy as np
def audit_selection():
 q=rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv');old=rows(R/'VERIFIED_V1_SOURCE_REGISTRY.csv');co=read(R/'00_integrity/COHORT_RECONCILIATION.json');assert len(co['remaining34'])==34
 ff=rows(R/'GEOMETRY_SELECTION_FEATURES.csv');sc=read(R/'03_geometry_only_selection/ROBUST_SCALING.json');mat=np.array([[float(a[k]) for k in sc['features']] for a in ff]);assert np.allclose(np.median(mat,0),sc['median'],rtol=0,atol=1e-14);assert np.allclose(np.percentile(mat,75,axis=0)-np.percentile(mat,25,axis=0),sc['IQR'],rtol=0,atol=1e-14)
 v=np.divide(mat-sc['median'],sc['IQR'],out=np.zeros_like(mat),where=np.array(sc['IQR'])>1e-12);idx={a['source_id']:i for i,a in enumerate(ff)};pr={a['source_id']:a for a in rows(R/'SOURCE_PROVENANCE_REGISTRY.csv')};refs=sorted(a['source_id'] for a in old);rem=co['remaining34'].copy();rank=rows(R/'FULL34_GEOMETRY_RANKING.csv')
 for i,z in enumerate(q,1):
  plates={pr[t]['confirmed_parent_plate'] for t in refs};dist={t:float(np.linalg.norm(v[idx[t]]-v[[idx[s] for s in refs]],axis=1).min()) for t in rem};priority={t:int(pr[t]['confirmed_parent_plate'] not in plates) for t in rem};mxp=max(priority.values());mx=max(dist[t] for t in rem if priority[t]==mxp);pick=min(t for t in rem if priority[t]==mxp and abs(dist[t]-mx)<=1e-12);assert pick==z['source_id']
  rr=[a for a in rank if int(a['round'])==i];assert {a['source_id'] for a in rr}==set(rem)
  for a in rr:assert abs(float(a['minimum_standardized_distance'])-dist[a['source_id']])<1e-12 and int(a['new_documented_parent_plate'])==priority[a['source_id']]
  refs.append(pick);rem.remove(pick)
 assert len(rank)==160
 return True
