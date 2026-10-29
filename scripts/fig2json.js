// Figma .fig -> authoring JSON. Each top-level frame (>=1000px wide) on matching pages becomes a comp.
// usage: unzip file.fig -d figdir && node scripts/fig2json.js <figdir> <outdir> [pageRegex]
//   -> outdir/project.json, outdir/images/*, outdir/comps/NN.json (one comp each: ExtendScript chokes on big files)
//   then: json2jsx -i outdir/comps/NN.json -aep outdir/project.aep for each, and run them in one AE session.
// needs: npm install (kiwi-schema)
const fs=require('fs'),path=require('path'),zlib=require('zlib'),kiwi=require('kiwi-schema');
const [dir,out,pageRe='.']=process.argv.slice(2);
const b=fs.readFileSync(path.join(dir,'canvas.fig'));let o=12;const ch=[];
while(o<b.length){const n=b.readUInt32LE(o);ch.push(b.subarray(o+4,o+4+n));o+=4+n;}
const un=c=>c[0]===0x28&&c[1]===0xb5?zlib.zstdDecompressSync(c):zlib.inflateRawSync(c);
const msg=kiwi.compileSchema(kiwi.decodeBinarySchema(un(ch[0]))).decodeMessage(un(ch[1]));
const N=msg.nodeChanges,blobs=msg.blobs;
const id=g=>g&&g.sessionID+':'+g.localID, kids={};
N.forEach(n=>n.parentIndex&&(kids[id(n.parentIndex.guid)]??=[]).push(n));
for(const k in kids)kids[k].sort((a,b)=>a.parentIndex.position<b.parentIndex.position?-1:1); // bottom -> top
const hex=u=>Buffer.from(u).toString('hex');
fs.mkdirSync(path.join(out,'images'),{recursive:true});

// image hash -> {file,w,h,id}
const imgs={};
function image(h){
  if(imgs[h]!==undefined)return imgs[h];
  const src=path.join(dir,'images',h);
  if(!fs.existsSync(src))return imgs[h]=null;
  const d=fs.readFileSync(src);let w,hh,ext;
  if(d[0]===0x89){ext='png';w=d.readUInt32BE(16);hh=d.readUInt32BE(20);}
  else if(d[0]===0xff){ext='jpg';let i=2;while(i<d.length){const m=d[i+1],len=d.readUInt16BE(i+2);if(m>=0xc0&&m<=0xcf&&m!==0xc4&&m!==0xc8&&m!==0xcc){hh=d.readUInt16BE(i+5);w=d.readUInt16BE(i+7);break;}i+=2+len;}}
  else if(d.subarray(0,4).toString()==='GIF8'){ext='gif';w=d.readUInt16LE(6);hh=d.readUInt16LE(8);}
  else return imgs[h]=null; // ponytail: webp/unknown skipped, AE cannot import them
  const file=path.join(out,'images',h+'.'+ext);fs.copyFileSync(src,file);
  return imgs[h]={file:path.resolve(file).replace(/\\/g,'/'),w,h:hh,id:'img_'+h.slice(0,10)};
}

