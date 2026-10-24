"""Download this private release; requires authorized GitHub token or Git credential helper."""
from pathlib import Path
import argparse,json,subprocess,base64,urllib.request,urllib.error,hashlib,os,fnmatch
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**k):return None
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--destination',type=Path,required=True);a.add_argument('--manifest',type=Path,default=Path(__file__).resolve().parents[1]/'release/ASSET_MANIFEST.json');a.add_argument('--pattern',default='*',help='Optional shell-style archive name selection, e.g. models-*');o=a.parse_args();m=json.loads(o.manifest.read_text())
 token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
 if token:auth='Bearer '+token
 else:
  r=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,check=True);d=dict(s.split('=',1) for s in r.stdout.splitlines() if '=' in s);auth='Basic '+base64.b64encode((d['username']+':'+d['password']).encode()).decode()
 headers={'Authorization':auth,'User-Agent':'WeldStressAI-artifact-download','Accept':'application/vnd.github+json'}
 base='https://api.github.com/repos/'+m['repository']
 with urllib.request.urlopen(urllib.request.Request(base+'/releases/tags/'+m['tag'],headers=headers),timeout=60) as f:release=json.load(f)
 by={x['name']:x for x in release['assets']};o.destination.mkdir(parents=True,exist_ok=True)
 for item in m['assets']:
  if not fnmatch.fnmatchcase(item['name'],o.pattern):continue
  dest=o.destination/item['name']
  if dest.exists():
   assert sha(dest)==item['SHA256'],'Existing download differs; move it aside first.';print('ALREADY_VERIFIED',dest.name);continue
  asset=by[item['name']];h=dict(headers);h['Accept']='application/octet-stream';req=urllib.request.Request(asset['url'],headers=h)
  try:response=urllib.request.build_opener(NoRedirect()).open(req,timeout=120)
  except urllib.error.HTTPError as e:
   if e.code not in [301,302,303,307,308]:raise
   target=e.headers['Location'];from urllib.parse import urlparse
   host=urlparse(target).hostname;assert urlparse(target).scheme=='https' and (host.endswith('.githubusercontent.com') or host.endswith('.amazonaws.com'))
   # Never send the GitHub credential to a different host.
   response=urllib.request.urlopen(urllib.request.Request(target,headers={'User-Agent':headers['User-Agent']}),timeout=120)
  tmp=dest.with_suffix(dest.suffix+'.download-part')
  with response,tmp.open('wb') as f:
   for b in iter(lambda:response.read(8*1024**2),b''):f.write(b)
  assert tmp.stat().st_size==item['bytes'] and sha(tmp)==item['SHA256'],dest.name
  tmp.rename(dest);print('DOWNLOADED_AND_VERIFIED',dest.name,flush=True)
 print('COMPLETE. Next run tools/verify_and_restore.py; no research entry points were executed.')
if __name__=='__main__':main()
