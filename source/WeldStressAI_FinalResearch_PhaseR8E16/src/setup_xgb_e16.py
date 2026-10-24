from common_e16 import *
import urllib.request,subprocess

def main():
 gate();meta=json.load(urllib.request.urlopen('https://pypi.org/pypi/xgboost/3.0.2/json'));a=next(a for a in meta['urls'] if a['filename']=='xgboost-3.0.2-py3-none-win_amd64.whl');assert a['digests']['sha256']=='b4c89b71d134da9fa6318e3c9f5459317d1013b4d57059d10ed2840750e2f7e1';write(R/'09_resource_preflight/XGBOOST_PYPI_METADATA.json',meta);wheel=R/'tmp'/a['filename'];urllib.request.urlretrieve(a['url'],wheel);assert sha(wheel)==a['digests']['sha256'];write(R/'09_resource_preflight/XGBOOST_WHEEL_PROVENANCE.json',dict(version='3.0.2',official_url=a['url'],SHA256=sha(wheel),bytes=wheel.stat().st_size,independent_target=str(R/'runtime_site')))
 p=subprocess.run([sys.executable,'-m','pip','install','--no-deps','--no-compile','--no-cache-dir','--target',str(R/'runtime_site'),str(wheel)]);assert p.returncode==0;sys.path.insert(0,str(R/'runtime_site'));import xgboost;assert xgboost.__version__=='3.0.2';write(R/'09_resource_preflight/XGBOOST_RUNTIME_READY.json',dict(UTC=now(),passed=True,version=xgboost.__version__,path=xgboost.__file__,backend='CPU hist, n_jobs=2',existing_environments_modified=False));print('XGBOOST_RUNTIME_READY',flush=True)
if __name__=='__main__':main()
