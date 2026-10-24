"""Non-target provenance audit. No historical test targets or prediction files opened."""
from setup_e11r1 import R,B,E9,read,rows,write,table,now,sha
from pathlib import Path
import numpy as np,json,zipfile,itertools,hashlib,re
DATA=B.parent/'WeldScan-FEA/data';E3=B/'WeldStressAI_SingleSurface_Transfer_PhaseR8E3'
def main():
 declaration=R/'01_provenance/FORENSIC_SCREEN_PREREGISTRATION.json'
 if not declaration.exists():write(declaration,dict(UTC=now(),metrics=['exact original member SHA256','canonical XYZ SHA256','triangle connectivity SHA256','translation-normalized rounded XYZ fingerprint 1e-6mm','fixed-grid affine-detrended relief RMS/P95/correlation for original and X/Y/XY mirror','rigid-invariant fixed point-distance signature','fixed repeated-window offsets'],thresholds=dict(possible_duplicate_RMS_mm=.005,possible_duplicate_P95_mm=.010,correlation_min=.999,exact_fingerprint_decimals=6),window_offsets_samples=[[0,0],[-100,0],[100,0],[0,-4],[0,4]],window_crop='X100:-100,Y4:-4, common fixed overlap',registration='No fitted rigid or nonrigid registration. Subtract least-squares plane once per front; only fixed grid reflection/offsets. Distance signature uses 256 seed20261021 index pairs; fingerprint diagnostic only.',conclusion='POSSIBLE_DEPENDENCY_FLAG only; no geometric result certifies common origin or independence',historical_test_geometry_screen=False))
 q=read(E3/'00_protocol/QUARANTINE.json');dev=q['development_IDs'];test=q['historical_test_IDs'];assert len(dev)==47 and len(test)==12 and not set(dev)&set(test)
 meta=rows(DATA/'metadata/metadata.csv');scan=rows(DATA/'metadata/scan_files.csv');registry=rows(E9/'HISTORICAL_DATASET_REGISTRY.csv');reg={a['specimen_id']:a for a in registry};doc=DATA/'metadata/dissertation_extracted.txt';text=doc.read_text(encoding='utf-8-sig')
 assert 'steel plate code, which was' in text and 'location of the specimen in the welded' in text
 evidence=[];nodes=[];edges=[];sources=[];unresolved=[];hashes=[];groups={};archive=DATA/'raw/scan_geometry.zip';audit=now()
 for p in [doc,DATA/'metadata/dissertation.pdf',DATA/'raw/readme.md',DATA/'metadata/metadata.csv',DATA/'metadata/scan_files.csv',DATA/'metadata/repository.json']:
  hashes.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,kind='ORIGINAL_NON_TARGET_PROVENANCE'))
 with zipfile.ZipFile(archive) as z:
  for sid in sorted(dev+test):
   m=[a for a in meta if a['SpecimenName']==sid];s=[a for a in scan if a['SpecimenName']==sid];scan_rows_original=len(s);s=list({json.dumps(a,sort_keys=True):a for a in s}.values());assert len(s)==1,(sid,len(s))
   if not m:m=[a for a in meta if a['SpecimenName'].rsplit('-',1)[0]==sid.rsplit('-',1)[0]]
   assert m and len({(a['Material'],a['Geometry'],a['Thickness_mm']) for a in m})==1,(sid,m);m=m[0];s=s[0];match=re.fullmatch(r'([A-Z]+)(\d+)-V1-S355-AW',sid);assert match
   plate='ORIGINAL_S355MLO_PLATE_'+match[1];coupon='COUPON_'+match[1]+match[2]+'_V1_S355';groups.setdefault(plate,[]).append(sid)
   nodes.extend([dict(id=sid,type='SourceGeometry',population='DEVELOPMENT' if sid in dev else 'EXPOSED_TEST_PROVENANCE_ONLY'),dict(id=coupon,type='PhysicalCoupon',basis='Documented nomenclature; not independently reidentified by laboratory records')])
   for target,relation in [(coupon,'SOURCE_FROM_DOCUMENTED_COUPON'),(plate,'CONFIRMED_SAME_PARENT_PLATE')]:
    edges.append(dict(source_entity=sid,target_entity=target,relationship_type=relation,evidence_file=str(doc),evidence_field='Section3.2.6/Figure3.9 PDFpage56; prefix=steelplatecode, number=position',classification='CONFIRMED_SAME_PARENT_PLATE' if target==plate else 'CONFIRMED_SAME_PHYSICAL_SPECIMEN',verified=True,mandatory_grouping=True,audit_timestamp=audit))
   sourcehash={}
   for field in ['ScanFileFrontRaw','ScanFileBackRaw','ScanFileFrontProcessed','ScanFileBackProcessed']:
    name=s[field].replace('\\','/').removeprefix('./');info=z.getinfo(name);blob=z.read(info);h=hashlib.sha256(blob).hexdigest();sourcehash[field]=h;node='SCAN:'+name
    nodes.append(dict(id=node,type='ScanFile',sha256=h,zip_member_timestamp=list(info.date_time),timestamp_is_acquisition=False,bytes=info.file_size))
    edges.append(dict(source_entity=node,target_entity=coupon,relationship_type='DOCUMENTED_SCAN_FILE_MAPPING',evidence_file=str(DATA/'metadata/scan_files.csv'),evidence_field=field+':'+sid,classification='CONFIRMED_SAME_PHYSICAL_SPECIMEN',verified=True,mandatory_grouping=True,audit_timestamp=audit))
    evidence.append(dict(source_id=sid,field=field,value=name,sha256=h,evidence_file=str(DATA/'metadata/scan_files.csv'),classification='DOCUMENTED_FILE_MAPPING',note='ZIP timestamp is packaging metadata, not scan-session proof'))
   gp=Path(reg[sid]['package_path'])/'geometry_provenance.json';g=read(gp);assert g['source_hashes']['front']==sourcehash['ScanFileFrontProcessed'];hashes.append(dict(path=str(gp),sha256=sha(gp),bytes=gp.stat().st_size,kind='NON_TARGET_PACKAGE_PROVENANCE'))
   evidence.extend([dict(source_id=sid,field=k,value=v,sha256='',evidence_file=str(DATA/'metadata/metadata.csv'),classification='DOCUMENTED_METADATA',note='Nominal specification; not material calibration') for k,v in m.items()])
   evidence.append(dict(source_id=sid,field='parent_plate',value=plate,sha256=hashes[0]['sha256'],evidence_file=str(doc),classification='CONFIRMED_SAME_PARENT_PLATE',note='Explicit nomenclature rule, not an unsupported prefix assumption'))
   for field in ['scan_session','scan_timestamp','manufacturing_batch','weld_bead_id','adjacent_cut_coordinates','instrument_serial','independent_cross_plate_batch_relationship']:
    unresolved.append(dict(source_id=sid,field=field,status='UNKNOWN',evidence='No per-source field in inspected original metadata,scan_files,archive headers,package provenance,readme or dissertation',mandatory_independence_restriction=True))
   sources.append(dict(source_id=sid,population='DEVELOPMENT47' if sid in dev else 'HISTORICAL_EXPOSED_TEST12_PROVENANCE_ONLY',documented_coupon_id=coupon,confirmed_parent_plate=plate,manufacturing_batch='UNKNOWN',scan_session='UNKNOWN',scan_timestamp='UNKNOWN',instrument_family='KEYENCE_LJ_V7080_DOCUMENTED_METHOD',instrument_serial='UNKNOWN',nominal_thickness_mm=m['Thickness_mm'],source_family=reg[sid]['dependency_group'],physical_status='PHYSICAL_DEPENDENCE_CONFIRMED',between_plate_independence='PHYSICAL_INDEPENDENCE_UNRESOLVED',processed_front_SHA256=sourcehash['ScanFileFrontProcessed'],raw_front_SHA256=sourcehash['ScanFileFrontRaw'],source_geometry_SHA256=reg[sid]['front_geometry_hash'],target_values_opened=False,AI_performance_opened=False))
 # Original front geometry forensic comparison only for the47 development identities.
 screen=[];surfaces={};signatures={};rng=np.random.default_rng(20261021);ii=rng.integers(0,68457,(256,2))
 for sid in sorted(dev):
  g=E3/'02_geometry/single'/sid;x=np.load(g/'xyz.npy');tri=np.load(g/'triangles.npy');A=np.c_[np.ones(len(x)),x[:,:2]-x[:,:2].mean(0)];relief=x[:,2]-A@np.linalg.lstsq(A,x[:,2],rcond=None)[0];surfaces[sid]=relief.reshape(1201,57)
  signatures[sid]=np.linalg.norm(x[ii[:,0]]-x[ii[:,1]],axis=1)
  f=hashlib.sha256(np.round(x-x.mean(0),6).tobytes()).hexdigest();screen.append(dict(source_id=sid,XYZ_SHA256=sha(g/'xyz.npy'),triangle_SHA256=sha(g/'triangles.npy'),translation_fingerprint=f,points=len(x),triangles=len(tri),grid='1201x57;nominal0.05x0.5mm',acquisition_session_confirmed=False,physical_independence='NOT_INFERRED'))
 pairs=[]
 for a,b in itertools.combinations(sorted(dev),2):
  u=surfaces[a];v=surfaces[b];best=None
  for mirror,w in [('none',v),('X',v[::-1]),('Y',v[:,::-1]),('XY',v[::-1,::-1])]:
   for dx,dy in [(0,0),(-100,0),(100,0),(0,-4),(0,4)]:
    aa=u[100:-100,4:-4];bb=w[100+dx:1101+dx,4+dy:53+dy];d=aa-bb;rms=float(np.sqrt(np.mean(d*d)));p95=float(np.percentile(abs(d),95));corr=float(np.corrcoef(aa.ravel(),bb.ravel())[0,1]);item=dict(source_a=a,source_b=b,RMS_mm=rms,P95_mm=p95,correlation=corr,mirror=mirror,offset_X_samples=dx,offset_Y_samples=dy)
    if best is None or rms<best['RMS_mm']:best=item
  exact=next(s for s in screen if s['source_id']==a)['translation_fingerprint']==next(s for s in screen if s['source_id']==b)['translation_fingerprint'];flag=exact or (best['RMS_mm']<=.005 and best['P95_mm']<=.01 and best['correlation']>=.999);best.update(distance_signature_RMS_mm=float(np.sqrt(np.mean((signatures[a]-signatures[b])**2))),screen_flag='POSSIBLE_DEPENDENCY_FLAG' if flag else 'NO_SCREEN_FLAG_NOT_INDEPENDENCE',documented_same_parent_plate=a[0]==b[0],confirmed_common_origin_from_geometry=False);pairs.append(best)
  if flag:edges.append(dict(source_entity=a,target_entity=b,relationship_type='GEOMETRY_SIMILARITY_FLAG',evidence_file='GEOMETRY_PAIRWISE_SCREEN.csv',evidence_field=a+':'+b,classification='POSSIBLE_SHARED_ORIGIN',verified=False,mandatory_grouping=False,audit_timestamp=audit))
 for plate,members in groups.items():nodes.append(dict(id=plate,type='ParentWeldedPlate',documentary_basis='Dissertation3.2.6/Fig3.9 + same material scope',members=members))
 # No synthetic batch/session nodes. Known external one-plate limitation read only.
 aalborg=B/'WeldStressAI_Aalborg_ExternalAudit/PHYSICAL_SPECIMEN_IDENTITY.csv';external=rows(aalborg);write(R/'01_provenance/EXISTING_AALBORG_PROVENANCE.json',dict(path=str(aalborg),sha256=sha(aalborg),records=external,external_runs=0,untouched_external_validation=False))
 table(R/'SOURCE_PROVENANCE_REGISTRY.csv',sources);table(R/'PHYSICAL_PROVENANCE_EVIDENCE.csv',evidence);table(R/'PHYSICAL_DEPENDENCY_EDGES.csv',edges);write(R/'PHYSICAL_DEPENDENCY_GRAPH.json',dict(UTC=audit,nodes=nodes,edges=edges));table(R/'CONFIRMED_PHYSICAL_GROUPS.csv',[dict(evidence_level='CONFIRMED_PARENT_PLATE_GROUPS',group_id=p,members=';'.join(v),source_count=len(v),independence_between_groups='BATCH_UNRESOLVED') for p,v in groups.items()]+[dict(evidence_level='CONFIRMED_COUPON_GROUPS',group_id=s['documented_coupon_id'],members=s['source_id'],source_count=1,independence_between_groups='SAME_PLATE_DEPENDENCE') for s in sources]);table(R/'UNRESOLVED_DEPENDENCY_RECORDS.csv',unresolved);table(R/'GEOMETRY_DUPLICATE_SCREEN.csv',screen);table(R/'GEOMETRY_PAIRWISE_SCREEN.csv',pairs);table(R/'POTENTIAL_SHARED_SPECIMEN_PAIRS.csv',[p for p in pairs if p['screen_flag']=='POSSIBLE_DEPENDENCY_FLAG'],list(pairs[0]));table(R/'01_provenance/PROVENANCE_INPUT_HASHES.csv',hashes)
 write(R/'01_provenance/AUDIT_RECEIPT.json',dict(UTC=now(),development=47,test_provenance_only=12,documented_coupon_identifiers=len(sources),documented_parent_plate_codes=len(groups),documented_manufacturing_batches=0,per_source_sessions=0,possible_geometry_flags=sum(p['screen_flag']=='POSSIBLE_DEPENDENCY_FLAG' for p in pairs),pairwise_comparisons=len(pairs),same_plate_dev_test_shared=sorted(set(a[0] for a in dev)&set(a[0] for a in test)),physical_dependency_audit='PHYSICAL_DEPENDENCY_AUDIT_COMPLETE_WITH_EVIDENCE',independence='PHYSICAL_INDEPENDENCE_NOT_ESTABLISHED',limitation='Documentary nomenclature identifies plate groups and coupon locations; no independent physical inspection, unique plate serials, batch records or per-source acquisition sessions. Distinct plate codes are not proof of cross-batch independence.'))
 print('PROVENANCE_AUDIT_COMPLETED',len(groups),'documented plate codes',flush=True)
if __name__=='__main__':main()