// Figma path command blob -> AE bezier paths (0 close, 1 move, 2 line, 3 quad, 4 cubic)
function paths(blobIdx){
  const d=Buffer.from(blobs[blobIdx].bytes),res=[];let cur=null,i=0;
  const f=()=>{const v=d.readFloatLE(i);i+=4;return v;};
  const end=()=>{if(cur&&cur.v.length>1)res.push(cur);cur=null;};
  while(i<d.length){const c=d[i++];
    if(c===0){if(cur){const n=cur.v.length-1,a=cur.v[0],z=cur.v[n];
        if(n>0&&Math.abs(a[0]-z[0])<1e-3&&Math.abs(a[1]-z[1])<1e-3){cur.i[0]=cur.i[n];cur.v.pop();cur.i.pop();cur.o.pop();}
        cur.closed=true;}end();}
    else if(c===1){end();cur={v:[[f(),f()]],i:[[0,0]],o:[[0,0]],closed:false};}
    else if(c===2){cur.v.push([f(),f()]);cur.i.push([0,0]);cur.o.push([0,0]);}
    else if(c===3){const p=cur.v.at(-1),q=[f(),f()],e=[f(),f()];
      cur.o[cur.o.length-1]=[(q[0]-p[0])*2/3,(q[1]-p[1])*2/3];cur.v.push(e);cur.i.push([(q[0]-e[0])*2/3,(q[1]-e[1])*2/3]);cur.o.push([0,0]);}
    else if(c===4){const p=cur.v.at(-1),c1=[f(),f()],c2=[f(),f()],e=[f(),f()];
      cur.o[cur.o.length-1]=[c1[0]-p[0],c1[1]-p[1]];cur.v.push(e);cur.i.push([c2[0]-e[0],c2[1]-e[1]]);cur.o.push([0,0]);}
    else break;}
  end();
  const r=x=>Math.round(x*100)/100;
  return res.map(p=>({type:'path',path:{closed:p.closed,vertices:p.v.map(a=>a.map(r)),inTangents:p.i.map(a=>a.map(r)),outTangents:p.o.map(a=>a.map(r))}}));
}
const paint=ps=>(ps||[]).filter(p=>p.visible!==false&&(p.type==='SOLID'||p.type.startsWith('GRADIENT')));
// ponytail: gradients flattened to their first stop color
function color(p){const c=p.type==='SOLID'?p.color:p.stops[0].color;return{color:[c.r,c.g,c.b],opacity:Math.round((p.opacity??1)*(c.a??1)*100)};}
const toHex=c=>'#'+[c.r,c.g,c.b].map(v=>Math.round(v*255).toString(16).padStart(2,'0')).join('');

const I={a:1,b:0,c:0,d:1,x:0,y:0};
const mul=(A,B)=>({a:A.a*B.a+A.c*B.b,b:A.b*B.a+A.d*B.b,c:A.a*B.c+A.c*B.d,d:A.b*B.c+A.d*B.d,x:A.a*B.x+A.c*B.y+A.x,y:A.b*B.x+A.d*B.y+A.y});
const mat=t=>t?{a:t.m00,b:t.m10,c:t.m01,d:t.m11,x:t.m02,y:t.m12}:I;
const tr=(x,y)=>({...I,x,y});
const inv=M=>{const k=M.a*M.d-M.b*M.c;return{a:M.d/k,b:-M.b/k,c:-M.c/k,d:M.a/k,x:(M.c*M.y-M.d*M.x)/k,y:(M.b*M.x-M.a*M.y)/k};};
const xf=(M,op,sx=1,sy=1)=>{const s=Math.hypot(M.a,M.b);return{position:[+M.x.toFixed(2),+M.y.toFixed(2)],
  rotation:+(Math.atan2(M.b,M.a)*180/Math.PI).toFixed(3),scale:[+(s*100*sx).toFixed(3),+((M.a*M.d-M.b*M.c)/s*100*sy).toFixed(3)],opacity:Math.round(op*100)};};

