"""Execute every delivered notebook in a fresh local kernel and retain evidence.

Project: JupyterLite-C3S-Atlas; contributors (AI assisted); 2026-11-15.
Inputs: content notebooks/helpers/reference files. Outputs: executed notebooks and
validation/execution.json. Dependencies: nbclient, ipykernel, nbformat.
This validates native Python; browser/Pyodide verification is recorded separately.
"""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import time
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = []
    for path in sorted((ROOT / 'content').glob('*.ipynb')):
        started = time.perf_counter()
        notebook = nbformat.read(path, as_version=4)
        source_hash = hashlib.sha256('\n'.join(c.source for c in notebook.cells).encode()).hexdigest()
        km = KernelManager(kernel_name='python3')
        km.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
        client = NotebookClient(notebook, timeout=180, km=km,
                                resources={'metadata': {'path': str(ROOT / 'content')}},
                                allow_errors=False)
        try:
            client.execute()
            nbformat.write(notebook, path)
        finally:
            if km.has_kernel:
                km.shutdown_kernel(now=True)
        records.append(dict(notebook=path.name, status='passed',
                            seconds=round(time.perf_counter()-started, 2), source_sha256=source_hash,
                            code_cells=sum(c.cell_type == 'code' for c in notebook.cells)))
        print(f'PASS {path.name}', flush=True)
    out = ROOT / 'validation'
    out.mkdir(exist_ok=True)
    dependencies = {name: importlib.metadata.version(name) for name in
                    ['numpy', 'pandas', 'matplotlib', 'plotly', 'nbformat', 'nbclient', 'ipykernel']}
    report = dict(date='2026-11-20', python=sys.version, executable=sys.executable,
                  packages=dependencies, notebooks=records,
                  reference_manifest_sha256=hashlib.sha256((ROOT/'content/data/manifest.json').read_bytes()).hexdigest(),
                  helper_sha256=hashlib.sha256((ROOT/'content/atlas_helpers.py').read_bytes()).hexdigest(),
                  pulse_helper_sha256=hashlib.sha256((ROOT/'content/pulse_helpers.py').read_bytes()).hexdigest(),
                  pulse_manifest_sha256=hashlib.sha256((ROOT/'content/data/pulse/manifest.json').read_bytes()).hexdigest(),
                  limits=['Native Python execution is not browser execution.',
                          'No authenticated CDS retrieval or user-provided data analysis was run.'])
    (out/'execution.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
