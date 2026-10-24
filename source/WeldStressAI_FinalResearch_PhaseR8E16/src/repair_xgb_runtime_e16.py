from common_e16 import *
import urllib.request,subprocess

def main():
 meta=json.load(urllib.request.urlopen('https://pypi.org/pypi/scikit-learn/1.6.1/json'));a=next(a for a in meta['urls'] if a['filename']=='scikit_learn-1.6.1-cp310-cp310-win_amd64.whl');p=R/'tmp'/a['filename'];urllib.request.urlretrieve(a['url'],p);assert sha(p)==a['digests']['sha256'];write(R/'09_resource_preflight/SKLEARN_WHEEL_PROVENANCE.json',dict(version='1.6.1',url=a['url'],SHA256=sha(p),reason='System sklearn binary incompatible with existing numpy2; isolated repair before any fit'))
 run=subprocess.run([sys.executable,'-m','pip','install','--no-deps','--no-compile','--no-cache-dir','--target',str(R/'runtime_site'),str(p)]);assert run.returncode==0;sys.path.insert(0,str(R/'runtime_site'));import sklearn,xgboost,numpy,scipy;assert xgboost.__version__=='3.0.2';write(R/'09_resource_preflight/XGBOOST_RUNTIME_READY.json',dict(UTC=now(),passed=True,xgboost=xgboost.__version__,sklearn=sklearn.__version__,numpy=numpy.__version__,scipy=scipy.__version__,path=xgboost.__file__,backend='CPU hist; n_jobs2',existing_environments_modified=False));print('XGBOOST_RUNTIME_READY',flush=True)
if __name__=='__main__':main()
