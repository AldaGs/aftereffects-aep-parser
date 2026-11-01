// Approximate preview renderer for motion.schema.json authoring files, for checking a
// layout without After Effects. Renders the first composition to JPEG frames in headless Chromium.
//
// Usage: node scripts/preview.js <in.json> <outdir> [fps=15] [scale=0.5] [from=0] [to=duration]
//   contact sheet: ffmpeg -i <outdir>/f%05d.jpg -frames:v 1 -vf "scale=480:-1,tile=4x5" sheet.jpg
//   video:         ffmpeg -framerate <fps> -i <outdir>/f%05d.jpg -pix_fmt yuv420p preview.mp4
// Needs Playwright with Chromium (npm install playwright && npx playwright install chromium).
//
// Supported: shape/text/null/precomp layers, parenting, keyframes (preset and custom ease),
// JS expressions using time/value, shape groups with transforms, trim paths, stroke caps/joins/dashes,
// track mattes, enabled:false. Not rendered: effects, adjustment layers, footage, 3D, masks,
// auto-bezier spatial curves (paths are drawn straight). Text uses Liberation fonts for Arial/Georgia.
// Other fonts: set PREVIEW_FONTS to a folder of .ttf/.otf files named <Family>-<Style>.ttf (e.g. Chonburi-Regular.ttf);
// a layer whose PostScript font name starts with <Family> is drawn with that file.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const pageCode = String.raw`
let PROJ, COMPS = {};
function hex(c){ if (Array.isArray(c)) return c; c=c.replace('#',''); const n=parseInt(c,16); return [(n>>16&255)/255,(n>>8&255)/255,(n&255)/255,1]; }
function css(c, a){ c = typeof c === 'string' ? hex(c) : c; return 'rgba('+Math.round(c[0]*255)+','+Math.round(c[1]*255)+','+Math.round(c[2]*255)+','+(a==null?1:a)+')'; }
function bez(x1,y1,x2,y2,x){ // solve cubic-bezier timing
  let lo=0, hi=1, t=x; for(let i=0;i<40;i++){ t=(lo+hi)/2; const xt=3*(1-t)*(1-t)*t*x1+3*(1-t)*t*t*x2+t*t*t; if(xt<x) lo=t; else hi=t; }
  return 3*(1-t)*(1-t)*t*y1+3*(1-t)*t*t*y2+t*t*t; }
function infl(k,side){ if(!k.ease) return 1/3; if(typeof k.ease==='object'){ const v=k.ease[side+'Influence']; return Math.max(0.001,(v==null?33.33:v)/100); } if(k.ease==='linear') return 0.001; return 0.75; }
function lerp(a,b,u){ if (typeof a==='string') a=hex(a); if (typeof b==='string') b=hex(b);
  if (Array.isArray(a)) return a.map((v,i)=>v+(b[i]-v)*u); return a+(b-a)*u; }
function evalProp(p, t, def){
  if (p==null) return def;
  let v;
  if (typeof p!=='object' || Array.isArray(p)) v=p;
  else if (p.keyframes){
    const ks=p.keyframes;
    if (t<=ks[0].time) v=ks[0].value; else if (t>=ks[ks.length-1].time) v=ks[ks.length-1].value;
    else { for(let i=0;i<ks.length-1;i++){ const a=ks[i], b=ks[i+1]; if(t>=a.time && t<b.time){
      if (a.interp==='hold'){ v=a.value; break; }
      const x=(t-a.time)/(b.time-a.time); const i0=infl(a,'out'), i1=infl(b,'in');
      const y = (i0===1/3 && i1===1/3) ? x : bez(i0, i0===1/3?1/3:0, 1-i1, i1===1/3?2/3:1, x);
      v=lerp(a.value,b.value,y); break; } } }
  } else v = p.value!=null ? p.value : def;
  if (typeof v==='string' && v[0]==='#') v=hex(v);
  if (p && typeof p==='object' && p.expression){
    try { v = (new Function('time','value','thisComp','return eval('+JSON.stringify(p.expression)+')'))(t, v, null); } catch(e){ console.log('expr err', p.expression, e.message); }
  }
  return v==null?def:v;
}
// 2D affine [a,b,c,d,e,f]
function mul(m,n){ return [m[0]*n[0]+m[2]*n[1], m[1]*n[0]+m[3]*n[1], m[0]*n[2]+m[2]*n[3], m[1]*n[2]+m[3]*n[3], m[0]*n[4]+m[2]*n[5]+m[4], m[1]*n[4]+m[3]*n[5]+m[5]]; }
function layerMatrix(comp, L, t){
  const tr=L.transform||{};
  const defPos = [comp.width/2, comp.height/2];
  let defAnc=[0,0]; if (L.type==='precomp'){ const s=COMPS[L.source]; defAnc=[s.width/2,s.height/2]; } if (L.type==='null') defAnc=[50,50];
  const P=evalProp(tr.position,t,defPos), A=evalProp(tr.anchorPoint,t,defAnc), S=evalProp(tr.scale,t,[100,100]), R=evalProp(tr.rotation,t,0)*Math.PI/180;
  const sx=S[0]/100, sy=S[1]/100, c=Math.cos(R), s=Math.sin(R);
  let m=[c*sx, s*sx, -s*sy, c*sy, 0, 0];
  m[4]=P[0]-(m[0]*A[0]+m[2]*A[1]); m[5]=P[1]-(m[1]*A[0]+m[3]*A[1]);
  if (L.parent){ const pl=comp.layers.find(x=>x.name===L.parent); if(pl) m=mul(layerMatrix(comp,pl,t),m); }
  return m;
}
// ---- shapes as polylines ----
function sampleBez(p0,c0,c1,p1,out,n){ for(let i=1;i<=n;i++){ const u=i/n, a=(1-u)*(1-u)*(1-u), b=3*(1-u)*(1-u)*u, c=3*(1-u)*u*u, d=u*u*u;
  out.push([a*p0[0]+b*c0[0]+c*c1[0]+d*p1[0], a*p0[1]+b*c0[1]+c*c1[1]+d*p1[1]]); } }
