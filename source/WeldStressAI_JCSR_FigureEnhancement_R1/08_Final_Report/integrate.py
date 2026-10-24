from common import *
import numpy as np

f3='Fig03_Geometry_Representation_Observation_Context'
f7='Fig07_FE_vs_N2_N3_Stress_Fields'
cap3=('Processed measured G07 geometry, observation support and numerical representation. '
 '(a) Original canonical XYZ in mm, true three-dimensional aspect, tensile +X direction, exact historical FULL/X50/X43 extents for owning tile 4, and the same original query ID 50815 with its visible sixteen-neighbor neighborhood. The magnified neighborhood inset is explanatory; the query is selected by a deterministic geometry-only rule within the existing collar proxy, before reading predictions, and is illustrative rather than statistically representative. '
 '(b) All nineteen historical N1/N2 and visible-local N3 channels, indexed 0–18. At this point only historical channels 0, 1, 2, 6, 16 and 17 change between FULL and either restriction; all nineteen N3 local channels remain identical. The 4096-point visible contextual support can still change. Numerical values and exact formulas are archived. '
 '(c) Executed compact SurfacePT: width 24, three sixteen-neighbor sets, local attention, learned scale weights, mean encoded context, per-query layer normalization and scalar T2 output; 7228 parameters and no query-to-query attention or pooling. '
 '(d) A prediction can change without changing the measured query geometry. This is a computational representation effect, not a physical stress change or experimental stress measurement. Geometry proxies are not independently authenticated measured weld-toe trajectories. Codex-assisted plotting and historical tool declarations remain subject to author confirmation.')
cap7=('Frozen FE T2 numerical references, saved N2/N3 predictions and signed errors for G07 and X23, FULL observation and prespecified seed 20261021. '
 'All panels use the original processed measured front geometry and identical 34,200-point scoring-core IDs, XYZ and vertex areas within each source. '
 'T2 is the qualified regularized maximum principal tensile stress in MPa; signed error is prediction minus FE reference in MPa. '
 'The three stress maps share the exact joint source-wise extrema; both error maps share symmetric zero-centered limits spanning their joint maximum absolute error. Sources have separate limits. '
 'Physical XY aspect is retained. Display shading interpolates only within unchanged original canonical triangles; no different mesh, field resampling, smoothing or clipping is introduced. '
 'Historical High95 masks are retained separately in Supplementary Figures S7, S9 and S21–S30. '
 'X23 FULL/20261021 is the documented small positive source-level High95 exception; the adverse X23 seed/context results remain in the supplementary atlas. '
 'These are numerical stress fields, not experimental stress measurements; no independently authenticated measured weld-toe trajectory or validated crack-initiation location is shown.')

md=(J/'01_Main_Manuscript/WELDSTRESS_AI_JCSR_MAIN_MANUSCRIPT.md').read_text(encoding='utf-8')
for n in [1,2,4,5,6,8,9]:
 for p in (J/'03_Figures').glob(f'Fig{n:02d}_*'):
  copy(p,Path('05_Final_Manuscript/figures/main')/p.name)
for folder,stem in [('01_Enhanced_Figure03',f3),('02_New_Figure07',f7)]:
 for ext in ['png','pdf','svg']:copy(D/folder/(stem+'.'+ext),Path('05_Final_Manuscript/figures/main')/(stem+'.'+ext))
md=md.replace('Fig03_Representation_and_executed_network.png',f3+'.png').replace('Fig07_Regional_errors.png',f7+'.png')
md=re.sub(r'^Figure 3\. .*$', 'Figure 3. '+cap3,md,flags=re.M)
md=re.sub(r'^Figure 7\. .*$', 'Figure 7. '+cap7,md,flags=re.M)
md=md.replace('Figure 3 documents this implementation.','Figure 3 links the original observed geometry, exact observation extents, verified channel definitions and executed implementation.')
md=md.replace('Figure 7 provides the retrospective regional MAE comparison discussed in Section 5.7.','Supplementary Figure S20 preserves the complete retrospective regional MAE comparison discussed in Section 5.7. Figure 7 instead shows the frozen FE and saved N2/N3 stress fields for the prespecified G07 and X23 FULL/20261021 cases. X23 is retained as a difficult X-group source; this particular source/seed/context is the documented small positive High95 exception, while its adverse comparisons remain in Supplementary Figures S21–S30.')
md=md.replace('Regional errors in Figure 7 separate','Regional errors in Supplementary Figure S20 separate')
write('05_Final_Manuscript/WELDSTRESS_AI_JCSR_VISUAL_FINAL.md',md)
write('01_Enhanced_Figure03/CAPTION.md','Figure 3. '+cap3+'\n')
write('02_New_Figure07/CAPTION.md','Figure 7. '+cap7+'\n')
write('05_Final_Manuscript/FINAL_FIGURE_CAPTIONS.md','\n\n'.join(re.findall(r'^Figure [1-9]\. .*$',md,re.M))+'\n')

