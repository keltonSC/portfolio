// Every record below is invented for this public demonstration.
export const fixture=Object.freeze([
  {id:'c01',campaign:'Busca · Produto Aurora',venture:'Produto Aurora',team:'Equipe A',channel:'Busca',month:'2026-07',spend:1800,leads:90,visits:18,sales:3,revenue:210000},
  {id:'c02',campaign:'Social · Produto Aurora',venture:'Produto Aurora',team:'Equipe A',channel:'Social',month:'2026-07',spend:2400,leads:160,visits:20,sales:2,revenue:140000},
  {id:'c03',campaign:'Busca · Produto Horizonte',venture:'Produto Horizonte',team:'Equipe B',channel:'Busca',month:'2026-07',spend:2100,leads:70,visits:14,sales:2,revenue:180000},
  {id:'c04',campaign:'Social · Produto Horizonte',venture:'Produto Horizonte',team:'Equipe B',channel:'Social',month:'2026-07',spend:1600,leads:100,visits:10,sales:1,revenue:90000},
  {id:'c05',campaign:'Busca · Produto Aurora',venture:'Produto Aurora',team:'Equipe A',channel:'Busca',month:'2026-08',spend:2200,leads:110,visits:22,sales:4,revenue:280000},
  {id:'c06',campaign:'Social · Produto Aurora',venture:'Produto Aurora',team:'Equipe A',channel:'Social',month:'2026-08',spend:2600,leads:180,visits:27,sales:3,revenue:210000},
  {id:'c07',campaign:'Busca · Produto Horizonte',venture:'Produto Horizonte',team:'Equipe B',channel:'Busca',month:'2026-08',spend:2400,leads:100,visits:20,sales:3,revenue:270000},
  {id:'c08',campaign:'Social · Produto Horizonte',venture:'Produto Horizonte',team:'Equipe B',channel:'Social',month:'2026-08',spend:1800,leads:120,visits:18,sales:2,revenue:180000},
  {id:'c09',campaign:'Busca · Produto Aurora',venture:'Produto Aurora',team:'Equipe A',channel:'Busca',month:'2026-09',spend:2500,leads:125,visits:25,sales:5,revenue:350000},
  {id:'c10',campaign:'Social · Produto Aurora',venture:'Produto Aurora',team:'Equipe A',channel:'Social',month:'2026-09',spend:2800,leads:200,visits:30,sales:4,revenue:280000},
  {id:'c11',campaign:'Busca · Produto Horizonte',venture:'Produto Horizonte',team:'Equipe B',channel:'Busca',month:'2026-09',spend:2700,leads:135,visits:27,sales:4,revenue:360000},
  {id:'c12',campaign:'Social · Produto Horizonte',venture:'Produto Horizonte',team:'Equipe B',channel:'Social',month:'2026-09',spend:2100,leads:150,visits:24,sales:3,revenue:270000}
].map(Object.freeze));

export const money=value=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}).format(value);
export const number=value=>new Intl.NumberFormat('pt-BR',{maximumFractionDigits:1}).format(value);
export function filtered(rows,filters={}){
  const query=String(filters.query||'').trim().toLocaleLowerCase('pt-BR');
  return rows.filter(row=>['month','venture','team','channel'].every(key=>!filters[key]||row[key]===filters[key])&&
    (!query||[row.campaign,row.venture,row.team,row.channel].some(value=>String(value).toLocaleLowerCase('pt-BR').includes(query))));
}
export function metrics(rows){
  const total=rows.reduce((acc,row)=>{for(const key of ['spend','leads','visits','sales','revenue'])acc[key]+=Number(row[key])||0;return acc;},
    {spend:0,leads:0,visits:0,sales:0,revenue:0});
  return {...total,cpl:total.leads?total.spend/total.leads:null,conversion:total.leads?100*total.sales/total.leads:null,visitRate:total.leads?100*total.visits/total.leads:null};
}
export function group(rows,key){
  const groups=new Map();
  for(const row of rows){const label=String(row[key]??'Sem classificação');if(!groups.has(label))groups.set(label,[]);groups.get(label).push(row);}
  return [...groups].map(([label,values])=>({label,...metrics(values)})).sort((a,b)=>b.leads-a.leads||a.label.localeCompare(b.label));
}
