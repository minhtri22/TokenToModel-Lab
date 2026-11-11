/** TTM O0 diagnostic N1: original public synthetic generator. No private FINAL seed or labels. */
export const generateO0Public = function generateO0Public(){
  const SEED=20261111, people=["Ada","Ben","Cora","Dax","Eve","Finn","Gia","Hank","Iris","Joel","Kira","Luz","Mona","Noel","Omar","Pia"], items=["lamp","coin","map","ring","book","bell","card","vase","drum","kite","pear","quill"], tags=["amber","cobalt","frost","lotus","meadow","raven","sable","tulip","violet","willow"], goals=["plant","draw","count","sing","write","read","paint","build","travel","learn"], rooms=["atrium","garden","hall","library","tower","studio","market","porch"];
  function seedRng(seed){let s=(seed>>>0)||1;return ()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return(s>>>0)}}
  function choices(arr,rng,n){const a=arr.slice(); for(let i=a.length-1;i>0;i--){const j=rng()%(i+1);[a[i],a[j]]=[a[j],a[i]]}return a.slice(0,n)}
  function pack(family,split,index,attempt=0){
    const salt=({TRAIN:7,DEV_IID:23,DEV_STRUCT:53})[split], rng=seedRng((SEED^Math.imul(index+1,19937)^Math.imul(family+1,1009009)^Math.imul(attempt+1,7919)^Math.imul(salt,65537))>>>0);
    const [a,b,c,d,e,f]=choices(people,rng,6),[x,y]=choices(items,rng,2),[tag,alt]=choices(tags,rng,2),[goal,dgoal]=choices(goals,rng,2),[room,room2]=choices(rooms,rng,2);
    const structural=split==="DEV_STRUCT", base=[`At sunset, ${e} checked a ledger.`,`During the morning, ${f} visited the ${room2}.`];
    function build(variant){
      const newOwner=variant===0?a:b;
      let rows, targetQuestion,dQuestion,targetAnswer,dAnswer, signature;
      if(family===0){
        rows=[
          `The label ${tag} designates ${newOwner}.`,
          structural?`The marker ${alt} designates label ${tag}.`:`The spare label ${alt} designates ${e}.`,
          `The ${x} was carried by ${c}.`,
          `The ${y} was carried by ${d}.`,
          `${c} handed the ${x} to ${structural?"marker "+alt:"label "+tag}.`,
          `The ${y} remained with ${d}.`,
          ...base
        ];
        targetQuestion=`Who carries the ${x} now?`;dQuestion=`Who carries the ${y} now?`;targetAnswer=newOwner;dAnswer=d;
        signature=`N1:${structural?"CHAIN2":"DIRECT_ALIAS"}:HOLDER`;
      }else if(family===1){
        rows=[
          `The duty ${goal} began with ${c}.`,
          `The duty ${dgoal} began with ${d}.`,
          structural?`${c} delegated the duty ${goal} to ${e}.`:`${c} delegated the duty ${goal} to ${a}.`,
          structural?`${e} delegated the duty ${goal} to ${a}.`:`The duty ${dgoal} was acknowledged by ${d}.`,
          variant===0?`${a} cancelled the duty ${goal}.`:`${a} delegated the duty ${goal} to ${b}.`,
          `The duty ${dgoal} stayed with ${d}.`,
          ...base
        ];
        targetQuestion=`Who holds the duty ${goal} now?`;dQuestion=`Who holds the duty ${dgoal} now?`;targetAnswer=variant===0?"NONE":b;dAnswer=d;
        signature=`N2:${structural?"DOUBLE_DELEGATE":"SINGLE_DELEGATE"}:CANCEL_VS_TRANSFER`;
      }else if(family===2){
        rows=[
          `In the ${room}, the guide is ${newOwner}.`,
          `In the ${room2}, the guide is ${d}.`,
          structural?`In the ${room}, the helper means the guide.`:`In the ${room2}, the helper means the guide.`,
          `The ${x} was initially with ${c}.`,
          `The ${y} was initially with ${d}.`,
          `${c} passed the ${x} to the ${structural?"helper":"guide"} in the ${room}.`,
          `The ${y} stayed with the guide in the ${room2}.`,
          ...base
        ];
        targetQuestion=`Who has the ${x} now?`;dQuestion=`Who has the ${y} now?`;targetAnswer=newOwner;dAnswer=d;
        signature=`N3:${structural?"ROLE_REF_CHAIN":"SCOPED_ROLE"}:HOLDER`;
      }else{
        rows=[
          `The seal ${tag} belongs to ${newOwner}.`,
          structural?`The badge ${alt} identifies seal ${tag}.`:`The badge ${alt} belongs to ${e}.`,
          `The ${x} was in care of ${c}.`,
          `The ${y} was in care of ${d}.`,
          `${c} filed the ${x} for the owner of ${structural?"badge "+alt:"seal "+tag}.`,
          `The ${y} remained filed under ${d}.`,
          ...base
        ];
        targetQuestion=`Who is responsible for the ${x} now?`;dQuestion=`Who is responsible for the ${y} now?`;targetAnswer=newOwner;dAnswer=d;
        signature=`N4:${structural?"SEAL_BADGE_CHAIN":"SEAL_DIRECT"}:HOLDER`;
      }
      // Preserve prerequisites and dependency order; vary only independent tail noise placement.
      if((rng()&1)===1){rows.splice(0,0,rows.pop())}
      return {story:rows.join("\n"),answers:[targetAnswer,dAnswer],questions:[targetQuestion,dQuestion],signature};
    }
    const A=build(0),B=build(1);
    if(A.questions.join("|")!==B.questions.join("|"))throw Error("PAIR_QUESTION_MISMATCH");
    if(A.answers[0]===B.answers[0]||A.answers[1]!==B.answers[1])throw Error("COUNTERFACTUAL_INVARIANT_FAIL");
    const rows=[];
    for(const [v,g] of [["A",A],["B",B]])for(let q=0;q<2;q++)rows.push({
      family:"N"+(family+1),split,group_id:split+"-N"+(family+1)+"-"+String(index+1).padStart(4,"0"),
      cell:v+(q===0?"_TARGET":"_DISTRACTOR"),story:g.story,question:g.questions[q],answer:g.answers[q],structural_signature:g.signature});
    return rows;
  }
  const sections={TRAIN:{groups:1024,per:256},DEV_IID:{groups:64,per:16},DEV_STRUCT:{groups:64,per:16}};
  const parts={}, seen=new Set(),stats={};
  for(const [split,detail] of Object.entries(sections)){
    const raw=[];
    for(let family=0;family<4;family++)for(let i=0;i<detail.per;i++){
      let q=null;
      for(let attempt=0;attempt<200;attempt++){
        const trial=pack(family,split,i,attempt);
        if(trial.every(v=>!seen.has(v.story+"\nQUESTION="+v.question))){q=trial;break}
      }
      if(!q)throw Error("GENERATION_DEDUP_EXHAUSTED:"+split+":"+family+":"+i);
      for(const x of q){seen.add(x.story+"\nQUESTION="+x.question);raw.push(x)}
    }
    // Randomize row order without leaking group/family through sequential model-only JSON.
    const random=seedRng((SEED^Math.imul(detail.groups,9091))>>>0);
    for(let i=raw.length-1;i>0;i--){const j=random()%(i+1);[raw[i],raw[j]]=[raw[j],raw[i]]}
    parts[split]={
      oracle:{schema:"ttm.o0.n1.public.oracle.v1",split,labels_public:true,sealed_final:false,records:raw},
      model:{schema:"ttm.o0.n1.model.input.v1",records:raw.map(({story,question})=>({story,question}))}
    };
    stats[split]={groups:detail.groups,rows:raw.length,by_family:Object.fromEntries([1,2,3,4].map(i=>["N"+i,raw.filter(z=>z.family==="N"+i).length])),mean_story_chars:Math.round(raw.reduce((s,z)=>s+z.story.length,0)/raw.length),max_story_chars:Math.max(...raw.map(x=>x.story.length))};
  }
  return {parts,stats};
};
