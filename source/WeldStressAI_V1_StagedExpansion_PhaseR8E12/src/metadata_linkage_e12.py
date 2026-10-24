from setup_e11r1 import *
def main():
 data=B.parent/'WeldScan-FEA/data/metadata';meta=rows(data/'metadata.csv');scan=rows(data/'scan_files.csv');out=[]
 for a in rows(R/'SOURCE_PROVENANCE_REGISTRY.csv'):
  sid=a['source_id'];exact=[x for x in meta if x['SpecimenName']==sid];linked=exact or [x for x in meta if x['SpecimenName'].rsplit('-',1)[0]==sid.rsplit('-',1)[0]];assert linked and len({(x['Material'],x['Geometry'],x['Thickness_mm']) for x in linked})==1
  matches=[x for x in scan if x['SpecimenName']==sid];unique={json.dumps(x,sort_keys=True) for x in matches};assert len(unique)==1
  out.append(dict(source_id=sid,metadata_basis='EXACT_STATE_METADATA' if exact else 'EXPLICIT_UNAMBIGUOUS_COUPON_TREATMENT_SIBLING_LINK',metadata_SpecimenNames=';'.join(sorted({x['SpecimenName'] for x in linked})),metadata_Conditions=';'.join(sorted({x['Condition'] for x in linked})),nominal_thickness_mm=linked[0]['Thickness_mm'],material=linked[0]['Material'],documented_coupon_link_basis='Dissertation3.2.6 platecode/position and condition suffix;4.3 before-after scan methodology',original_scan_mapping_rows=len(matches),distinct_scan_mapping_rows=1,repeated_identical_metadata_rows_are_repeat_scans=False,original_files_modified=False))
 table(R/'SOURCE_METADATA_LINKAGE.csv',out);print('EXPLICIT_METADATA_LINKAGE',len(out),'sources;',sum(a['metadata_basis']!='EXACT_STATE_METADATA' for a in out),'treatment-sibling nominal links')
if __name__=='__main__':main()
