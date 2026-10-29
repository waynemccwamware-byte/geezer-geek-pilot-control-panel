import json,csv,re,collections
D=json.load(open('combined.json')); rows,A=D['rows'],D['A']
# connector get_airport results for route tokens missing from the list lookup (29-Oct-2026)
A.update({
 'XSBY':['Scorpion Bay Airport','San Juanico','Baja California Sur','Mexico',26.258347,-112.498272],
 'XFTE':['El Fuerte','','Sinaloa','Mexico',26.398199,-108.612000],
 'MX0016':['Bahía Tortugas Airfield','Bahía Tortugas','Baja California Sur','Mexico',27.706336,-114.912922],
 'MX0375':['Guachochi','Guachochi','Chihuahua','Mexico',26.842652,-107.061353]})
ALIAS={'ABREOJOS':'MX-AJS','LAGUNA':'MX-0007','XSQA':'MX-1384'}   # per Wayne 29-Oct-2026: Punta Abreojos, Laguna San Ignacio, San Pedro de la Cueva
RENAME={'TORTUGAS':'MX0016','MMXL':'MMML'}   # per Wayne 29-Oct-2026: Bahia Tortugas; MMXL was a typo for MMML
NAME={'LAGUNA':'Laguna San Ignacio Airstrip'}   # Punta Abreojos (OurAirports); endpoint on 08-Oct-2015 and 11-Oct-2015
CC={'US':'United States','MX':'Mexico','CA':'Canada','PA':'Panama','NI':'Nicaragua','BS':'Bahamas','TC':'Turks and Caicos','DO':'Dominican Republic'}
OA={};OAalt=collections.defaultdict(list)
for r in csv.DictReader(open('../oa/airports.csv',encoding='utf-8')):
    if r['type'] in ('heliport','balloonport'): continue
    rec=[r['name'],r['municipality'],r['iso_region'].split('-',1)[-1],CC.get(r['iso_country'],r['iso_country']),float(r['latitude_deg']),float(r['longitude_deg'])]
    OA[r['ident']]=rec
    for k in ('icao_code','gps_code','local_code'):
        if r[k]: OAalt[r[k]].append((r['iso_country'],rec))
def oa(t):
    if t in ALIAS: return OA[ALIAS[t]]
    if re.fullmatch(r'[A-Z]{4}',t) and t[0] not in 'KM': return None   # e.g. PASO is a fix, not Seldovia AK
    if t in OA: return OA[t]
    c=OAalt.get(t,[]); us=[x for k,x in c if k in('US','MX','CA')]
    return (us or [x for k,x in c] or [None])[0]
def toks(s):
    s=re.sub(r'\([^)]*\)','',s.upper())
    return [x for x in re.split(r'[\s,\-\.]+',s) if x]
drops=collections.defaultdict(set); vis={}
def resolve(t,endpt):
    if '/' in t: return None,'radial/DME'
    if re.fullmatch(r'[VJTQ]\d+',t): return None,'airway'
    if t in A: return A[t],'ff'
    if not endpt and re.fullmatch(r'[A-Z]{3}',t): return None,'navaid'
    if not endpt and re.fullmatch(r'[A-Z]{5}',t) and not t.startswith(('K','M')): return None,'fix'
    r=oa(t); return (r,'oa') if r else (None,'unresolved')
for date,f,to,el in rows:
    seen=set()
    for t,e in [(f,1),(to,1)]+[(x,0) for x in toks(el)]:
        t=t.strip().upper()
        if not t: continue
        t=RENAME.get(t,t)
        rec,why=resolve(t,e)
        if rec is not None and t in NAME: rec=[NAME[t]]+list(rec[1:])
        if rec is None: drops[why].add(t); continue
        key=t
        if key in seen: continue
        seen.add(key)
        v=vis.setdefault(key,{'rec':rec,'yr':int(date[:4]),'n':0,'end':0,'src':why})
        v['yr']=min(v['yr'],int(date[:4])); v['n']+=1; v['end']+=e

US={'AR':'Arkansas','AZ':'Arizona','CA':'California','CO':'Colorado','ID':'Idaho','KS':'Kansas','MO':'Missouri','NC':'North Carolina','NE':'Nebraska','NM':'New Mexico','NV':'Nevada','OK':'Oklahoma','OR':'Oregon','TX':'Texas','UT':'Utah','WA':'Washington','WY':'Wyoming','AK':'Alaska','MT':'Montana','NY':'New York','FL':'Florida'}
MXR={'BCN':'Baja California','BCS':'Baja California Sur','CAM':'Campeche','CHH':'Chihuahua','COA':'Coahuila','GRO':'Guerrero','JAL':'Jalisco','NLE':'Nuevo León','OAX':'Oaxaca','ROO':'Quintana Roo','SIN':'Sinaloa','SON':'Sonora','TAB':'Tabasco','VER':'Veracruz','YUC':'Yucatán'}
OTHER={('Bahamas','EX'):'Exuma',('Nicaragua','RI'):'Rivas',('Panama','1'):'Bocas del Toro',('Panama','8'):'Panamá',('Dominican Republic','18'):'Puerto Plata',('Turks and Caicos','SC'):''}
def region(ctry,rg):
    if ctry=='United States' and rg in US: return US[rg]
    if ctry=='Mexico' and rg in MXR: return MXR[rg]
    return OTHER.get((ctry,rg),rg)
out=[[k,v['rec'][0],v['rec'][1] or '',region(v['rec'][3] or '',v['rec'][2] or ''),v['rec'][3] or '',round(v['rec'][4],5),round(v['rec'][5],5),v['yr'],v['n'],0 if v['end'] else 1] for k,v in sorted(vis.items(),key=lambda x:(x[1]['yr'],x[0]))]
json.dump(out,open('wayne_airports.json','w'),ensure_ascii=False,separators=(',',':'))
print('airports',len(out),'| by year',dict(sorted(collections.Counter(o[7] for o in out).items())))
print('countries',collections.Counter(o[4] for o in out))
print('route-only',sum(o[9] for o in out))
print('lat range',min(o[5] for o in out),max(o[5] for o in out),'lon',min(o[6] for o in out),max(o[6] for o in out))
for k in ('unresolved',): print(k,sorted(drops[k]))
print('missing name/coords',[o[0] for o in out if not o[1] or o[5] is None])
