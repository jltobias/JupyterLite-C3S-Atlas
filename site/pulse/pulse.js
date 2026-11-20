/* Original educational dashboard, 2026-11-20. Climate values are local snapshots. */
'use strict';
const el = id => document.getElementById(id);
const format = value => (value > 0 ? '+' : '') + value.toFixed(2);
const labels = {1:'Absolute SST',2:'Traditional anomaly',3:'Relative index'};
const config = {responsive:true,displaylogo:false};
const layout = {margin:{l:65,r:35,t:55,b:65},paper_bgcolor:'#fff',plot_bgcolor:'#fff',font:{family:'system-ui, sans-serif',color:'#12334b'}};
const radians = degrees => degrees * Math.PI/180;
function xyz(lon,lat,r=1.008) { return [r*Math.cos(radians(lat))*Math.cos(radians(lon)),r*Math.cos(radians(lat))*Math.sin(radians(lon)),r*Math.sin(radians(lat))]; }
function patch(ring,value,name,showscale) {
  const [w,s]=ring[0], [e,n]=ring[2], x=[],y=[],z=[],c=[];
  for(let j=0;j<8;j++) { const xx=[],yy=[],zz=[],cc=[]; for(let i=0;i<20;i++) { const p=xyz(w+(e-w)*i/19,s+(n-s)*j/7);xx.push(p[0]);yy.push(p[1]);zz.push(p[2]);cc.push(value); }x.push(xx);y.push(yy);z.push(zz);c.push(cc); }
  return {type:'surface',x,y,z,surfacecolor:c,colorscale:'RdBu',reversescale:true,cmin:-4,cmax:4,showscale,colorbar:{title:{text:'Δ °C'}},hovertemplate:`${name}: ${value.toFixed(4)} °C (region mean)<extra></extra>`};
}
async function start() {
  if(!window.Plotly) throw new Error('Plotly did not load; use the table, downloads, or book.');
  const responses=await Promise.all([fetch('data/monthly.json'),fetch('data/globe-base.json')]);
  if(responses.some(r=>!r.ok)) throw new Error('Snapshot files could not load.');
  const [data,globe]=await Promise.all(responses.map(r=>r.json()));
  const dates=data.regions.nino34.rows.map(r=>r[0]);
  const params=new URLSearchParams(location.search);
  if(params.has('region') && data.regions[params.get('region')]) el('region').value=params.get('region');
  if(['1','2','3'].includes(params.get('quantity'))) el('quantity').value=params.get('quantity');
  if(['map','globe','heatmap','scene'].includes(params.get('view'))) el('view').value=params.get('view');
  if(dates.includes(params.get('month')+'-01')) el('month').value=params.get('month');
  async function render() {
    const key=el('region').value, region=data.regions[key], q=Number(el('quantity').value), view=el('view').value;
    const date=el('month').value+'-01', index=dates.indexOf(date);
    if(index<0) { el('status').textContent='Choose an archived month from January 1979 through October 2026.';return; }
    const row=region.rows[index], peers=region.rows.filter(r=>r[0].slice(5,7)===date.slice(5,7));
    const rank=1+peers.filter(r=>r[2]>row[2]).length;
    el('absolute').textContent=row[1].toFixed(2)+' °C';el('anomaly').textContent=format(row[2])+' °C';el('relative').textContent=format(row[3])+' °C';el('rank').textContent=`${rank} / ${peers.length}`;
    el('status').textContent=`${region.name} · ${date.slice(0,7)} · archived ${data.snapshot}. Select a point or change the controls.`;
    const series=[{type:'scatter',mode:'lines',x:dates,y:region.rows.map(r=>r[q]),name:labels[q],line:{color:q===3?'#166f83':'#ad4f20',width:2},hovertemplate:'%{x}<br>%{y:.4f} °C<extra></extra>'},
      {type:'scatter',mode:'markers',x:[date],y:[row[q]],name:'Selected month',marker:{size:12,color:'#142c42'},hovertemplate:'%{x}<br>%{y:.4f} °C<extra></extra>'}];
    await Plotly.react('timeseries',series,{...layout,title:{text:`${region.name} · ${labels[q]}`},showlegend:false,xaxis:{title:{text:'Month'},rangeslider:{visible:true,thickness:.12}},yaxis:{title:{text:q===1?'SST (°C)':'°C; reference 1991–2020'}},uirevision:'timeseries-'+key+'-'+q},config);
    let traces=[], viewLayout={...layout,title:{text:`${region.name} · ${date.slice(0,7)}`},showlegend:false};
    if(view==='map') {
      const x=[],y=[];
      for(const line of data.coastlines) {let prev=null;for(const p of line) {if(prev!==null && Math.abs(p[0]-prev)>180){x.push(null);y.push(null);}x.push(p[0]);y.push(p[1]);prev=p[0];}x.push(null);y.push(null);}
      traces.push({type:'scatter',mode:'lines',x,y,line:{color:'#718797',width:1},hoverinfo:'skip'});
      for(const [id,r] of Object.entries(data.regions)) for(const ring of r.rings) traces.push({type:'scatter',mode:'lines',x:ring.map(p=>p[0]),y:ring.map(p=>p[1]),line:{color:id===key?'#9d4823':'#687c8e',width:id===key?3:1},fill:id===key?'toself':'none',fillcolor:'rgba(230,159,0,.3)',hovertemplate:r.name+' definition box<extra></extra>'});
      Object.assign(viewLayout,{xaxis:{title:{text:'Longitude (°)'},range:[-180,180]},yaxis:{title:{text:'Latitude (°)'},range:[-35,35]},uirevision:'map'});
      el('view-note').textContent='The highlight locates the selected region, not SST pixels. Boxes overlap. Niño 4 crosses ±180°. Coastlines: Natural Earth. Values are in the table.';
    } else if(view==='globe') {
      traces=[...globe.data,...region.rings.map((ring,i)=>patch(ring,row[2],region.name,i===0))];
      Object.assign(viewLayout,{scene:globe.layout.scene,uirevision:'globe'});
      el('view-note').textContent='Colour is one traditional regional anomaly, on a fixed −4 to +4 °C scale (values outside saturate). Unit sphere; patch offset is for display, not height. Rotate to see the Pacific. Use 2D and the table if WebGL is unavailable.';
    } else {
      const years=Array.from({length:47},(_,i)=>1979+i),months=Array.from({length:12},(_,i)=>i+1);
      const z=months.map((m,i)=>years.map((y,j)=>region.rows[j*12+i][2]));
      traces=[{type:view==='scene'?'surface':'heatmap',x:years,y:months,z,colorscale:'RdBu',reversescale:true,...(view==='scene'?{cmin:-4,cmax:4}:{zmin:-4,zmax:4}),colorbar:{title:{text:'Δ °C'}}}];
      Object.assign(viewLayout,{title:{text:`${region.name} · traditional anomaly · 1979–2025`},xaxis:{title:{text:'Year'}},yaxis:{title:{text:'Calendar month'},dtick:1},scene:{xaxis:{title:{text:'Year'}},yaxis:{title:{text:'Month'}},zaxis:{title:{text:'Anomaly (°C)'}}},uirevision:view+'-'+key});
      el('view-note').textContent='Calendar views show traditional anomalies for complete years 1979–2025, independently of the selected month. Height in 3D means °C. Scale: −4 to +4 °C, with saturation outside. Switch to the heatmap for unobstructed comparison; no missing 2026 months are filled.';
    }
    await Plotly.react('spatial',traces,viewLayout,config);
    const table=document.createElement('table'), head=table.createTHead().insertRow();
    for(const label of ['Region','Month','SST (°C)','Traditional (°C)','Relative (°C)']) {const th=document.createElement('th');th.scope='col';th.textContent=label;head.append(th);}
    const body=table.createTBody();
    for(const r of Object.values(data.regions)) {const values=r.rows[index];const tr=body.insertRow();for(const value of [r.name,date.slice(0,7),...values.slice(1).map(v=>v.toFixed(4))]) tr.insertCell().textContent=value;}
    el('values').replaceChildren(table);el('share-url').hidden=true;
  }
  // Serialize redraws so rapid control changes cannot leave an older view last.
  let queue=Promise.resolve();
  const redraw=()=>{queue=queue.then(render).catch(report);return queue;};
  el('controls').addEventListener('submit',e=>e.preventDefault());
  el('controls').addEventListener('change',redraw);
  await redraw();
  el('timeseries').on('plotly_click',event=>{const date=String(event.points[0].x).slice(0,7);if(dates.includes(date+'-01')){el('month').value=date;redraw();}});
  el('share').addEventListener('click',async()=>{
    const url=new URL(location.href);url.search=new URLSearchParams({region:el('region').value,quantity:el('quantity').value,view:el('view').value,month:el('month').value}).toString();
    el('share-url').value=url.href;el('share-url').hidden=false;
    try {await navigator.clipboard.writeText(url.href);el('status').textContent='View link copied. It identifies this archived snapshot.';} catch {el('status').textContent='Copy the view URL from the text field.';el('share-url').focus();el('share-url').select();}
  });
}
function report(error) {el('status').textContent='Interactive view unavailable: '+error.message+' Tables, source downloads, and notebooks remain available.';}
start().catch(report);