function rectPts(sz,pos,r){ const w=sz[0]/2,h=sz[1]/2; r=Math.min(r||0,w,h); const pts=[]; const cx=pos[0], cy=pos[1];
  const corners=[[cx+w-r,cy-h+r,-90],[cx+w-r,cy+h-r,0],[cx-w+r,cy+h-r,90],[cx-w+r,cy-h+r,180]];
  for(const [x,y,a0] of corners){ for(let i=0;i<=8;i++){ const a=(a0+90*i/8)*Math.PI/180; pts.push([x+Math.cos(a)*r,y+Math.sin(a)*r]); if(!r) break; } }
  return {pts, closed:true}; }
function ellPts(sz,pos){ const pts=[]; for(let i=0;i<64;i++){ const a=-Math.PI/2+i/64*Math.PI*2; pts.push([pos[0]+Math.cos(a)*sz[0]/2,pos[1]+Math.sin(a)*sz[1]/2]); } return {pts,closed:true}; }
function pathPts(p){ const v=p.vertices, it=p.inTangents||[], ot=p.outTangents||[]; const pts=[v[0].slice()]; const n=v.length; const segs=p.closed?n:n-1;
  for(let i=0;i<segs;i++){ const a=v[i], b=v[(i+1)%n], o=ot[i]||[0,0], ii=it[(i+1)%n]||[0,0];
    const curved = o[0]||o[1]||ii[0]||ii[1];
    sampleBez(a,[a[0]+o[0],a[1]+o[1]],[b[0]+ii[0],b[1]+ii[1]],b,pts,curved?24:1); }
  if (p.closed) pts.pop(); return {pts, closed:!!p.closed}; }
