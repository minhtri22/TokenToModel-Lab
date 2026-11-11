#!/usr/bin/env python3
"""Public reproducible CF1 DEV only. No FINAL scenarios, seeds, labels or keys.

Self-authored short naturalistic stories (not a blind science dataset).
Any future model evaluation on this public DEV must be exploratory.
"""
from __future__ import annotations
import argparse,hashlib,json,random
from pathlib import Path
SCENES=[]
def add(family,lead,clue_a,clue_b,tail,ending):
    SCENES.append((family,lead,clue_a,clue_b,tail,ending))
# DEV content below: first four plots from each family, as frozen before any neural score.
add('C1',"At the town library, two visitors had left parcels behind the counter. The clerk found a blue claim slip with a tiny drawing of a bird.","The clerk checked the log: the blue slip was issued to {a}, not {b}.","The clerk checked the log: the blue slip was issued to {b}, not {a}.","The parcel carried the same bird drawing. The clerk followed the log rather than trusting either visitor's memory.","The clerk returned the parcel to {name}.")
add('C1',"During a community art show, two painters stored canvases in the same locked room. One canvas had a ribbon along its wooden frame.","The exhibition list linked the ribbon-marked canvas to {a}, although {b} had carried it inside.","The exhibition list linked the ribbon-marked canvas to {b}, although {a} had carried it inside.","The gallery assistant had promised to return each work to the painter listed beside its mark.","The ribbon-marked canvas was handed to {name}.")
add('C1',"The station's lost-property desk held a suitcase without a name tag. Its handle was wrapped in orange tape.","The duty officer found that {a}, rather than {b}, had registered that tape pattern in the luggage book.","The duty officer found that {b}, rather than {a}, had registered that tape pattern in the luggage book.","The officer ignored the order in which the travelers came to ask. The tape registration was decisive.","The suitcase was released to {name}.")
add('C1',"A neighborhood repair shop kept two bicycles under a single tarp. One bicycle had a small brass bell and a bent left pedal.","On the service form, the bell-and-pedal description belonged to {a}; {b}'s bicycle was different.","On the service form, the bell-and-pedal description belonged to {b}; {a}'s bicycle was different.","The mechanic checked that description carefully before giving anyone a bicycle.","The mechanic gave the bicycle to {name}.")
add('C2',"The residents' committee was preparing a short public report. Two members could have taken responsibility, but the minutes named only one editor.","After the vote, {a} accepted responsibility for the report and {b} remained available as a backup.","After the vote, {b} accepted responsibility for the report and {a} remained available as a backup.","The chair asked who had the active obligation, not who might volunteer next week.","The report was now {name}'s responsibility.")
add('C2',"At the school festival, the volunteers changed their plan for arranging chairs. A written assignment was made before anyone moved a chair.","The final assignment gave the chair plan to {a}; {b} would only advise if asked.","The final assignment gave the chair plan to {b}; {a} would only advise if asked.","Later, the director read the assignment aloud to avoid confusing advice with ownership of the task.","The chair plan was assigned to {name}.")
add('C2',"A health clinic organized a patient-information leaflet. Two staff members had suggested ideas for it at the meeting.","The coordinator formally delegated the finished leaflet to {a}, releasing {b} from that duty.","The coordinator formally delegated the finished leaflet to {b}, releasing {a} from that duty.","No one had printed it yet. The coordinator only wanted to record whose task it currently was.","The leaflet remained a task for {name}.")
add('C2',"The neighborhood museum needed someone to update a visitor map. Both applicants were present when the director revised the schedule.","The director kept {a} on map duty and cancelled {b}'s earlier tentative assignment.","The director kept {b} on map duty and cancelled {a}'s earlier tentative assignment.","The old schedule was crossed out. The revised obligation was the only one still active.","The updated map was {name}'s assignment.")
add('C3',"The ferry company changed its final boarding time and posted a note beside the office door. Two travelers were waiting in different rooms.","Only {a} read the note saying boarding would close at six; {b} did not see the update.","Only {b} read the note saying boarding would close at six; {a} did not see the update.","Neither traveler spoke to the other before the clerk asked about the revised closing time.","The traveler who knew the revised time was {name}.")
add('C3',"The school moved a class into Room 12 and sent a notice through a staff chat. Two teachers had their phones on the desk.","{a} opened the new room notice; {b} was offline and received no other message.","{b} opened the new room notice; {a} was offline and received no other message.","There was no later conversation. The principal wanted to know whose information had actually changed.","The teacher who knew the new room was {name}.")
add('C3',"A gallery curator moved the opening talk to the east hall. A printed update was placed near the entrance.","{a} stopped to read the update while {b} walked past without looking.","{b} stopped to read the update while {a} walked past without looking.","They separated afterward and did not exchange messages. A guide asked who had learned about the east hall.","The informed visitor was {name}.")
add('C3',"The train operator replaced Platform 3 with Platform 7 on the departure board. The announcement was displayed but not spoken.","{a} studied the updated board; {b} remained in a waiting room with no view of it.","{b} studied the updated board; {a} remained in a waiting room with no view of it.","No one relayed the change. A station worker later asked which person had seen the new platform.","The person who knew about Platform 7 was {name}.")
# Exact short continuations set in the original authoring pass before source freeze.
SHORT_ENDINGS={
'C1':["The clerk gave it to {name}.","The canvas went to {name}.","The suitcase went to {name}.","The mechanic chose {name}."],
'C2':["{name} owned the task.","{name} kept the duty.","{name} had the leaflet task.","{name} held the assignment."],
'C3':["{name} knew the time.","{name} knew the room.","{name} knew the hall.","{name} knew the platform."]}
CASTS=[('Mira','Lena'),('Anna','Jack'),('Ella','Emma')]

