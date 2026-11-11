/** Independent public visible-text state checker. */
export const checkCorpus = function checkCorpus(a){
 const need=(x,m)=>{if(!x)throw Error("STRICT_QA:"+m)};
 function interpret(story,question){
  let holder={},goal={},label={},marker={},guide={},helper={},seal={},badge={};
  for(const line of story.split("\n")){
   let m;
   if((m=/^The (?:spare )?label (\w+) designates (\w+)\.$/.exec(line))){label[m[1]]=m[2];continue}
   if((m=/^The marker (\w+) designates label (\w+)\.$/.exec(line))){marker[m[1]]=m[2];continue}
   if((m=/^The (\w+) was carried by (\w+)\.$/.exec(line))){need(holder[m[1]]===undefined,"DOUBLE_OWNER");holder[m[1]]=m[2];continue}
   if((m=/^(\w+) handed the (\w+) to (label|marker) (\w+)\.$/.exec(line))){
    need(holder[m[2]]===m[1],"BAD_HANDOFF");const v=m[3]==="marker"?label[marker[m[4]]]:label[m[4]];need(v,"NO_ALIAS");holder[m[2]]=v;continue}
   if((m=/^The (\w+) remained with (\w+)\.$/.exec(line))){need(holder[m[1]]===m[2],"FALSE_REMAIN");continue}
   if((m=/^The duty (\w+) began with (\w+)\.$/.exec(line))){need(goal[m[1]]===undefined,"DOUBLE_GOAL");goal[m[1]]=m[2];continue}
   if((m=/^(\w+) delegated the duty (\w+) to (\w+)\.$/.exec(line))){need(goal[m[2]]===m[1],"FALSE_DELEGATE");goal[m[2]]=m[3];continue}
   if((m=/^(\w+) cancelled the duty (\w+)\.$/.exec(line))){need(goal[m[2]]===m[1],"FALSE_CANCEL");goal[m[2]]="NONE";continue}
   if(/^The duty \w+ was acknowledged by \w+\.$/.test(line))continue;
   if((m=/^The duty (\w+) stayed with (\w+)\.$/.exec(line))){need(goal[m[1]]===m[2],"FALSE_GOAL_STAY");continue}
   if((m=/^In the (\w+), the guide is (\w+)\.$/.exec(line))){guide[m[1]]=m[2];continue}
   if((m=/^In the (\w+), the helper means the guide\.$/.exec(line))){helper[m[1]]=true;continue}
   if((m=/^The (\w+) was initially with (\w+)\.$/.exec(line))){need(holder[m[1]]===undefined,"DOUBLE_INIT");holder[m[1]]=m[2];continue}
   if((m=/^(\w+) passed the (\w+) to the (guide|helper) in the (\w+)\.$/.exec(line))){
    need(holder[m[2]]===m[1]&&guide[m[4]],"ROLE_INVALID");if(m[3]==="helper")need(helper[m[4]],"HELPER_UNDEFINED");holder[m[2]]=guide[m[4]];continue}
   if((m=/^The (\w+) stayed with the guide in the (\w+)\.$/.exec(line))){need(holder[m[1]]===guide[m[2]],"FALSE_GUIDE_STAY");continue}
   if((m=/^The seal (\w+) belongs to (\w+)\.$/.exec(line))){seal[m[1]]=m[2];continue}
   if((m=/^The badge (\w+) identifies seal (\w+)\.$/.exec(line))){badge[m[1]]=m[2];continue}
   if(/^The badge \w+ belongs to \w+\.$/.test(line))continue;
   if((m=/^The (\w+) was in care of (\w+)\.$/.exec(line))){need(holder[m[1]]===undefined,"DOUBLE_CARE");holder[m[1]]=m[2];continue}
   if((m=/^(\w+) filed the (\w+) for the owner of (seal|badge) (\w+)\.$/.exec(line))){
    need(holder[m[2]]===m[1],"FALSE_FILE");const key=m[3]==="seal"?m[4]:badge[m[4]];need(seal[key],"NO_SEAL");holder[m[2]]=seal[key];continue}
   if((m=/^The (\w+) remained filed under (\w+)\.$/.exec(line))){need(holder[m[1]]===m[2],"FALSE_FILE_STAY");continue}
   if(/^At sunset, \w+ checked a ledger\.$/.test(line)||/^During the morning, \w+ visited the \w+\.$/.test(line))continue;
   throw Error("STRICT_QA:INVALID_EVENT:"+line);
  }
  let q=/^Who (?:has|carries) the (\w+) now\?$/.exec(question)||/^Who is responsible for the (\w+) now\?$/.exec(question);
  if(q){need(holder[q[1]]!==undefined,"UNBOUND_ITEM");return holder[q[1]]}
  q=/^Who holds the duty (\w+) now\?$/.exec(question);need(q&&goal[q[1]]!==undefined,"UNBOUND_DUTY");return goal[q[1]];
 }
 const report={schema:"ttm.o0.n1.independent_corpus_qa.v1",status:"PENDING",correct:0,groups:0,by_split:{},quartets_verified:0,mutants_rejected:0,coarse_struct_signature_overlap:0,public_oracle_only:true};
 const seen=new Set(),groups=new Map(),sig={TRAIN:new Set(),DEV_STRUCT:new Set()};
 for(const [split,obj] of Object.entries(a)){
  const oracle=obj.oracle,mod=obj.model,stats={rows:0,families:{N1:0,N2:0,N3:0,N4:0}};
  need(Object.keys(mod).sort().join(",")==="records,schema"&&mod.schema==="ttm.o0.n1.model.input.v1","ROOT_ALLOWLIST");
  need(oracle.schema==="ttm.o0.n1.public.oracle.v1"&&oracle.labels_public&&!oracle.sealed_final,"ORACLE_META");
  need(mod.records.length===oracle.records.length,"ROW_MISMATCH");
  for(let i=0;i<mod.records.length;i++){
   const x=mod.records[i],y=oracle.records[i];
   need(Object.keys(x).sort().join(",")==="question,story","MODEL_RECORD_ALLOWLIST");
   need(x.story===y.story&&x.question===y.question,"INPUT_MISMATCH");
   need(x.story.length<=1200&&x.question.length<130,"EXCESSIVE_TEXT");
   const key=x.story+"\n"+x.question;need(!seen.has(key),"INPUT_DUPLICATE");seen.add(key);
   need(interpret(x.story,x.question)===y.answer,"ORACLE_FAIL");
   report.correct++;stats.rows++;stats.families[y.family]++;
   if(!groups.has(y.group_id))groups.set(y.group_id,[]);groups.get(y.group_id).push(y);
   if(split==="TRAIN")sig.TRAIN.add(y.structural_signature);
   if(split==="DEV_STRUCT")sig.DEV_STRUCT.add(y.structural_signature);
  }
  report.by_split[split]=stats;
 }
 for(const [gid,r] of groups){
  need(r.length===4,"GROUP_SIZE");const z=Object.fromEntries(r.map(x=>[x.cell,x]));
  need(["A_TARGET","B_TARGET","A_DISTRACTOR","B_DISTRACTOR"].every(k=>z[k]),"MISSING_CELL");
  need(z.A_TARGET.answer!==z.B_TARGET.answer&&z.A_DISTRACTOR.answer===z.B_DISTRACTOR.answer,"INVARIANT_FAIL");
  need(z.A_TARGET.story===z.A_DISTRACTOR.story&&z.B_TARGET.story===z.B_DISTRACTOR.story,"SHARED_STORY_FAIL");
  need(z.A_TARGET.question===z.B_TARGET.question&&z.A_DISTRACTOR.question===z.B_DISTRACTOR.question,"SHARED_QUERY_FAIL");
  report.quartets_verified++;
 }
 report.groups=groups.size;
 for(const x of sig.DEV_STRUCT)if(sig.TRAIN.has(x))report.coarse_struct_signature_overlap++;
 need(report.correct===4608&&report.groups===1152&&report.coarse_struct_signature_overlap===0,"DATASET_SIZE_OR_SIG");
 const sample=a.DEV_IID.model, mutate=[];
 for(const k of ["answer","source_events","split","group_id","id"]){let y=JSON.parse(JSON.stringify(sample));y.records[0][k]="INJECT";mutate.push(y)}
 for(const k of ["oracle","answer_vector","split"]){let y=JSON.parse(JSON.stringify(sample));y[k]="INJECT";mutate.push(y)}
 for(const y of mutate){
  let rejected=false;
  try{need(Object.keys(y).sort().join(",")==="records,schema","MUTANT_ROOT");for(const z of y.records)need(Object.keys(z).sort().join(",")==="question,story","MUTANT_ROW")}
  catch(e){if(String(e).startsWith("Error: STRICT_QA:"))rejected=true;else throw e}
  need(rejected,"MUTATION_ACCEPTED");report.mutants_rejected++;
 }
 // Five semantic illegal-state mutants.
 const changes=[
  [/(\w+) handed the (\w+) to label/,"Nobody handed the $2 to label"],
  [/(\w+) delegated the duty (\w+) to/,"Nobody delegated the duty $2 to"],
  [/(\w+) cancelled the duty (\w+)\./,"Nobody cancelled the duty $2."],
  [/(\w+) passed the (\w+) to the guide/,"Nobody passed the $2 to the guide"],
  [/(\w+) filed the (\w+) for the owner/,"Nobody filed the $2 for the owner"]
 ];
 for(const [pat,rep] of changes){
  const rec=a.TRAIN.oracle.records.find(x=>pat.test(x.story));need(rec,"MUTATION_FIXTURE_MISSING");
  let rejected=false;try{interpret(rec.story.replace(pat,rep),rec.question)}catch(e){rejected=String(e).startsWith("Error: STRICT_QA:")}
  need(rejected,"SEMANTIC_MUTATION_ACCEPTED");report.mutants_rejected++;
 }
 report.status="PASS_4608_VISIBLE_TEXT_1152_QUARTETS_13_NEGATIVE";
 report.notes=["Programmatic object allowlist tested with 8 mutations; raw duplicate JSON-key scanning requires a separate byte-level validator before science.","Five illegal-state story mutations rejected independently of the generator.","Coarse split signature is not full query-rooted graph isomorphism, so structural claim stays HOLD.","Public DEV labels cannot serve as hidden FINAL."];
 return report;
};
