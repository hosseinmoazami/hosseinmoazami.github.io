#!/usr/bin/env python3
"""Generate the three dependency-free SVGs for the Kubernetes deletion runbook."""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'assets/charts'

def start(height, title, description):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
            '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#526777"/></marker></defs>',
            '<style>text{font-family:system-ui,sans-serif;fill:#203c4a;font-size:17px}.title{font-size:21px;font-weight:700}.small{font-size:15px}.line{stroke:#526777;stroke-width:2;fill:none;marker-end:url(#arrow)}</style>',
            f'<rect width="480" height="{height}" rx="12" fill="#f4f3ee"/>']

def text(a, x, y, value, cls=''):
    a.append(f'<text x="{x}" y="{y}" text-anchor="middle" class="{cls}">{escape(value)}</text>')

def box(a, x, y, width, lines, fill='#e3eeeb', height=80):
    a.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="{fill}" stroke="#b2c4be"/>')
    for i, line in enumerate(lines):
        text(a, x + width / 2, y + 27 + i * 23, line, 'small' if width < 300 else '')

def path(a, d):
    a.append(f'<path d="{d}" class="line"/>')

def save(name, a):
    (OUT / name).write_text('\n'.join(a + ['</svg>']) + '\n')

a = start(950, 'Namespace deletion triage', 'Inspect conditions and API availability. Failed discovery means unknown inventory. With complete discovery, inspect remaining objects and controllers; only consider namespace finalization after cleanup and risk review.')
text(a, 240, 34, 'Namespace stuck in Terminating', 'title')
box(a, 30, 60, 420, ['Read namespace conditions', 'Check discovery and API errors'])
path(a, 'M240,140 L240,165 L125,165 L125,190')
path(a, 'M240,165 L355,165 L355,190')
box(a, 20, 200, 210, ['API errors present', 'Inventory is incomplete', 'Repair APIs; rescan'], '#f1e0d9', 104)
box(a, 250, 200, 210, ['Discovery succeeds', 'List every namespaced', 'resource type'], height=104)
path(a, 'M355,304 L355,336 L240,336 L240,366')
box(a, 30, 376, 420, ['Any list errors?', 'Resolve them before claiming empty'])
path(a, 'M240,456 L240,480 L125,480 L125,512')
path(a, 'M240,480 L355,480 L355,512')
box(a, 20, 522, 210, ['Objects remain', 'Inspect finalizers', 'Check controller'], height=104)
box(a, 250, 522, 210, ['No objects found', 'Check namespace', 'finalization state'], height=104)
path(a, 'M125,626 L125,662')
path(a, 'M355,626 L355,662')
box(a, 20, 672, 210, ['Restore normal cleanup', 'or deliberately bypass', 'one reviewed obligation'], '#e7e2d2', 104)
box(a, 250, 672, 210, ['Last resort: /finalize', 'Accept orphan risk', 'Verify all storage'], '#f1e0d9', 104)
text(a, 240, 823, 'After object cleanup: repeat the inventory.')
text(a, 240, 861, 'After forced finalization: API absence is not')
text(a, 240, 887, 'proof that external storage was removed.')
text(a, 240, 926, 'Never interpret failed queries as empty results.', 'small')
save('namespace-deletion-triage.svg', a)

a = start(875, 'Normal and forced finalizer cleanup', 'Deletion sets a deletion timestamp. With no remaining finalizers, deletion can complete subject to grace periods. Normally controllers fulfill cleanup obligations; manually clearing finalizers bypasses that work and can orphan backend resources.')
text(a, 240, 34, 'Finalizers record pending obligations', 'title')
box(a, 30, 60, 420, ['kubectl delete', 'deletionTimestamp is set'])
path(a, 'M240,140 L240,170')
box(a, 30, 180, 420, ['Are finalizers still present?'])
path(a, 'M30,220 L12,220 L12,713 L29,713')
text(a, 86, 300, 'No', 'small')
path(a, 'M240,260 L240,290 L130,290 L130,330')
path(a, 'M240,290 L355,290 L355,330')
text(a, 240, 317, 'Yes', 'small')
box(a, 30, 340, 200, ['Normal path', 'Controller handles', 'cleanup obligation'], height=104)
box(a, 250, 340, 210, ['Forced bypass', 'Operator clears', 'finalizer keys'], '#f1e0d9', 104)
path(a, 'M130,444 L130,480')
path(a, 'M355,444 L355,480')
box(a, 30, 490, 200, ['Required cleanup', 'finishes; controller', 'removes its key'], height=104)
box(a, 250, 490, 210, ['Cleanup may not run', 'Backend artifacts', 'can remain'], '#f1e0d9', 104)
path(a, 'M130,594 L130,630 L240,630 L240,663')
path(a, 'M355,594 L355,630 L240,630')
box(a, 30, 673, 420, ['All keys cleared + grace period complete', 'Object can leave the API'], height=80)
path(a, 'M240,753 L240,780')
text(a, 253, 810, 'API object gone ≠ backend verified', 'title')
text(a, 240, 849, 'Namespace spec.finalizers uses a separate path.', 'small')
save('kubernetes-finalizer-cleanup.svg', a)

a = start(950, 'Kubernetes and Longhorn storage relationships', 'A namespaced Pod uses a PVC bound to a cluster-scoped PV. A StorageClass supplies provisioning configuration to CSI. The PV CSI handle identifies the Longhorn volume, which is backed by replica storage. StorageClass is not in the application data path.')
text(a, 240, 34, 'Follow the claim to its backing data', 'title')
box(a, 30, 60, 420, ['Pod → PVC', 'Same application namespace'])
path(a, 'M240,140 L240,185')
text(a, 330, 167, 'claim binding', 'small')
box(a, 30, 195, 420, ['PersistentVolume (cluster-scoped)', 'Reclaim policy + CSI volume handle'])
path(a, 'M240,275 L240,315')
box(a, 30, 325, 420, ['CSI provisioner / driver', 'Provision, attach, delete operations'])
path(a, 'M240,405 L240,444')
box(a, 30, 454, 420, ['Longhorn volume', 'Backend identity from the PV handle'])
path(a, 'M240,534 L240,573')
box(a, 30, 583, 420, ['Replica storage on disks', 'Separate from Kubernetes API records'])
box(a, 30, 701, 420, ['StorageClass → provisioning policy', 'Provisioner, parameters, reclaim default'], '#e7e2d2', 85)
text(a, 240, 817, 'StorageClass configures provisioning;', 'small')
text(a, 240, 841, 'it is not a hop between PV and disk.', 'small')
text(a, 240, 886, 'Deleting a PVC can destroy backing data.')
text(a, 240, 915, 'Bypassing finalizers can instead orphan it.')
save('kubernetes-storage-deletion.svg', a)
print('Generated three deletion diagrams.')
