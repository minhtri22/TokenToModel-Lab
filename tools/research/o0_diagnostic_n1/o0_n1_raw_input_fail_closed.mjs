/** Fail-closed duplicate-key and exact-field JSON validator; no labels accepted. */
export const validateModelJsonRaw = function validateModelJsonRaw(raw){
 const fail=m=>{throw Error("O0_INPUT_REJECT:"+m)};
 if(typeof raw!=="string"||raw.length<10||raw.length>500000)fail("INPUT_SIZE");
 const frames=[];let i=0;
 while(i<raw.length){
  const c=raw[i];
  if(c==="{"||c==="["){frames.push(c==="{"?{kind:"obj",keys:new Set()}:{kind:"arr"});i++;continue}
  if(c==="}"||c==="]"){if(!frames.length)fail("UNBALANCED");frames.pop();i++;continue}
  if(c==='"'){
   const start=i++;let escaped=false,closed=false;
   while(i<raw.length){
    const d=raw[i++];
    if(escaped){escaped=false;continue}
    if(d==="\\"){escaped=true;continue}
    if(d==='"'){closed=true;break}
   }
   if(!closed)fail("UNTERMINATED_STRING");
   const tok=JSON.parse(raw.slice(start,i));let j=i;while(j<raw.length&&/\s/.test(raw[j]))j++;
   if(raw[j]===":"&&frames.length&&frames.at(-1).kind==="obj"){
    const keys=frames.at(-1).keys;if(keys.has(tok))fail("DUPLICATE_JSON_KEY");keys.add(tok)
   }
   continue
  }
  i++;
 }
 if(frames.length)fail("UNTERMINATED_STRUCTURE");
 let x;try{x=JSON.parse(raw)}catch{fail("INVALID_JSON")}
 if(!x||Object.getPrototypeOf(x)!==Object.prototype||Object.keys(x).sort().join(",")!=="records,schema")fail("ROOT_ALLOWLIST");
 if(x.schema!=="ttm.o0.n1.model.input.v1"||!Array.isArray(x.records)||x.records.length<1||x.records.length>1024)fail("BAD_SCHEMA_OR_RECORD_COUNT");
 for(const row of x.records){
  if(!row||Array.isArray(row)||Object.getPrototypeOf(row)!==Object.prototype||Object.keys(row).sort().join(",")!=="question,story")fail("RECORD_FIELD_ALLOWLIST");
  if(typeof row.story!=="string"||typeof row.question!=="string"||row.story.length<30||row.story.length>1200||row.question.length>150||row.question.length<8)fail("RECORD_TEXT_LIMIT");
  if(row.story.includes("\u0000")||row.question.includes("\u0000"))fail("NUL_IN_TEXT");
 }
 return {rows:x.records.length,strict_root:true,strict_record:true,duplicate_keys_rejected:true};
};
