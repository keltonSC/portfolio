import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {Pipeline, ROOT, STAGES, digest} from '../pipeline.mjs';
const original=JSON.parse(fs.readFileSync(path.join(ROOT,'examples/imovel-demo.json'),'utf8'));
const clone=x=>structuredClone(x);
function harness(t){const dir=fs.mkdtempSync(path.join(os.tmpdir(),'imobiliarios-test-'));t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));const p=new Pipeline(dir);p.init(clone(original));return p;}
function response(p,stage){const s=p.load(original.id); const payload={
  catalogador:{assets:clone(original.assets),facts:clone(original.facts),missing:['Preço não fornecido; não será divulgado.']},
  roteirista:{scenes:[{id:'s1',duration_seconds:10,asset_ids:['a-sala'],fact_ids:['f-area'],text:'82 m² privativos',purpose:'Texto integrado; fixture.'},{id:'s2',duration_seconds:10,asset_ids:['a-varanda'],fact_ids:['f-varanda'],text:'Varanda integrada',purpose:'Demonstração e CTA'}],total_duration_seconds:20,cta:'Agende uma visita'},
  diretor:{shots:[{scene_id:'s1',technique:'tracked_text',asset_ids:['a-sala'],instructions:'Planejar tracking, sujeito a inspeção.',requires_tools:['After Effects'],is_simulation:false},{scene_id:'s2',technique:'real_edit',asset_ids:['a-varanda'],instructions:'Planejar montagem.',requires_tools:['Premiere'],is_simulation:false}]},
  produtor:{jobs:[{scene_id:'s1',technique:'tracked_text',execution_status:'not_executed',required_tools:['After Effects'],instructions:'Preparar composição.',output_path:null},{scene_id:'s2',technique:'real_edit',execution_status:'not_executed',required_tools:['Premiere'],instructions:'Preparar montagem.',output_path:null}],executed:false},
  editor:{timeline:[{scene_id:'s1',start_seconds:0,duration_seconds:10,source_asset_ids:['a-sala'],overlay_text:'82 m² privativos'},{scene_id:'s2',start_seconds:10,duration_seconds:10,source_asset_ids:['a-varanda'],overlay_text:'Varanda integrada'}],export:{width:1080,height:1920,fps:30},rendered:false,output_path:null},
  revisor:{decision:'plan_approved',checks:['facts','references','timing','visual','audio'].map(name=>({name,result:['visual','audio'].includes(name)?'not_tested':'pass',detail:'Validação de fixture, sem render.'})),video_approved:false}
}[stage];return {job_id:original.id,input_digest:digest(s),stage,mode:'planning',status:'ready',payload,issues:[],evidence:['examples/imovel-demo.json (sintético)']};}
function advance(p,until){for(const stage of STAGES){if(stage===until)return; p.accept(original.id,response(p,stage));}}
test('seis etapas terminam em plano aprovado, nunca vídeo aprovado',t=>{const p=harness(t);advance(p,null);assert.equal(p.status(original.id).status,'plan_approved');assert.equal(p.status(original.id).video_produced,false);assert.equal(p.load(original.id).events.length,7);});
test('reinicializar trabalho não sobrescreve estado',t=>{const p=harness(t);assert.throws(()=>p.init(original),/EEXIST/);assert.equal(p.load(original.id).events.length,1);});
test('IDs impedem traversal',t=>{const p=harness(t);assert.throws(()=>p.status('../fora'),/ID inválido/);});
test('fixture não pode se passar por trabalho real',t=>{const p=harness(t);assert.throws(()=>p.init({...original,id:'real',synthetic:false}),/Fixture/);});
test('fatos alterados são rejeitados sem gravar etapa',t=>{const p=harness(t),o=response(p,'catalogador');o.payload.facts[0].value='120 m²';assert.throws(()=>p.accept(original.id,o),/Fato alterado/);assert.equal(p.status(original.id).next_stage,'catalogador');});
test('inspeção visual não pode ser inventada',t=>{const p=harness(t),o=response(p,'catalogador');o.payload.assets[0].inspection='visual';assert.throws(()=>p.accept(original.id,o),/inspeção/);});
test('resposta de outro trabalho é rejeitada',t=>{const p=harness(t),o=response(p,'catalogador');o.job_id='outro';assert.throws(()=>p.accept(original.id,o),/outro trabalho/);});
test('ordem de etapas é obrigatória',t=>{const p=harness(t),o=response(p,'catalogador');o.stage='editor';assert.throws(()=>p.accept(original.id,o),/esperado/);});
test('referências inexistentes não passam',t=>{const p=harness(t);advance(p,'roteirista');const o=response(p,'roteirista');o.payload.scenes[0].fact_ids=['f-inventado'];assert.throws(()=>p.accept(original.id,o),/referência desconhecida/);});
test('roteiro com duração incoerente não passa',t=>{const p=harness(t);advance(p,'roteirista');const o=response(p,'roteirista');o.payload.scenes[0].duration_seconds=11;assert.throws(()=>p.accept(original.id,o),/Soma/);});
test('direção não pode trocar mídia entre cenas',t=>{const p=harness(t);advance(p,'diretor');const o=response(p,'diretor');o.payload.shots[0].asset_ids=['a-varanda'];assert.throws(()=>p.accept(original.id,o),/fora da cena/);});
test('IA precisa declarar simulação',t=>{const p=harness(t);advance(p,'diretor');const o=response(p,'diretor');o.payload.shots[0].technique='ai_reference';assert.throws(()=>p.accept(original.id,o),/simulação/);});
test('produtor não pode alegar execução nesta fase',t=>{const p=harness(t);advance(p,'produtor');const o=response(p,'produtor');o.payload.executed=true;assert.throws(()=>p.accept(original.id,o),/esperado false/);});
test('needs_input não permite esconder execução falsa em payload',t=>{const p=harness(t);advance(p,'produtor');const o=response(p,'produtor');o.status='needs_input';o.issues=['falta acesso'];o.payload.executed=true;assert.throws(()=>p.accept(original.id,o),/esperado false/);});
test('timeline não pode conter lacuna',t=>{const p=harness(t);advance(p,'editor');const o=response(p,'editor');o.payload.timeline[1].start_seconds=12;assert.throws(()=>p.accept(original.id,o),/Lacuna/);});
test('editor não pode mudar texto aprovado',t=>{const p=harness(t);advance(p,'editor');const o=response(p,'editor');o.payload.timeline[0].overlay_text='120 m²';assert.throws(()=>p.accept(original.id,o),/Texto/);});
test('revisor não pode aprovar imagem sem render',t=>{const p=harness(t);advance(p,'revisor');const o=response(p,'revisor');o.payload.checks.find(c=>c.name==='visual').result='pass';assert.throws(()=>p.accept(original.id,o),/not_tested/);});
test('revisor não pode aprovar vídeo',t=>{const p=harness(t);advance(p,'revisor');const o=response(p,'revisor');o.payload.video_approved=true;assert.throws(()=>p.accept(original.id,o),/esperado false/);});
test('falha factual impede aprovação do plano',t=>{const p=harness(t);advance(p,'revisor');const o=response(p,'revisor');o.payload.checks[0].result='fail';assert.throws(()=>p.accept(original.id,o),/Plano não pode/);});
test('pendências bloqueiam próximo agente e exigem revisão explícita',t=>{const p=harness(t),o=response(p,'catalogador');o.status='needs_input';o.payload={};o.issues=['Ficha ausente'];p.accept(original.id,o);assert.equal(p.status(original.id).status,'needs_input');assert.throws(()=>p.prompt(original.id),/pendências/);p.revise(original.id,'catalogador');p.accept(original.id,response(p,'catalogador'));assert.equal(p.status(original.id).next_stage,'roteirista');});
test('revisão invalida dependentes e resposta antiga',t=>{const p=harness(t);advance(p,'editor');const old=response(p,'editor');p.revise(original.id,'roteirista');assert.deepEqual(p.status(original.id).accepted_stages,['catalogador']);advanceFrom(p,'roteirista','editor');assert.throws(()=>p.accept(original.id,old),/desatualizado/);});
function advanceFrom(p,start,until){for(const stage of STAGES.slice(STAGES.indexOf(start))){if(stage===until)return;p.accept(original.id,response(p,stage));}}
test('limite de entregas evita ciclo e preserva última saída',t=>{const p=harness(t);for(let i=0;i<3;i++){p.accept(original.id,response(p,'catalogador'));if(i<2)p.revise(original.id,'catalogador');}assert.throws(()=>p.revise(original.id,'catalogador'),/Limite/);assert.equal(p.status(original.id).next_stage,'roteirista');});
test('número no texto exige fato referenciado',t=>{const p=harness(t);advance(p,'roteirista');const o=response(p,'roteirista');o.payload.scenes[0].text='Cobertura de 999 m² por R$ 1';o.payload.scenes[0].fact_ids=[];assert.throws(()=>p.accept(original.id,o),/Número/);});
test('parecer de correção não pode encerrar como ready',t=>{const p=harness(t);advance(p,'revisor');const o=response(p,'revisor');o.payload.decision='changes_requested';assert.throws(()=>p.accept(original.id,o),/needs_input/);});
test('prompt expõe dados como não confiáveis e identifica contexto',t=>{const p=harness(t);const prompt=p.prompt(original.id);assert.match(prompt,/CONTEXTO NÃO CONFIÁVEL/);assert.ok(prompt.includes(digest(p.load(original.id))));assert.match(prompt,/catalogador/);});