function trimPoly(poly, s, e, off){
  let pts=poly.pts.slice(); if (poly.closed) pts.push(pts[0]);
  const L=[0]; for(let i=1;i<pts.length;i++) L.push(L[i-1]+Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]));
  const tot=L[L.length-1]; if(!tot) return [];
  let a=s/100+off/360, b=e/100+off/360; if (e<=s) return [];
  const pieces=[]; const seg=(x,y)=>{ // x<y in [0,1]
    const out=[]; const at=d=>{ for(let i=1;i<L.length;i++) if(L[i]>=d){ const u=(d-L[i-1])/((L[i]-L[i-1])||1); return [pts[i-1][0]+(pts[i][0]-pts[i-1][0])*u, pts[i-1][1]+(pts[i][1]-pts[i-1][1])*u]; } return pts[pts.length-1]; };
    out.push(at(x*tot)); for(let i=0;i<L.length;i++) if(L[i]>x*tot && L[i]<y*tot) out.push(pts[i]); out.push(at(y*tot)); return out; };
  a=a-Math.floor(a); b=a+(e-s)/100;
  if (b<=1) pieces.push(seg(a,b)); else { pieces.push(seg(a,1)); pieces.push(seg(0,b-1)); }
  return pieces;
}
function buildGroup(items, t){
  // returns {ops: [...drawn later-first...], paths: [...]}
  let paths=[]; const ops=[];
  for (const it of items){
    if (it.type==='rect') paths.push(rectPts(evalProp(it.size,t,[100,100]), evalProp(it.position,t,[0,0]), evalProp(it.roundness,t,0)));
    else if (it.type==='ellipse') paths.push(ellPts(evalProp(it.size,t,[100,100]), evalProp(it.position,t,[0,0])));
    else if (it.type==='path') paths.push(pathPts(it.path));
    else if (it.type==='group'){ const g=buildGroup(it.items||[],t); const tr=it.transform;
      if (tr){ const P=evalProp(tr.position,t,[0,0]), An=evalProp(tr.anchorPoint,t,[0,0]), S=evalProp(tr.scale,t,[100,100]), R=evalProp(tr.rotation,t,0)*Math.PI/180, O=evalProp(tr.opacity,t,100)/100;
        const c=Math.cos(R), sn=Math.sin(R), sx=S[0]/100, sy=S[1]/100;
        const f=q=>{ const x=(q[0]-An[0])*sx, y=(q[1]-An[1])*sy; return [P[0]+x*c-y*sn, P[1]+x*sn+y*c]; };
        const seen=new Set(); const fix=p=>{ if(seen.has(p)) return; seen.add(p); p.pts=p.pts.map(f); };
        g.paths.forEach(fix); g.ops.forEach(o=>{ o.paths.forEach(fix); o.op*=O; }); }
      ops.push(...g.ops); paths=paths.concat(g.paths); }
    else if (it.type==='trim'){ const s=evalProp(it.start,t,0), e=evalProp(it.end,t,100), o=evalProp(it.offset,t,0);
      paths=paths.map(p=>({pts:p.pts, closed:p.closed, trim:[s,e,o]})); }
    else if (it.type==='fill') ops.push({kind:'fill', color:evalProp(it.color,t,[1,0,0,1]), op:evalProp(it.opacity,t,100), paths:paths.slice()});
    else if (it.type==='stroke') ops.push({kind:'stroke', color:evalProp(it.color,t,[1,1,1,1]), op:evalProp(it.opacity,t,100), w:evalProp(it.strokeWidth,t,2), cap:it.lineCap, join:it.lineJoin, dash:it.dashes&&[evalProp(it.dashes.dash,t,10), evalProp(it.dashes.gap,t,evalProp(it.dashes.dash,t,10)), evalProp(it.dashes.offset,t,0)], paths:paths.slice()});
  }
  return {ops, paths};
}
function drawShape(ctx, L, t){
  const g=buildGroup(L.shapes||[], t);
  for (let i=g.ops.length-1;i>=0;i--){ const op=g.ops[i];
    ctx.beginPath();
    if (op.kind==='fill'){ for(const p of op.paths){ if(p.trim && (p.trim[1]-p.trim[0])<=0) continue; ctx.moveTo(p.pts[0][0],p.pts[0][1]); for(const q of p.pts) ctx.lineTo(q[0],q[1]); ctx.closePath(); }
      ctx.fillStyle=css(op.color, op.op/100); ctx.fill('nonzero'); }
    else { for(const p of op.paths){ const pieces = p.trim ? trimPoly(p,...p.trim) : [p.closed? p.pts.concat([p.pts[0]]) : p.pts];
        for(const pc of pieces){ if(!pc.length) continue; ctx.moveTo(pc[0][0],pc[0][1]); for(const q of pc) ctx.lineTo(q[0],q[1]); } }
      ctx.strokeStyle=css(op.color, op.op/100); ctx.lineWidth=op.w; ctx.lineJoin=op.join||'miter'; ctx.lineCap=op.cap==='projecting'?'square':(op.cap||'butt'); ctx.setLineDash(op.dash?op.dash.slice(0,2):[]); ctx.lineDashOffset=op.dash?-op.dash[2]:0; if (op.w>0) ctx.stroke(); }
  }
}
function drawText(ctx, L){
  const T=L.text; const size=T.fontSize||48; const f=T.font||''; const bold=/Bold/.test(f), ital=/Italic/.test(f);
  const own=(window.FONTFAMS||[]).find(n=>f.indexOf(n)===0);
  const fam=own?'"'+own+'"':/Georgia/.test(f)?'"Liberation Serif", Georgia, serif':'"Liberation Sans", Arial';
  ctx.font=(ital?'italic ':'')+(bold?'bold ':'')+size+'px '+fam; ctx.letterSpacing=((T.tracking||0)/1000*size)+'px';
  ctx.fillStyle=css(T.fillColor||'#ffffff'); ctx.textAlign = T.justification==='center'?'center':(T.justification==='right'?'right':'left'); ctx.textBaseline='alphabetic';
  const lines=T.string.split(/\r|\n/); const lead=T.leading||size*1.2;
  lines.forEach((ln,i)=>ctx.fillText(ln,0,i*lead));
}
const OFF=[];
function offscreen(i){ const cv=document.getElementById('cv'); if(!OFF[i]){ const c=document.createElement('canvas'); OFF[i]=c; }
  const c=OFF[i]; if(c.width!==cv.width||c.height!==cv.height){ c.width=cv.width; c.height=cv.height; }
  const x=c.getContext('2d'); x.setTransform(1,0,0,1,0,0); x.globalCompositeOperation='source-over'; x.clearRect(0,0,c.width,c.height); return x; }
