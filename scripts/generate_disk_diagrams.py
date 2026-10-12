#!/usr/bin/env python3
"""Generate dependency-free SVG diagrams for the disk-full runbook."""
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

def box(a, x, y, width, lines, fill='#e3eeeb', height=86):
    a.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="{fill}" stroke="#b2c4be"/>')
    for i, line in enumerate(lines):
        text(a, x + width / 2, y + 27 + i * 23, line, 'small' if width < 300 else '')

def path(a, d):
    a.append(f'<path d="{d}" class="line"/>')

def save(name, a):
    (OUT / name).write_text('\n'.join(a + ['</svg>']) + '\n')

a = start(740, 'Who owns the stored bytes?', 'Docker manages images, layers and cache. Volumes may contain persistent application data. Elasticsearch owns index deletion inside its volume. Inspect sizes without deleting managed filesystem contents.')
text(a, 240, 34, 'Who owns the stored bytes?', 'title')
box(a, 30, 60, 420, ['Linux filesystem', 'df → capacity · du → directory usage'])
path(a, 'M240,146 L240,175 L125,175 L125,201')
path(a, 'M240,175 L355,175 L355,201')
box(a, 20, 211, 210, ['Docker layers / cache', 'Image + writable layers', 'Managed by Docker'], height=104)
box(a, 250, 211, 210, ['Docker volume', 'Persistent app data', 'Not disposable cache'], '#e7e2d2', 104)
path(a, 'M125,315 L125,349')
path(a, 'M355,315 L355,349')
box(a, 20, 359, 210, ['Review Docker objects', 'Use scoped CLI cleanup', 'Never edit overlay2'], height=104)
box(a, 250, 359, 210, ['Elasticsearch data', 'UUID → index name', 'Check retention'], height=104)
path(a, 'M355,463 L355,497')
box(a, 250, 507, 210, ['Verify snapshot', 'Delete exact index', 'through its API'], '#f1e0d9', 104)
text(a, 129, 530, 'Broken layers?', 'small')
text(a, 129, 555, 'Rebuild / restore.', 'small')
text(a, 129, 580, 'Prune is not repair.', 'small')
text(a, 240, 656, 'Volume prune can delete application data.')
text(a, 240, 687, 'A large path is not proof of disposable data.')
text(a, 240, 719, 'Inspect first; let the owner perform cleanup.', 'small')
save('disk-storage-ownership.svg', a)

a = start(880, 'Disk-full investigation flow', 'Check block and inode pressure, scan the affected mount, check open deleted files, and follow either Docker object cleanup or Elasticsearch index deletion. Verify capacity and service health afterwards.')
text(a, 240, 34, 'Disk full: investigate before deleting', 'title')
box(a, 30, 60, 420, ['df -h + df -i', 'Which mount and which resource is full?'])
path(a, 'M240,146 L240,175')
box(a, 30, 185, 420, ['du → drill down → find / ncdu', 'Keep the scan on the affected filesystem'])
path(a, 'M240,271 L240,300')
box(a, 30, 310, 420, ['df remains high but files are missing?', 'lsof +L1 → review open deleted files'], '#e7e2d2')
path(a, 'M240,396 L240,425 L125,425 L125,453')
path(a, 'M240,425 L355,425 L355,453')
box(a, 20, 463, 210, ['Docker objects', 'system df -v', 'Review prune scope'], height=104)
box(a, 250, 463, 210, ['Elasticsearch volume', 'Map UUIDs via API', 'Review snapshots'], height=104)
path(a, 'M125,567 L125,601')
path(a, 'M355,567 L355,601')
box(a, 20, 611, 210, ['Choose scoped cleanup', 'If layers are missing:', 'recover, do not prune'], '#f1e0d9', 104)
box(a, 250, 611, 210, ['Delete reviewed index', 'through Elasticsearch', 'Never remove shards'], '#f1e0d9', 104)
path(a, 'M125,715 L125,743 L240,743 L240,768')
path(a, 'M355,715 L355,743 L240,743')
box(a, 30, 778, 420, ['Recheck df + Docker / cluster health', 'Fix retention and capacity monitoring'])
save('disk-full-decision-flow.svg', a)
print('Generated two disk-full diagrams.')
