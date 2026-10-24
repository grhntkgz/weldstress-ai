from common import *
checks=[]
for i,r in enumerate(rows(D/'00_Source_Integrity/HISTORICAL_FILE_HASH_AUDIT.csv'),1):
 actual=sha(r['path']);checks.append({'path':r['path'],'expected_SHA256':r['expected_SHA256'],'actual_SHA256':actual,'status':'PASS' if actual==r['expected_SHA256'] else 'FAIL'})
 if i%500==0:print('Rehashed',i,flush=True)
table('06_Scientific_QA/FINAL_HISTORICAL_PRESERVATION.csv',checks)
assert all(r['status']=='PASS' for r in checks)
js('06_Scientific_QA/FINAL_HISTORICAL_PRESERVATION.json',{'status':'PASS','files':len(checks),'fresh_hashing':True,'prior_directories_modified':False})
print('FRESH FINAL HISTORICAL PASS',len(checks),flush=True)