function convert(frame){
  const layers=[],assets={},names={};
  const uname=n=>{n=(n||'layer').slice(0,200);names[n]=(names[n]||0)+1;return names[n]>1?n+' '+names[n]:n;};
  function walk(n,M,op,root,clip){
    if(n.visible===false||n.mask)return; // ponytail: Figma masks dropped (none on Hurt); map to track mattes if needed
    const W=root?I:mul(M,mat(n.transform)),O=op*(n.opacity??1);
    const push=L=>{if(clip)L.trackMatte={target:clip,type:'Alpha'};layers.push(L);};
    const geo=(g,ps)=>{const items=[];for(const p of paint(ps))for(const gg of g||[])items.push({type:'group',name:'g',items:[...paths(gg.commandsBlob),{type:'fill',...color(p)}]});return items;};
    if(n.type==='TEXT'){
      const al=n.textAlignHorizontal||'LEFT';
      // Figma style props -> AE text props (shared by the base style and per-run overrides)
      const st=(s,fs)=>{const o={},ls=s.letterSpacing,lh=s.lineHeight,fp=s.fillPaints&&paint(s.fillPaints)[0];
        if(s.fontName)o.font=s.fontName.postscript||undefined;
        if(s.fontSize)o.fontSize=s.fontSize;
        if(fp)o.fillColor=color(fp).color;
        if(ls)o.tracking=Math.round(ls.units==='PERCENT'?ls.value*10:ls.value/fs*1000);
        if(lh)o.leading=lh.units==='PIXELS'?lh.value:lh.units==='RAW'?lh.value*fs:lh.value===100?0:lh.value/100*fs; // PERCENT 100 = auto
        return o;};
      const base=st(n,n.fontSize);
      let str=n.textData?.characters||'';
      if(n.textCase==='UPPER')str=str.toUpperCase();else if(n.textCase==='LOWER')str=str.toLowerCase(); // ponytail: TITLE case / underline not mapped
      // runs: consecutive chars sharing a non-zero override styleID
      const ids=n.textData?.characterStyleIDs||[],tbl={};(n.textData?.styleOverrideTable||[]).forEach(s=>tbl[s.styleID]=s);
      const runs=[];for(let i=0;i<ids.length;){let j=i;while(j<ids.length&&ids[j]===ids[i])j++;
        if(ids[i]&&tbl[ids[i]]){const o=st(tbl[ids[i]],tbl[ids[i]].fontSize||n.fontSize);if(Object.keys(o).length)runs.push({start:i,end:j,...o});}i=j;}
      // paragraph box; auto-width text gets slack so AE's metrics don't wrap it differently
      const auto=n.textAutoResize==='WIDTH_AND_HEIGHT',pad=auto?n.size.x*0.1+n.fontSize:0;
      const bx={CENTER:-pad/2,RIGHT:-pad}[al]||0;
      push({name:uname(n.name),type:'text',transform:xf(mul(W,tr(bx,0)),O),text:{
        string:str.replace(/\n/g,'\r'),...base,fillColor:base.fillColor||[0,0,0],
        boxSize:[+(n.size.x+pad).toFixed(1),+(n.size.y*1.5+n.fontSize).toFixed(1)],spaceAfter:n.paragraphSpacing||0,
        runs:runs.length?runs:undefined,justification:{CENTER:'center',RIGHT:'right',JUSTIFIED:'justifyLeft'}[al]||'left'}});
      return;}
    const shapes=[...geo(n.fillGeometry,n.fillPaints),...geo(n.strokeGeometry,n.strokePaints)];
    if(shapes.length)push({name:uname(n.name),type:'shape',transform:xf(W,O),shapes});
    const w=n.size?.x,h=n.size?.y;
    // node outline in local coords (corner radius / ellipse included); falls back to the bounding box
    const outline=()=>(n.fillGeometry||[]).flatMap(g=>paths(g.commandsBlob)).map(p=>p.path)
      .concat(n.fillGeometry?.length?[]:[{closed:true,vertices:[[0,0],[w,0],[w,h],[0,h]]}]);
    for(const p of (n.fillPaints||[]).filter(p=>p.visible!==false&&p.type==='IMAGE'&&p.image?.hash)){
      const img=image(hex(p.image.hash));if(!img)continue;
      assets[img.id]={id:img.id,name:img.id,type:'file',file:img.file};
      // L2I: node-local px -> image px
      let L2I;
      if(p.imageScaleMode==='FILL'||p.imageScaleMode==='FIT'){
        const s=(p.imageScaleMode==='FIT'?Math.min:Math.max)(w/img.w,h/img.h);
        L2I={a:1/s,b:0,c:0,d:1/s,x:-(w-img.w*s)/2/s,y:-(h-img.h*s)/2/s};
      }else{ // STRETCH/CROP: paint transform maps node UV -> image UV. ponytail: TILE treated as stretch
        const T=p.transform&&p.imageScaleMode!=='TILE'?mat(p.transform):I;
        L2I=mul({...I,a:img.w,d:img.h},mul(T,{...I,a:1/w,d:1/h}));
      }
      const ap=(M,v)=>[+(M.a*v[0]+M.c*v[1]+M.x).toFixed(2),+(M.b*v[0]+M.d*v[1]+M.y).toFixed(2)];
      const lin=(M,v)=>[+(M.a*v[0]+M.c*v[1]).toFixed(2),+(M.b*v[0]+M.d*v[1]).toFixed(2)];
      const masks=outline().map((q,i)=>({name:'crop '+(i+1),path:{closed:q.closed,vertices:q.vertices.map(v=>ap(L2I,v)),
        inTangents:q.inTangents&&q.inTangents.map(v=>lin(L2I,v)),outTangents:q.outTangents&&q.outTangents.map(v=>lin(L2I,v))}}));
      push({name:uname(n.name+' img'),type:'footage',source:img.id,transform:{...xf(mul(W,inv(L2I)),O*(p.opacity??1)),anchorPoint:[0,0]},masks});
    }
    let ch=kids[id(n.guid)];
    if(!ch&&n.type==='INSTANCE')ch=kids[id(n.symbolData?.symbolID)]; // ponytail: instance overrides ignored
    // clipping frame -> hidden alpha matte shared by all descendants. ponytail: nested clips use only the innermost frame
    if(ch&&!root&&n.frameMaskDisabled===false&&(n.type==='FRAME'||n.type==='INSTANCE'||n.type==='SYMBOL')){
      clip=uname(n.name+' matte');
      layers.push({name:clip,type:'shape',transform:xf(W,1),jsx:'layer.enabled = false;',
        shapes:[{type:'group',name:'g',items:[...outline().map(path=>({type:'path',path})),{type:'fill',color:[1,1,1],opacity:100}]}]});
    }
    for(const k of ch||[])walk(k,W,O,false,clip);
  }
  walk(frame,null,1,true);
  const bg=paint(frame.fillPaints)[0];
  return {comp:{width:Math.round(frame.size.x),height:Math.round(frame.size.y),fps:30,duration:5,
    backgroundColor:bg?toHex(bg.color):'#000000',layers:layers.reverse()},assets};
}