# All original SI source assets remain byte-identical. Rebuild only the SI document.
for p in (J/'05_Supplementary_Material').rglob('*'):
 if p.is_file() and p.suffix not in ['.docx']:
  copy(p,Path('04_Supplementary_Update')/p.relative_to(J/'05_Supplementary_Material'))
si=(J/'05_Supplementary_Material/SUPPLEMENTARY_INFORMATION.md').read_text(encoding='utf-8')
reg=rows(J/'05_Supplementary_Material/SUPPLEMENTARY_FIGURE_INDEX.csv')
regional=('Complete unchanged former main Figure 7: retrospective regional MAE in MPa for N1/N2/N3 across parent, collar and height proxies, FULL/X50/X43, all thirteen measured fronts and five documentary plates. Original area-weighted source metrics are averaged within plate and across separately scored seeds 20261021/20261022. The proxies are not independent measured toes. Numerical T2 errors, source/seed metrics and contributions remain unchanged in the CSV appendices.')
extras=[(20,J/'03_Figures/Fig07_Regional_errors.png',regional)]
i=21
for sid in ['G07','X23']:
 for cond in ['FULL','X50','X43']:
  for seed in [20261021,20261022]:
   if cond=='FULL' and seed==20261021:continue
   path=P/'figures/supplementary/legacy_R2'/f'{sid}-V1-S355-AW_{cond}_s{seed}_spatial.png'
   cap=(f'{sid}-V1-S355-AW, {cond}, seed {seed}: unchanged historical atlas showing original geometry, frozen FE T2, saved N2/N3 fields, signed errors and historical High95 masks. High95 uses each field’s original area-weighted interpolated 95th percentile with inclusive membership. These are not the matched-area rank masks of Figures S10–S19. All adverse cases are retained. Geometry labels are proxies and stress is numerical, not experimentally measured.')
   extras.append((i,path,cap));i+=1
for n,path,cap in extras:
 for ext in ['png','pdf']:copy(path.with_suffix('.'+ext),Path('04_Supplementary_Update/figures')/f'Figure_S{n:02d}.{ext}')
 reg.append({'figure_id':f'S{n}','file':f'figures/Figure_S{n:02d}.png','source':str(path),'SHA256':sha(path),'caption':cap})
 si+=f'\n![Figure S{n}](figures/Figure_S{n:02d}.png)\n\nFigure S{n}. {cap}\n'
si=si.replace('All figures reuse frozen artwork.','All figures reuse frozen artwork. Figures S1–S19 retain their original numbering and bytes. Figure S20 preserves the former main regional-error grid. Figures S7, S9 and S21–S30 together cover both G07/X23 sources, both seeds and all three contexts without replacing the existing rank-mask evidence.')
write('04_Supplementary_Update/SUPPLEMENTARY_INFORMATION.md',si)
table('04_Supplementary_Update/SUPPLEMENTARY_FIGURE_INDEX.csv',reg)
write('04_Supplementary_Update/UPDATED_FIGURE_CAPTIONS.md','\n\n'.join('Figure '+r['figure_id']+'. '+r['caption'] for r in reg)+'\n')
mainreg=[]
for n in range(1,10):
 p=next((D/'05_Final_Manuscript/figures/main').glob(f'Fig{n:02d}_*.png'))
 mainreg.append({'figure':n,'file':str(p.relative_to(D/'05_Final_Manuscript')),'SHA256':sha(p),'action':'Recreated from frozen arrays' if n in [3,7] else 'Preserved byte-identical','caption':re.search(rf'^Figure {n}\. (.*)$',md,re.M).group(1)})
table('05_Final_Manuscript/FINAL_FIGURE_REGISTRY.csv',mainreg)
write('03_Other_Figure_Updates/REVIEW_AND_PRESERVATION.md','# Review of preserved main figures\n\nFigures 1, 2, 4, 5, 6, 8 and 9 retain their original PNG/PDF bytes and captions. Figure 1 uses true physical proportions; Figure 3 now supplies an additional actual geometry view. Figure 6 distinguishes matched ranking from common reference thresholds and retains the extreme 1% deterioration and separately identified seeds. Figure 8 retains geometry–FE association rather than duplicating prediction maps; all transition boundaries remain proxies. Figure 9 retains FULL-only comparisons and G0’s unequal area. The complete dense former Figure 7 moves unchanged to S20. No other redraw was justified.\n')
for name in ['journal_docx_builder.py','render_docx_word.py']:copy(J/'10_Reproducibility_Manifest'/name,Path('08_Final_Report')/name)
print('INTEGRATION COMPLETE: 9 main; 30 SI; 7 unchanged main; original 19 SI unchanged')
