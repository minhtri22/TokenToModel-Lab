/** Predeclared shallow non-state baseline for O0 DIAG N1 public toy. */
export const aliasAwareLastEventHeuristic = function aliasAwareLastEventHeuristic(story,question){
 const target=((question.match(/\bthe (\w+) now\?$/)||question.match(/\bduty (\w+) now\?$/))||[])[1];
 if(!target)return "UNKNOWN";
 const lines=story.split("\n");
 const match=(s,pat)=>new RegExp(pat).exec(s);
 const alias={},marker={},seals={},badges={},guides={};
 for(const line of lines){
  let m;
  if((m=/^The (?:spare )?label (\w+) designates (\w+)\.$/.exec(line)))alias[m[1]]=m[2];
  if((m=/^The marker (\w+) designates label (\w+)\.$/.exec(line)))marker[m[1]]=m[2];
  if((m=/^The seal (\w+) belongs to (\w+)\.$/.exec(line)))seals[m[1]]=m[2];
  if((m=/^The badge (\w+) identifies seal (\w+)\.$/.exec(line)))badges[m[1]]=m[2];
  if((m=/^In the (\w+), the guide is (\w+)\.$/.exec(line)))guides[m[1]]=m[2];
 }
 if(question.startsWith("Who holds the duty ")){
  for(let i=lines.length-1;i>=0;i--){
   const line=lines[i];let m;
   if(match(line,"^\\w+ cancelled the duty "+target+"\\.$"))return "NONE";
   if((m=match(line,"^\\w+ delegated the duty "+target+" to (\\w+)\\.$")))return m[1];
   if((m=match(line,"^The duty "+target+" stayed with (\\w+)\\.$")))return m[1];
   if((m=match(line,"^The duty "+target+" began with (\\w+)\\.$")))return m[1];
  }
  return "UNKNOWN";
 }
 for(let i=lines.length-1;i>=0;i--){
  const line=lines[i];let m;
  if((m=match(line,"^\\w+ handed the "+target+" to (label|marker) (\\w+)\\.$")))return alias[m[1]==="marker"?marker[m[2]]:m[2]]||"UNKNOWN";
  if((m=match(line,"^\\w+ passed the "+target+" to the (guide|helper) in the (\\w+)\\.$")))return guides[m[2]]||"UNKNOWN";
  if((m=match(line,"^\\w+ filed the "+target+" for the owner of (seal|badge) (\\w+)\\.$")))return seals[m[1]==="badge"?badges[m[2]]:m[2]]||"UNKNOWN";
  if((m=match(line,"^The "+target+" (?:remained with|was carried by|was initially with|was in care of|remained filed under) (\\w+)\\.$")))return m[1];
  if((m=match(line,"^The "+target+" stayed with the guide in the (\\w+)\\.$")))return guides[m[1]]||"UNKNOWN";
 }
 return "UNKNOWN";
};
