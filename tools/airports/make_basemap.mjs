import fs from 'fs';
import {feature} from 'topojson-client';
import {geoBounds} from 'd3-geo';
const w=JSON.parse(fs.readFileSync('node_modules/world-atlas/countries-50m.json'));
const u=JSON.parse(fs.readFileSync('node_modules/us-atlas/states-10m.json'));
const r=x=>Math.round(x*100)/100;
function round(g){const f=c=>typeof c[0]==='number'?[r(c[0]),r(c[1])]:c.map(f);
  const dedupe=ring=>ring.filter((p,i)=>i===0||p[0]!==ring[i-1][0]||p[1]!==ring[i-1][1]);
  let co=f(g.coordinates);
  if(g.type==='Polygon') co=co.map(dedupe).filter(x=>x.length>=4);
  else co=co.map(p=>p.map(dedupe).filter(x=>x.length>=4)).filter(p=>p.length);
  return {type:g.type,coordinates:co};}
const skip=new Set(['Russia','Greenland']);
const ctry=feature(w,w.objects.countries).features.filter(f=>{
  if(skip.has(f.properties.name))return false;
  const [[x0,y0],[x1,y1]]=geoBounds(f);return x1>-172&&x0<-55&&y1>0&&y0<75&&x0<x1;
}).map(f=>({n:f.properties.name,g:round(f.geometry)}));
const states=feature(u,u.objects.states).features.map(f=>({n:f.properties.name,g:round(f.geometry)}));
fs.writeFileSync('geo.json',JSON.stringify({ctry,states}));
console.log(ctry.length,'countries:',ctry.map(c=>c.n).join(', '));
console.log(states.length,'states; bytes',fs.statSync('geo.json').size);