function drawLayer(ctx, comp, L, t, op){
  const st=L.startTime||0; const m=layerMatrix(comp,L,t);
  ctx.save(); ctx.transform(...m); ctx.globalAlpha*=op;
  if (L.type==='shape') drawShape(ctx,L,t);
  else if (L.type==='text') drawText(ctx,L);
  else if (L.type==='precomp') renderComp(ctx, COMPS[L.source], t-st);
  ctx.restore(); }
function renderComp(ctx, comp, t){
  for (let i=comp.layers.length-1;i>=0;i--){ const L=comp.layers[i];
    const st=L.startTime||0; const inP=L.in!=null?L.in:st; let outP=L.out!=null?L.out:comp.duration;
    if (L.type==='precomp' && L.out==null) outP=st+COMPS[L.source].duration;
    if (t<inP || t>=outP) continue;
    const op=evalProp((L.transform||{}).opacity,t,100)/100; if (op<=0) continue;
    if (L.enabled===false || L.type==='adjustment') continue;
    if (L.trackMatte){ const mL=comp.layers.find(x=>x.name===L.trackMatte.target); if(!mL) continue;
      const base=ctx.getTransform(), ga=ctx.globalAlpha;
      const a=offscreen(0), b=offscreen(1);
      a.setTransform(base); a.globalAlpha=1; drawLayer(a,comp,L,t,op);
      b.setTransform(base); b.globalAlpha=1; const mop=evalProp((mL.transform||{}).opacity,t,100)/100; drawLayer(b,comp,mL,t,mop);
      a.setTransform(1,0,0,1,0,0); a.globalCompositeOperation=/Inverted/.test(L.trackMatte.type)?'destination-out':'destination-in'; a.drawImage(b.canvas,0,0); a.globalCompositeOperation='source-over';
      ctx.save(); ctx.setTransform(1,0,0,1,0,0); ctx.globalAlpha=ga; ctx.drawImage(a.canvas,0,0); ctx.restore(); continue; }
    drawLayer(ctx,comp,L,t,op);
  }
}
window.setup=(json, scale)=>{ PROJ=json; for(const c of PROJ.compositions) COMPS[c.name]=c; const c=PROJ.compositions[0];
  const cv=document.getElementById('cv'); cv.width=c.width*scale; cv.height=c.height*scale; window.SCALE=scale; return c.duration; };
window.frame=(t)=>{ const c=PROJ.compositions[0]; const cv=document.getElementById('cv'); const ctx=cv.getContext('2d');
  ctx.setTransform(1,0,0,1,0,0); ctx.globalAlpha=1; ctx.fillStyle=c.backgroundColor||'#000'; ctx.fillRect(0,0,cv.width,cv.height);
  ctx.setTransform(SCALE,0,0,SCALE,0,0); renderComp(ctx,c,t); return cv.toDataURL('image/jpeg',0.9); };
`;

(async () => {
  const [inp, outdir, fps = '15', scale = '0.5', from = '0', to] = process.argv.slice(2);
  const json = JSON.parse(fs.readFileSync(inp, 'utf8'));
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();
  page.on('console', m => console.log('page:', m.text()));
  const fontDir = process.env.PREVIEW_FONTS, fams = [];
  let faces = '';
  if (fontDir) for (const fn of fs.readdirSync(fontDir).filter(n => /\.(ttf|otf)$/i.test(n))) {
    const fam = fn.replace(/\.(ttf|otf)$/i, '').split('-')[0];
    fams.push(fam);
    faces += '@font-face{font-family:"' + fam + '";src:url(data:font/ttf;base64,' + fs.readFileSync(path.join(fontDir, fn)).toString('base64') + ');}';
  }
  await page.setContent('<style>' + faces + '</style><canvas id="cv"></canvas><script>window.FONTFAMS=' + JSON.stringify(fams) + ';' + pageCode + '</script>');
  for (const fam of fams) await page.evaluate(f => document.fonts.load('48px "' + f + '"'), fam);
  const dur = await page.evaluate(([j, s]) => window.setup(j, s), [json, parseFloat(scale)]);
  const end = to ? parseFloat(to) : dur;
  const f = parseFloat(fps);
  let n = 0;
  for (let t = parseFloat(from); t < end - 1e-6; t += 1 / f) {
    const url = await page.evaluate(tt => window.frame(tt), t);
    fs.writeFileSync(path.join(outdir, 'f' + String(n++).padStart(5, '0') + '.jpg'), Buffer.from(url.split(',')[1], 'base64'));
  }
  console.log('frames', n);
  await browser.close();
})();
