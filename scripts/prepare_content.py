"""Synchronise shared documentation and the deterministic import fixture.

Project: JupyterLite-C3S-Atlas; contributors (AI assisted); 2026-11-15.
Inputs: docs, curriculum, original generator. Outputs: portable content tree.
Runtime: project Python, pandas, NumPy. No external data access.
"""
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'content'))
from atlas_helpers import monthly_demo


def main():
    content = ROOT/'content'
    for name in ['credits.md', 'learning-resources.md', 'data-guide.md']:
        shutil.copy2(ROOT/'docs'/name, content/name)
    shutil.copytree(ROOT/'licenses', content/'licenses', dirs_exist_ok=True)
    shutil.copy2(ROOT/'assets/PROVENANCE.md', content/'assets/PROVENANCE.md')
    examples = content/'data/examples'
    examples.mkdir(parents=True, exist_ok=True)
    monthly_demo()[['date', 't']].rename(columns={'t': 'value'}).to_csv(
        examples/'monthly_series.csv', index=False, date_format='%Y-%m-%d', float_format='%.6f')
    metadata = dict(data_kind='synthetic', source='Original monthly_demo(), atlas_helpers.py; seed 381',
                    variable='fictional near-surface temperature', units='°C', region='fictional region',
                    statistic='invented monthly mean', reference_period='none; absolute invented values',
                    licence='MIT, original project teaching data',
                    transformations='Generator output rounded to six decimal places for import fixture; no C3S measurements')
    (examples/'monthly_series.json').write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
    chapters = json.loads((ROOT/'curriculum.json').read_text(encoding='utf-8'))
    toc = 'format: jb-book\nroot: index\nchapters:\n'
    toc += ''.join('  - file: '+entry['slug']+'\n' for entry in chapters)
    toc += '  - file: variables\n  - file: data-guide\n  - file: learning-resources\n  - file: credits\n'
    (content/'_toc.yml').write_text(toc, encoding='utf-8')
    print('Prepared portable documentation, table of contents, and synthetic import fixture.')


if __name__ == '__main__':
    main()
