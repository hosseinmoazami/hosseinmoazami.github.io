#!/usr/bin/env python3
"""Generate the namespace-scoped ServiceAccount architecture diagram."""
from html import escape
from pathlib import Path

out = Path(__file__).resolve().parents[1] / 'assets/charts/limited-kubeconfig-rbac.svg'
a = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 820" role="img" aria-labelledby="title desc">',
     '<title id="title">One identity, two namespace-scoped grants</title>',
     '<desc id="desc">The ServiceAccount default/limited-access-user has one token. Two RoleBindings, in namespace1 and namespace2, reference this exact subject and the shared ClusterRole custom-namespace-access. No grant is created in namespace3. Other existing grants must still be audited.</desc>',
     '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#526777"/></marker></defs>',
     '<style>text{font-family:system-ui,sans-serif;fill:#203c4a;font-size:17px}.title{font-size:21px;font-weight:700}.small{font-size:15px}.line{stroke:#526777;stroke-width:2;fill:none;marker-end:url(#arrow)}</style>',
     '<rect width="480" height="820" rx="12" fill="#f4f3ee"/>']

def text(x,y,s,cls=''):
    a.append(f'<text x="{x}" y="{y}" text-anchor="middle" class="{cls}">{escape(s)}</text>')

def box(x,y,w,lines,fill='#e3eeeb',height=95):
    a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{height}" rx="8" fill="{fill}" stroke="#b2c4be"/>')
    for i,line in enumerate(lines): text(x+w/2,y+28+i*24,line,'small' if w<300 else '')

def path(d): a.append(f'<path d="{d}" class="line"/>')

text(240,35,'One identity, two scoped grants','title')
box(25,65,430,['ServiceAccount','default/limited-access-user','One token → same identity'],height=110)
path('M240,175 L240,210 L125,210 L125,249')
path('M240,210 L355,210 L355,249')
text(240,237,'Both bind the same subject','small')
box(20,259,210,['RoleBinding','namespace1','subject namespace: default'],height=105)
box(250,259,210,['RoleBinding','namespace2','subject namespace: default'],height=105)
path('M125,364 L125,445')
path('M355,364 L355,445')
text(240,412,'Shared role','small')
text(240,435,'reference','small')
box(25,455,430,['ClusterRole: custom-namespace-access','get / list / watch','pods · services · configmaps'],height=110)
box(25,610,430,['namespace3: no grant from this setup','Other bindings may still grant access.'],'#f1e0d9',85)
text(240,733,'Binding namespace = scope of the grant')
text(240,763,'Subject namespace = location of the identity')
text(240,796,'Kubeconfig contexts select defaults, not permissions.','small')
out.write_text('\n'.join(a+['</svg>'])+'\n')
print('Generated namespace-scoped RBAC diagram.')
