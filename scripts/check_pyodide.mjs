/** Execute all lesson cells in the exact Pyodide WebAssembly runtime under Node.
 * Project: JupyterLite-C3S-Atlas; contributors (AI assisted); 2026-11-15.
 * Inputs: a locally cached Pyodide distribution/wheels, content, built piplite wheel.
 * Output: validation/pyodide.json. This is not a browser UI or service-worker test.
 * Usage: node scripts/check_pyodide.mjs PATH_TO_PYODIDE_CACHE
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const root = process.cwd();
const cache = path.resolve(process.argv[2] || '.work/pyodide');
const { loadPyodide } = await import(pathToFileURL(path.join(cache, 'pyodide.mjs')));
const messages = [];
const py = await loadPyodide({ indexURL: cache + path.sep, packageCacheDir: cache,
  stdout: text => { if (messages.length < 100) messages.push(text.slice(0, 500)); },
  stderr: text => { if (messages.length < 100) messages.push(text.slice(0, 500)); },
});
await py.loadPackage(['numpy', 'pandas', 'matplotlib', 'ipython', 'micropip']);

async function mountTree(host, guest) {
  py.FS.mkdirTree(guest);
  for (const entry of await fs.readdir(host, { withFileTypes: true })) {
    if (entry.name.startsWith('_') || entry.name.startsWith('.')) continue;
    const source = path.join(host, entry.name), dest = guest + '/' + entry.name;
    if (entry.isDirectory()) await mountTree(source, dest);
    else py.FS.writeFile(dest, await fs.readFile(source));
  }
}
await mountTree(path.join(root, 'content'), '/course');
py.FS.mkdirTree('/wheels');
const wheels = (await fs.readdir(cache)).filter(name => /^(plotly|narwhals)-.*\.whl$/.test(name));
const pipliteDir = path.join(root, '_site/lite/extensions/@jupyterlite/pyodide-kernel-extension/static/pypi');
const piplite = (await fs.readdir(pipliteDir)).find(name => /^piplite-.*\.whl$/.test(name));
if (!piplite || wheels.length !== 2) throw new Error('Cache needs Plotly, Narwhals, and the built piplite wheel.');
for (const name of wheels) py.FS.writeFile('/wheels/' + name, await fs.readFile(path.join(cache, name)));
py.FS.writeFile('/wheels/' + piplite, await fs.readFile(path.join(pipliteDir, piplite)));
await py.runPythonAsync(`
import os, sys, micropip
os.chdir('/course')
os.environ['MPLBACKEND'] = 'Agg'
sys.path.insert(0, '/course')
await micropip.install(${JSON.stringify(wheels.map(n=>'emfs:/wheels/'+n))})
await micropip.install('emfs:/wheels/${piplite}', deps=False)
`);

const records = [];
for (const name of (await fs.readdir(path.join(root, 'content'))).filter(n => n.endsWith('.ipynb')).sort()) {
  const notebook = JSON.parse(await fs.readFile(path.join(root, 'content', name), 'utf8'));
  const globals = py.runPython('dict(__name__="__main__")');
  try {
    for (const [index, cell] of notebook.cells.entries()) {
      if (cell.cell_type !== 'code') continue;
      const source = Array.isArray(cell.source) ? cell.source.join('') : cell.source;
      try { await py.runPythonAsync(source, { globals }); }
      catch (error) { throw new Error(`${name} cell ${index}: ${error.message}`); }
    }
    records.push({ notebook: name, status: 'passed' });
    console.log('PASS WebAssembly ' + name);
  } finally { globals.destroy(); }
}
const versions = JSON.parse(py.runPython(`
import json, sys, importlib.metadata
json.dumps(dict(python=sys.version, packages={name:importlib.metadata.version(name) for name in ['numpy','pandas','matplotlib','plotly','piplite']}))
`));
const report = { date: '2026-11-15', node: process.version, pyodide: py.version, ...versions,
  notebooks: records, limits: ['Node-hosted WebAssembly, not browser UI.',
    'Packages were loaded from a local cache; browser network and service-worker behavior remain untested.',
    'No WebGL rendering was tested.'], runtime_messages: messages };
await fs.writeFile(path.join(root, 'validation/pyodide.json'), JSON.stringify(report, null, 2) + '\n');
console.log('WebAssembly compatibility check passed.');
