// Text is assigned through DOM APIs. Labels and filter inputs never become markup.
export function element(document,tag,text=null,className=null){
  const node=document.createElement(tag);
  if(text!==null)node.textContent=String(text);
  if(className)node.className=className;
  return node;
}
export function table(document,headers,rows){
  const node=element(document,'table'),head=element(document,'thead'),tr=element(document,'tr'),body=element(document,'tbody');
  for(const title of headers){const th=element(document,'th',title);th.scope='col';tr.append(th);}
  head.append(tr);node.append(head,body);
  for(const values of rows){const row=element(document,'tr');for(const value of values)row.append(element(document,'td',value));body.append(row);}
  if(!rows.length){const row=element(document,'tr'),cell=element(document,'td','Nenhum resultado para estes filtros.');cell.colSpan=headers.length;row.append(cell);body.append(row);}
  return node;
}
