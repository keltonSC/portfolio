import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fixture,filtered,metrics,group} from '../model.mjs';
import {element,table} from '../dom.mjs';

test('weighted CPL and conversion derive from summed data, with empty denominators explicit',()=>{
  const september=filtered(fixture,{month:'2026-09'}),total=metrics(september);
  assert.deepEqual([total.spend,total.leads,total.visits,total.sales,total.revenue],[10100,610,106,16,1260000]);
  assert.equal(total.cpl,10100/610);assert.equal(total.conversion,100*16/610);
  assert.equal(metrics([]).cpl,null);assert.equal(metrics([]).conversion,null);
});
test('combined filters and reset inputs preserve totals across dimensions',()=>{
  assert.equal(filtered(fixture,{month:'2026-09',venture:'Produto Aurora',team:'Equipe A',channel:'Busca'}).length,1);
  assert.equal(filtered(fixture,{query:'horizonte',channel:'Social'}).length,3);
  assert.equal(filtered(fixture,{team:'unavailable'}).length,0);
  assert.equal(group(fixture,'venture').reduce((sum,row)=>sum+row.leads,0),metrics(fixture).leads);
});
function documentFixture(){
  const nodes=[];return {nodes,createElement(tag){const node={tag,children:[],append(...items){this.children.push(...items);}};
    Object.defineProperty(node,'innerHTML',{set(){throw Error('HTML sink forbidden');}});nodes.push(node);return node;}};
}
test('hostile campaign, venture and search remain literal text; no HTML sink is used',()=>{
  const hostile='\"><img src=x onerror=alert(1)><script>bad()</script>',document=documentFixture();
  const node=element(document,'option',hostile);assert.equal(node.textContent,hostile);
  const output=table(document,['Campanha','Produto'],[[hostile,hostile]]);
  assert.equal(output.children[1].children[0].children[0].textContent,hostile);
  assert.equal(filtered([{campaign:hostile,venture:hostile,team:'A',channel:'B'}],{query:hostile}).length,1);
  assert.equal(document.nodes.filter(node=>node.tag==='img'||node.tag==='script').length,0);
});
test('public HTML and app prohibit network clients and inline executable markup',async()=>{
  const html=await readFile(new URL('../index.html',import.meta.url),'utf8');
  assert.ok(!/\son[a-z]+\s*=/i.test(html));assert.ok(!/<script(?![^>]*\bsrc=)[^>]*>/i.test(html));
  assert.match(html,/script-src 'self'/);assert.match(html,/connect-src 'none'/);assert.ok(!html.includes('unsafe-inline'));
  for(const file of ['app.mjs','dom.mjs','model.mjs']){
    const source=await readFile(new URL('../'+file,import.meta.url),'utf8');
    assert.ok(!/innerHTML|insertAdjacentHTML|fetch\(|XMLHttpRequest|localStorage|sessionStorage/.test(source));
    assert.ok(!/https?:\/\/|supabase\.co|x-dash-key/.test(source));
  }
});