const proj={assets:[],compositions:[]},seen={};
for(const page of N.filter(n=>n.type==='CANVAS'&&new RegExp(pageRe,'i').test(n.name))){
  const frames=(kids[id(page.guid)]||[]).filter(n=>n.type==='FRAME'&&n.visible!==false&&n.size.x>=1000)
    .sort((a,b)=>a.transform.m12-b.transform.m12||a.transform.m02-b.transform.m02);
  frames.forEach((f,i)=>{const {comp,assets}=convert(f);
    comp.name=`${page.name.slice(0,7)} ${String(i+1).padStart(2,'0')} ${f.name}`.slice(0,31).trim();
    for(const a of Object.values(assets))if(!seen[a.id]){seen[a.id]=1;proj.assets.push(a);}
    proj.compositions.push(comp);console.log(comp.name,comp.layers.length);});
}
fs.writeFileSync(path.join(out,'project.json'),JSON.stringify(proj,null,1));
fs.mkdirSync(path.join(out,'comps'),{recursive:true});
proj.compositions.forEach((c,i)=>{const used=new Set(c.layers.map(l=>l.source).filter(Boolean));
  fs.writeFileSync(path.join(out,'comps',String(i+1).padStart(2,'0')+'.json'),JSON.stringify({assets:proj.assets.filter(a=>used.has(a.id)),compositions:[c]}));});
