from common_r3 import *
from protocol_core import validate_bvp
import jsonschema
def main():
 protect();b=read(E9/'03_config/specimens'/SID/'BVP_PROPOSED.json');jsonschema.Draft202012Validator(read(E9/'STANDARD_BVP_SCHEMA.json')).validate(b);validate_bvp(b);d=read(R/'01_frozen_protocol/PARENT_DATUM.json');rear=dict(source_id=SID,protocol_id='FRONT_PARENT_HUBER_OUTER10_NORMAL_OFFSET_V1',nominal_thickness_mm=19,thickness_basis='DOCUMENTED_NOMINAL',intercept_Z_mm=d['intercept_Z_mm'],slope_X=d['slope_X'],slope_Y=d['slope_Y'],origin_X_mm=d['origin_X_mm'],origin_Y_mm=d['origin_Y_mm'],rear_offset_vertical_mm=19*np.sqrt(1+d['slope_X']**2+d['slope_Y']**2),parent_RMS_mm=d['parent_RMS_mm'],parent_P95_mm=d['parent_P95_abs_mm'],rear_measurement_used=False);jsonschema.Draft202012Validator(read(E9/'REAR_PLANE_RULE_SCHEMA.json')).validate(rear);write(R/'01_frozen_protocol/REAR_SCHEMA_INSTANCE.json',rear)
 registry=read(E9/'03_config/TARGET_INSTANCE_REGISTRY.json')['instances'];row=next(z for z in registry if z['source_id']==SID);assert row['source_geometry_hash']==sha(R/'01_frozen_protocol/source/xyz.npy') and row['original_point_ids_hash']==sha(R/'01_frozen_protocol/source/source_ids.npy');regpath=R/'QUALIFIED_V1_TARGET_REGISTRY.csv'
 if regpath.exists() and rows(regpath):
  selected=rows(regpath)[0];row.update(status='QUALIFIED',target_hash=selected['target_hash'],M1_mesh_hash=selected['M1_mesh_hash'],M2_mesh_hash=selected['M2_mesh_hash'])
 jsonschema.Draft202012Validator(read(E9/'TARGET_VERSION_SCHEMA.json')).validate(row);write(R/'01_frozen_protocol/TARGET_SCHEMA_INSTANCE.json',row);write(R/'01_frozen_protocol/SCHEMA_AUDIT.json',dict(UTC=now(),source_id=SID,BVP_schema_pass=True,rear_schema_pass=True,target_schema_pass=True,no_numeric_protocol_change=True));print('SCHEMA_AUDIT_PASS',SID,flush=True)
if __name__=='__main__':main()
