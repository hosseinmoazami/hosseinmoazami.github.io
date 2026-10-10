#!/usr/bin/env python3
"""Generate lightweight diagrams for the Kubernetes memory runbook."""
from pathlib import Path
from html import escape
OUT=Path(__file__).resolve().parents[1]/'assets/charts'
OUT.mkdir(exist_ok=True)
def start(h,title,desc):
 return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 {h}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>', '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#526777"/></marker></defs><style>text{font-family:system-ui,sans-serif;fill:#203c4a;font-size:17px}.title{font-size:21px;font-weight:700}.small{font-size:15px}.line{stroke:#526777;stroke-width:2;fill:none;marker-end:url(#arrow)}</style>',f'<rect width="480" height="{h}" rx="12" fill="#f4f3ee"/>']
def txt(a,x,y,s,cls='',anchor='middle'):a.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{escape(s)}</text>')
def box(a,y,lines,fill='#e3eeeb',height=76):
 a.append(f'<rect x="25" y="{y}" width="430" height="{height}" rx="8" fill="{fill}" stroke="#b2c4be"/>')
 for i,line in enumerate(lines):txt(a,240,y+28+i*23,line)
def arrow(a,y1,y2):a.append(f'<path d="M240,{y1} L240,{y2}" class="line"/>')
def save(name,a): (OUT/name).write_text('\n'.join(a+['</svg>'])+'\n')
a=start(650,'Memory investigation layers','Move from Kubernetes evidence to cgroup charge, process mappings, runtime accounting, and application behavior.')
txt(a,240,34,'Choose the right observation layer','title')
for i,lines in enumerate([['Kubernetes','describe · top · previous logs'],['Container / cgroup','memory.current · max · stat · events'],['Linux process','ps · status · smaps_rollup'],['Node.js runtime','in-process RSS / heap / external'],['Next.js application','SSR · caches · images · retained state']]):
 y=65+i*112;box(a,y,lines)
 if i<4:arrow(a,y+76,y+103)
txt(a,240,635,'These metrics overlap; do not add them.','small');save('memory-investigation-layers.svg',a)
a=start(750,'Node old space is only part of container memory','Conceptual compartments, not measured sizes. The cgroup charges more than the V8 old-generation heap; a 4096-MiB old-space ceiling leaves no budget for other memory under a 4-GiB limit.')
txt(a,240,33,'Container limit: 4 GiB = 4096 MiB','title')
a.append('<rect x="20" y="55" width="440" height="515" rx="10" fill="#fff" stroke="#9b713d" stroke-width="2"/><rect x="38" y="80" width="404" height="378" rx="8" fill="#e3eeeb" stroke="#146b68"/>')
txt(a,240,111,'Node.js process RSS','title')
a.append('<rect x="57" y="132" width="366" height="132" rx="8" fill="#ccdeda"/>')
txt(a,240,159,'V8 heap','title');txt(a,240,190,'Old generation: max-old-space-size');txt(a,240,221,'+ young generation / other spaces')
for i,s in enumerate(['Buffers / ArrayBuffers · native addons','Sharp / image buffers · OpenSSL / ICU','Stacks · libraries · allocator overhead']):txt(a,240,301+i*30,s,'small')
txt(a,240,425,'Categories overlap; not an additive ledger.','small')
txt(a,240,497,'Other processes + kernel memory');txt(a,240,528,'+ charged file cache / tmpfs')
box(a,590,['4096 MiB old space + other charges','can reach the cgroup ceiling first.'],'#f1e0d9',85)
txt(a,240,705,'Conceptual layout, not to scale.','small');txt(a,240,729,'A heap limit is not a reservation or an RSS limit.','small');save('node-container-memory-budget.svg',a)
a=start(695,'Reported memory observations','cgroup memory 1.8495 GiB; process VmRSS 1.8859 GiB; smaps RSS 1.8888 GiB and anonymous 1.8213 GiB. Samples and accounting differ; this is not an exact reconciliation.')
txt(a,240,33,'Observed values, converted to GiB','title')
for y,lines in [(65,['Cgroup charge: 1.8495 GiB','1,985,835,008 bytes']), (177,['next-server · PID 1','VmRSS: 1.8859 GiB']), (289,['smaps_rollup RSS: 1.8888 GiB','Anonymous: 1.8213 GiB (~96.4%)']), (401,['Private_Dirty: 1.8213 GiB','Overlaps Anonymous; do not add.'])]:
 box(a,y,lines)
 if y<401:arrow(a,y+76,y+103)
