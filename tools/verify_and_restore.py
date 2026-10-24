"""Verify release assets/members; optionally restore to a new workspace. No research runs."""
from pathlib import Path,PurePosixPath
import argparse,json,csv,hashlib,zipfile,sys,fnmatch
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--downloads',type=Path,required=True);a.add_argument('--manifest-dir',type=Path,default=Path(__file__).resolve().parents[1]/'release');a.add_argument('--restore',type=Path);a.add_argument('--pattern',default='*',help='Optional archive selection, e.g. models-*');o=a.parse_args()
 m=json.loads((o.manifest_dir/'ASSET_MANIFEST.json').read_text(encoding='utf-8'))
 with (o.manifest_dir/'ARTIFACT_MANIFEST.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 by={}
 for r in rows:by.setdefault(r['asset'],{})[r['archive_member']]=r
 aux=o.manifest_dir/'REPOSITORY_AUXILIARY_FILES.csv';auxrows=[];extra={}
 if aux.exists():
  with aux.open(encoding='utf-8-sig',newline='') as f:auxrows=list(csv.DictReader(f))
  for r in auxrows:
   name=r['repository_zip'];by.setdefault(name,{})[r['archive_member']]=r;extra[name]=dict(name=name,bytes=int(r['archive_bytes']),SHA256=r['archive_SHA256'],repository_asset=True)
 count=0;selected=[item for item in list(m['assets'])+list(extra.values()) if fnmatch.fnmatchcase(Path(item['name']).name,o.pattern)];assert selected,'No matching archives'
 for item in selected:
  p=(o.manifest_dir.parent/item['name']) if item.get('repository_asset') else (o.downloads/item['name']);assert p.is_file(),f'Missing {p}'
  assert p.stat().st_size==item['bytes'] and sha(p)==item['SHA256'],f'Asset hash mismatch: {p.name}'
  with zipfile.ZipFile(p) as z:
   expected=by[item['name']];assert set(z.namelist())==set(expected),'Archive membership differs'
   for info in z.infolist():
    r=expected[info.filename];assert info.file_size==int(r['bytes']);rel=PurePosixPath(info.filename)
    assert not rel.is_absolute() and '..' not in rel.parts and ':' not in info.filename
    assert (info.external_attr>>16)&0o170000!=0o120000,'Symlink not allowed'
    h=hashlib.sha256()
    with z.open(info) as f:
     for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
    assert h.hexdigest()==r['SHA256'],info.filename
    if o.restore:
     root=o.restore.resolve();dest=root.joinpath(*rel.parts);assert dest.resolve().is_relative_to(root)
     if dest.exists():assert dest.is_file() and sha(dest)==r['SHA256'],'Refusing to overwrite differing existing file: '+str(dest)
     else:
      dest.parent.mkdir(parents=True,exist_ok=True);tmp=dest.with_name(dest.name+'.restore-part');assert not tmp.exists(),str(tmp)
      with z.open(info) as src,tmp.open('xb') as dst:
       for b in iter(lambda:src.read(8*1024**2),b''):dst.write(b)
      assert sha(tmp)==r['SHA256'];tmp.rename(dest)
    count+=1
  print('VERIFIED',p.name,len(expected),flush=True)
 assert count==sum(len(by[item['name']]) for item in selected)
 if o.pattern=='*':assert count==m['files']+len(auxrows)==len(rows)+len(auxrows)
 print(json.dumps(dict(status='PASS',verified_files=count,assets=len(selected),selection=o.pattern,restored_to=str(o.restore) if o.restore else None,research_executions=0),indent=2))
if __name__=='__main__':main()
