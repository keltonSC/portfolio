import {fixture,filtered,metrics,group,money,number} from './model.mjs';
import {element,table} from './dom.mjs';
const form=document.querySelector('#filters'),cards=document.querySelector('#cards'),content=document.querySelector('#content'),summary=document.querySelector('#summary');
let view='overview';
const monthLabel=value=>({'2026-07':'Julho / 2026','2026-08':'Agosto / 2026','2026-09':'Setembro / 2026'}[value]||value);
for(const name of ['month','venture','team','channel']){
  const select=form.elements.namedItem(name);
  for(const value of [...new Set(fixture.map(row=>row[name]))].sort()){
    const option=element(document,'option',name==='month'?monthLabel(value):value);option.value=value;select.append(option);
  }
}
const metricCard=(label,value,note)=>{const card=element(document,'article',null,'card');card.append(element(document,'p',label,'label'),element(document,'strong',value,'value'),element(document,'p',note,'note'));return card;};
function chart(title,rows,key){
  const section=element(document,'section',null,'panel');section.append(element(document,'h2',title));
  const max=Math.max(1,...rows.map(row=>row[key]));
  for(const row of rows){
    const item=element(document,'div',null,'bar-row'),label=element(document,'span',row.label),progress=element(document,'progress');
    progress.max=max;progress.value=row[key];progress.setAttribute('aria-label',`${row.label}: ${number(row[key])}`);
    item.append(label,progress,element(document,'b',number(row[key])));section.append(item);
  }
  if(!rows.length)section.append(element(document,'p','Nenhum resultado para estes filtros.'));
  return section;
}
function render(){
  const filters=Object.fromEntries(['month','venture','team','channel','query'].map(key=>[key,form.elements.namedItem(key).value]));
  const rows=filtered(fixture,filters),total=metrics(rows);
  const active=Object.values(filters).filter(Boolean).length;
  summary.textContent=`${rows.length} de ${fixture.length} registros sintéticos · ${active?active+' filtros ativos':'todos os dados'}`;
  cards.replaceChildren(
    metricCard('Investimento',money(total.spend),'Soma do investimento fictício'),
    metricCard('Leads',number(total.leads),'Cadastros agregados, sem contatos'),
    metricCard('Custo por lead',total.cpl===null?'—':money(total.cpl),'Investimento ÷ leads'),
    metricCard('Conversão',total.conversion===null?'—':number(total.conversion)+'%','Vendas ÷ leads'));
  content.replaceChildren();
  if(view==='overview'){
    const grid=element(document,'div',null,'grid');
    grid.append(chart('Leads por produto',group(rows,'venture'),'leads'),chart('Leads por canal',group(rows,'channel'),'leads'));
    const panel=element(document,'section',null,'panel');panel.append(element(document,'h2','Funil comercial'),table(document,['Etapa','Quantidade','Definição'],[
      ['Leads',number(total.leads),'Cadastros fictícios'],['Visitas',number(total.visits),'Visitas fictícias'],['Vendas',number(total.sales),'Vendas fictícias']]));
    content.append(grid,panel,element(document,'p','A relação entre etapas é ilustrativa. Não representa atribuição causal, ROI real ou performance comprovada.', 'caption'));
  }else if(view==='campaigns'){
    const panel=element(document,'section',null,'panel');panel.append(element(document,'h2','Campanhas'),table(document,['Campanha','Mês','Investimento','Leads','CPL','Vendas'],rows.map(row=>[
      row.campaign,monthLabel(row.month),money(row.spend),number(row.leads),row.leads?money(row.spend/row.leads):'—',number(row.sales)])));content.append(panel);
  }else if(view==='ventures'){
    const panel=element(document,'section',null,'panel');panel.append(element(document,'h2','Resultado por produto'),table(document,['Produto','Investimento','Leads','Visitas','Vendas','Receita fictícia'],group(rows,'venture').map(row=>[
      row.label,money(row.spend),number(row.leads),number(row.visits),number(row.sales),money(row.revenue)])));content.append(panel);
  }else{
    const panel=element(document,'section',null,'panel');panel.append(element(document,'h2','Como ler esta demonstração'));
    for(const paragraph of ['Os 12 registros foram escritos para esta demonstração. Todos os nomes e números são fictícios.',
      'Os filtros recalculam as métricas a partir dos registros da amostra. Não há importação de arquivos, telemetria ou chamadas de rede.',
      'Um sistema operacional requer identidade individual, escopo autorizado no servidor, RLS, ingestão validada e atualização comprovada. Esta amostra não comprova proteção nem resultados de uma implantação real.',
      'CPL e conversão são razões de somas, não médias das taxas de cada campanha. Sem denominador, a métrica aparece como “—”.'])panel.append(element(document,'p',paragraph));
    content.append(panel);
  }
}
form.addEventListener('submit',event=>event.preventDefault());
form.addEventListener('input',render);
form.addEventListener('reset',()=>queueMicrotask(render));
document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>{
  view=button.dataset.view;document.querySelectorAll('[data-view]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));render();
}));
render();