def produce():
    pairs=[]
    for fam in ('C1','C2','C3'):
        scenes=[x for x in SCENES if x[0]==fam]
        assert len(scenes)==4
        for j,(_,lead,ca,cb,tail,_) in enumerate(scenes):
            for v,(a,b) in enumerate(CASTS):
                def render(z):return z.format(a=a,b=b).strip()
                A=render(lead)+' '+render(ca)+' '+render(tail)
                B=render(lead)+' '+render(cb)+' '+render(tail)
                x=' '+SHORT_ENDINGS[fam][j].format(name=a)
                y=' '+SHORT_ENDINGS[fam][j].format(name=b)
                pairs.append({'pair_id':f'{fam}-{j:02d}-{v}','family':fam,'motif_id':fam+'-'+str(j),
                    'context_a':A,'context_b':B,'completion_x':x,'completion_y':y,
                    'gold_a':'x','gold_b':'y','variant':v})
    assert len(pairs)==36
    random.Random(20261111).shuffle(pairs)
    public={'schema':'ttm.cf1.public_dev.v1','status':'PUBLIC_DEV_NOT_FINAL','pairs':pairs}
    model={'schema':'ttm.cf1.model_input.v1','records':[{k:r[k] for k in ('context_a','context_b','completion_x','completion_y')} for r in pairs]}
    return public,model

def canonical(z):return (json.dumps(z,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')

def main():
    a=argparse.ArgumentParser();a.add_argument('--out-dir');a.add_argument('--self-test',action='store_true');args=a.parse_args()
    oracle,model=produce()
    ob,mb=canonical(oracle),canonical(model)
    sha1='3a425188077f24041a02fe9675e5a503221fe5cc0247ebd53a8cc266329c046d'
    sha2='81e9849226029a1cb017c87da4202347be42dc92039db8c0d430d7115b68b4ed'
    if hashlib.sha256(ob).hexdigest()!=sha1 or hashlib.sha256(mb).hexdigest()!=sha2:
        raise RuntimeError('PUBLIC_DEV_SOURCE_GENERATION_SHA_FAILED')
    if args.out_dir:
        root=Path(args.out_dir).resolve();root.mkdir(parents=True,exist_ok=True)
        for name,data in [('CF1_DEV_PUBLIC_ORACLE.json',ob),('CF1_DEV_MODEL_INPUT_ONLY.json',mb)]:
            p=root/name
            with p.open('xb') as f:f.write(data)
    print('CF1_DEV_PUBLIC_REPRO_SHA=PASS_2/2; PAIRS=36')

if __name__=='__main__':main()
