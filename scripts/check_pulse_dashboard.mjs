// Test dashboard data/control logic against the built snapshot. This is NOT a
// browser or WebGL rendering test: minimal DOM and Plotly adapters capture calls.
import fs from 'node:fs/promises';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const elements=new Map(), plots=new Map();
class Element {
  constructor(){this.value='';this.textContent='';this.handlers={};this.children=[];}
  addEventListener(name,fn){this.handlers[name]=fn;}
  on(name,fn){this.handlers[name]=fn;}
  append(child){this.children.push(child);}
  replaceChildren(...children){this.children=children;}
  createTHead(){return this.add();} createTBody(){return this.add();}
  insertRow(){return this.add();} insertCell(){return this.add();}
  add(){const child=new Element();this.children.push(child);return child;}
  focus(){} select(){}
}
const get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
for(const [id,value] of Object.entries({region:'nino34',quantity:'2',view:'map',month:'2026-10'}))get(id).value=value;
let copied='';
const plotly={react:async(id,data,layout)=>{plots.set(id,{data,layout});}};
const context=vm.createContext({document:{getElementById:get,createElement:()=>new Element()},
  window:{Plotly:plotly},Plotly:plotly,URL,URLSearchParams,
  location:{href:'https://jltobias.github.io/JupyterLite-C3S-Atlas/pulse/',search:''},
  navigator:{clipboard:{writeText:async text=>{copied=text;}}},
  fetch:async path=>({ok:true,json:async()=>JSON.parse(await fs.readFile('_site/pulse/'+path,'utf8'))})});
await vm.runInContext(await fs.readFile('site/pulse/pulse.js','utf8'),context);
assert.equal(get('rank').textContent,'1 / 48');
assert.equal(plots.get('timeseries').data[0].y.at(-1),3.2345);
const source=JSON.parse(await fs.readFile('_site/pulse/data/monthly.json','utf8'));
let states=0;
for(const region of Object.keys(source.regions))for(const view of ['map','globe','heatmap','scene']){
  get('region').value=region;get('view').value=view;get('quantity').value='3';get('month').value='1997-12';
  await get('controls').handlers.change();
  const row=source.regions[region].rows.find(r=>r[0]==='1997-12-01');
  assert.equal(plots.get('timeseries').data[1].y[0],row[3]);
  assert.equal(get('anomaly').textContent,(row[2]>0?'+':'')+row[2].toFixed(2)+' °C');
  const spatial=plots.get('spatial');
  if(view==='globe'){
    const patches=spatial.data.slice(2);
    assert.equal(patches.length,region==='nino4'?2:1);
    assert.equal(patches[0].surfacecolor[0][0],row[2]);
  }
  if(view==='scene'||view==='heatmap'){
    assert.equal(spatial.data[0].z.length,12);assert.equal(spatial.data[0].z[0].length,47);
    assert.equal(spatial.data[0].z[11][18],row[2]);
    assert(spatial.data[0].z.flat().every(Number.isFinite));
  }
  assert.equal(get('values').children[0].children[1].children.length,4);
  states++;
}
get('month').value='2026-11';await get('controls').handlers.change();
assert.match(get('status').textContent,/Choose an archived month/);
get('timeseries').handlers.plotly_click({points:[{x:'2023-12-01'}]});
await get('controls').handlers.change();
assert.equal(get('month').value,'2023-12');
await get('share').handlers.click();
assert.equal(new URL(copied).searchParams.get('month'),'2023-12');
assert.equal(new URL(copied).searchParams.get('region'),'nino4');
const report={date:'2026-11-20',states,checks:['known snapshot rank','four regions × four views','relative time-series vs traditional spatial values','antimeridian patches','calendar indexing','partial-month rejection','chart selection','share parameters'],limits:['DOM/Plotly adapters only; no browser rendering, WebGL, CORS, or external GIS interaction.']};
await fs.writeFile('validation/pulse-dashboard.json',JSON.stringify(report,null,2)+'\n');
console.log('PASS Pulse dashboard control/data logic:',states,'region/view combinations; no browser rendering tested.');
