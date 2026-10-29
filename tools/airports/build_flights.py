import json,glob,collections,sys,re
files=sorted(glob.glob('/root/.claude/projects/-home-claude/90517416-bd5f-5bf0-bbb8-ab075d39d6f7/tool-results/mcp-ForeFlight_Mobile-list_logbook_entries-*.txt'))
SIM={'REDBIRD FMX ABOVE ALL',"ROMAN'S"}
rows=[];A={}
for f in files:
    d=json.load(open(f))
    for k,v in d['airports'].items(): A[k]=[v.get('name'),v.get('city'),v.get('state'),v.get('country'),v.get('latitude'),v.get('longitude')]
    for e in d['entries']:
        blob=' '.join([e.get('remarks') or '',e['aircraft'].get('tail_number') or '',e['aircraft'].get('make_model') or '',str(e.get('tags',''))])
        if (e['aircraft'].get('tail_number') in SIM or 'route' not in e or not e.get('total_hours')
            or e.get('status')!='approved' or re.search(r'x.?plane|track ?log',blob,re.I)): continue
        r=e['route']; rows.append([e['date'],r.get('from',''),r.get('to',''),r.get('elements','')])
p=json.load(open('page11.json')); rows+=p['entries']; A.update({k:v for k,v in p['airports'].items() if k not in A})
print('flights',len(rows))
vis=collections.defaultdict(lambda:{'first':'9999','last':'0','n':0,'endpt':False,'route':False,'raw':collections.Counter()})
for date,f,t,el in rows:
    toks=[('e',f),('e',t)]+[('r',x) for x in el.replace(',',' ').split()]
    seen=set()
    for kind,x in toks:
        x=x.strip().upper()
        if not x: continue
        v=vis[x]; v['raw'][kind]+=1
        if kind=='e': v['endpt']=True
        else: v['route']=True
        if x in seen: continue
        seen.add(x); v['n']+=1; v['first']=min(v['first'],date); v['last']=max(v['last'],date)
print('idents',len(vis))
unk=sorted(k for k in vis if k not in A)
print('not in connector airport lookup:',len(unk))
for k in unk: print(' ',k,dict(vis[k]['raw']),vis[k]['first'][:4],'endpt' if vis[k]['endpt'] else 'route-only')
json.dump({'rows':rows,'A':A},open('combined.json','w'))
json.dump({k:{kk:(vv if kk!='raw' else dict(vv)) for kk,vv in v.items()} for k,v in vis.items()},open('vis.json','w'))