box(a,518,['Application memory is the leading path.','Inspect V8, native allocations, caches.'],'#e7e2d2',84)
txt(a,240,635,'Different samples/accounting; not a proof of leak.','small');txt(a,240,662,'Not a measurement of the earlier OOM peak.','small');save('memory-incident-observations.svg',a)
a=start(770,'Stable usage versus possible unbounded growth','Conceptual sample paths, not recorded incident telemetry. Stable values fluctuate around 1.8 to 2 GiB; rising values approach a 4 GiB limit. Growth alone is not proof of a leak.')
txt(a,240,33,'Memory over time: compare trends','title')
for base,title,vals,color in [(85,'Stable workload / bounded working set',[1.8,1.9,2,1.9,2],'#146b68'),(405,'Possible leak / unbounded growth',[500/1024,900/1024,1.5,2.1,2.8,3.5,3.9],'#a6533c')]:
 txt(a,240,base,title,'title')
 for v in [0,1,2,3,4]:
  yy=base+235-v*48;a.append(f'<line x1="65" y1="{yy}" x2="440" y2="{yy}" stroke="#d4dcd8"/>');txt(a,45,yy+5,str(v),'small')
 pts=[(65+i*375/(len(vals)-1),base+235-v*48) for i,v in enumerate(vals)]
 a.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="3"/>')
 txt(a,80,base+25,'GiB','small');txt(a,240,base+260,'Successive samples →','small')
 if base==405:txt(a,420,base+30,'4 GiB limit','small','end')
txt(a,240,714,'Continued growth may reach OOM.','small');txt(a,240,740,'Illustration only; correlate load and post-GC baseline.','small');save('memory-stable-versus-growth.svg',a)
a=start(1150,'Memory troubleshooting decision flow','Branch on process RSS relative to cgroup charges, then classify mappings and choose capacity or growth investigation.')
txt(a,240,32,'OOMKilled: follow the evidence','title')
for y,lines in [(60,['describe + previous logs','Check reason, time, restart, and node']), (174,['top --containers + cgroup files','current / max / events / stat']), (288,['Find actual PID; compare RSS to charge','Same scope and sampling window'])]:
 box(a,y,lines)
 if y<288:arrow(a,y+76,y+103)
def smallbox(x,y,lines,fill='#e3eeeb',height=100):
 a.append(f'<rect x="{x}" y="{y}" width="205" height="{height}" rx="8" fill="{fill}" stroke="#b2c4be"/>')
 for i,line in enumerate(lines):txt(a,x+102.5,y+26+i*23,line,'small')
a.append('<path d="M240,364 L240,385 L127,385 L127,412" class="line"/><path d="M240,385 L353,385 L353,412" class="line"/>')
smallbox(25,422,['RSS much lower','Other processes / cache','tmpfs / kernel charges'],'#e7e2d2')
smallbox(250,422,['RSS comparable','Read smaps_rollup','Inspect memory type'])
a.append('<path d="M352,522 L352,558" class="line"/>')
smallbox(250,568,['Anonymous-heavy','V8 / native / caches'])
smallbox(25,568,['File-backed-heavy','Inspect mappings and','cgroup file charges'],'#e7e2d2')
a.append('<path d="M270,522 L270,543 L127,543 L127,558" class="line"/><path d="M352,668 L352,690 L240,690 L240,710" class="line"/>')
box(a,720,['Inspect runtime limits and headroom','Track heap, external memory, and RSS'])
arrow(a,796,822)
box(a,832,['Observe equivalent workload windows','Compare baseline after major GC'])
a.append('<path d="M240,908 L240,927 L127,927 L127,948" class="line"/><path d="M240,927 L352,927 L352,948" class="line"/>')
smallbox(25,958,['Stable','Capacity / concurrency','Peak headroom'])
smallbox(250,958,['Continuously growing','Retention / cache / native','Snapshots + GC traces'])
txt(a,240,1096,'Branches guide investigation; they are not verdicts.','small')
txt(a,240,1123,'A current snapshot cannot explain a past peak.','small')
save('memory-troubleshooting-flow.svg',a)
print('Generated five memory diagrams.')
