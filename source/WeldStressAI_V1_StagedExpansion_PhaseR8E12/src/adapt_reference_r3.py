"""Copy audited historical implementations into R3; explicit changes remove C02 instance constants."""
from common_r3 import *
def main():
 protect();copies=[]
 def cp(source,name,changes=()):
  s=source.read_text(encoding='utf-8-sig')
  for old,new in changes:assert old in s,old;s=s.replace(old,new)
  target=GLOBAL/'src'/name;assert not target.exists(),name;target.write_text(s,encoding='utf8');copies.append(dict(source=str(source),source_sha256=sha(source),copy=str(target),copy_sha256=sha(target),explicit_changes=[a for a,b in changes]))
 cp(HIST_R1/'src/pair_preflight_r1.py','pair_preflight_r1.py')
 cp(HIST_R2/'src/preflight_r2.py','preflight_r2.py',[
  ("assert (n,ne)==({'M1':(145527,82498),'M2':(193962,109737)}[level])","assert n<=350000 and ne<=230000 and read(LEVELS[level]/'PRE_SOLVER_QUALIFICATION.json')['pre_solver_qualified']"),
  ("origin=np.array([149.975,30,-9.37643484024406]);F=53200.","origin=case_origin();F=53200.;src=np.load(R/'01_frozen_protocol/geometry/solid_source.npz');assert np.ptp(src['y'])==28"),
  ("(level+'_C1.json')","(LEVELS[level].name+'.json')"),
  ("counts==({'M1':[145527,82498,187],'M2':[193962,109737,187]}[level])","counts==[read(folder/'EXPORT_RECEIPT.json')['nodes'],read(folder/'EXPORT_RECEIPT.json')['elements'],187]")])
 cp(HIST_R2/'src/gate_r2.py','gate_r2.py',[
  ("halo=(x[:,0]>=129.975)&(x[:,0]<=169.975)&(x[:,1]>=18)&(x[:,1]<=42)","src=np.load(R/'01_frozen_protocol/geometry/solid_source.npz');lo=src['x'][0];hi=src['x'][-1];yl=src['y'][0];yh=src['y'][-1];halo=(x[:,0]>=lo+10)&(x[:,0]<=hi-10)&(x[:,1]>=yl+2)&(x[:,1]<=yh-2)"),
  ("core=(x[:,0]>=130.975)&(x[:,0]<=168.975)&(x[:,1]>=19)&(x[:,1]<=41)","core=(x[:,0]>=lo+11)&(x[:,0]<=hi-11)&(x[:,1]>=yl+3)&(x[:,1]<=yh-3)"),
  ("(x[:,0]-149.975)","(x[:,0]-d['origin_X_mm'])"),("(x[:,1]-30)","(x[:,1]-d['origin_Y_mm'])")])
 cp(HIST_R2/'src/solve_r2.py','solve_r2.py',[
  ("np.unique(np.r_[np.linspace(0,ne-1,128,dtype=int),[4560,11398] if level=='M1' else []])","np.unique(np.r_[np.linspace(0,ne-1,128,dtype=int),np.argsort(m['quality'])[:16]])"),
  ("'NLGEOM,OFF','SHPP,ON','EQSLV,PCG,1e-8'","'NLGEOM,OFF','EQSLV,PCG,1e-8'"),
  ("folder=folder_for(level);assert not (folder/'input.dat').exists();pre=R/'02_mesh_import'/level;","may_execute_source();globalledger=GLOBAL/'21_reproducibility/NATIVE_SOLVE_LEDGER.json';gl=read(globalledger) if globalledger.exists() else [];assert len(gl)<4 and not any(v['source_id']==SID and v['level']==level for v in gl);folder=folder_for(level);assert not (folder/'input.dat').exists();pre=R/'02_mesh_import'/level;"),
  ("si=subprocess.STARTUPINFO();si.dwFlags", "gl.append(dict(UTC=now(),source_id=SID,level=level,kind='SOLVE',status='NATIVE_INVOCATION_AUTHORIZED',input_sha256=sha(folder/'input.dat')));write(globalledger,gl);si=subprocess.STARTUPINFO();si.dwFlags"),
  ("abs(native_xyz[:,0]-179.975)","abs(native_xyz[:,0]-native_xyz[:,0].max())"),("abs(native_xyz[:,0]-119.975)","abs(native_xyz[:,0]-native_xyz[:,0].min())")])
 cp(HIST_R2/'src/recover_r2.py','recover_r2.py')
 cp(HIST_R2/'src/t2_r2.py','t2_r2.py',[
  ("math.fsum(float(area[j])*float(a['sigma1_tensile'][j]) for j in nb)","math.fsum(float(area[j])*float(raw_sigma[j]) for j in nb)"),
  ("checks=[]\n  for i in ii", "checks=[];raw_sigma=a['sigma1_tensile']\n  for i in ii"),
  ("QUALIFIED_C02_V1_M2_TARGET.npz","QUALIFIED_"+"'+SID+'"+"_V1_M2_TARGET.npz")])
 # The literal NPZfilename substitution must remain syntactically quoted as a dynamic expression.
 p=GLOBAL/'src/t2_r2.py';s=p.read_text();s=s.replace("/'13_numerical_qualification/QUALIFIED_'+SID+'_V1_M2_TARGET.npz'", "/'13_numerical_qualification'/('QUALIFIED_'+SID+'_V1_M2_TARGET.npz')");p.write_text(s,encoding='utf8');copies[-1]['copy_sha256']=sha(p)
 write(GLOBAL/'21_reproducibility/REFERENCE_CODE_LINEAGE.json',copies);print('REFERENCE_IMPLEMENTATIONS_COPIED',len(copies),flush=True)
if __name__=='__main__':main()
