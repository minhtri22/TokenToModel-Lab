import copy,json,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from r2_runtime_integration_executed import check,create,parse
p=pathlib.Path(__file__).parent
original=create()
assert check(original)['oracle_text_parser_correct']==256
cases={}
def case(name,change):
 y=copy.deepcopy(original)
 change(y)
 try:check(y)
 except (ValueError,AssertionError,KeyError,TypeError,IndexError,AttributeError) as e:
  cases[name]={'status':'REJECTED_AS_REQUIRED','error':str(e)[:100]}
 else:
  cases[name]={'status':'UNEXPECTED_ACCEPT'}

def mutate(idx,key,value):
 return lambda x:x['records'][idx].__setitem__(key,value)
case('wrong_owner_label',mutate(128,'answer','wrong'))
case('wrong_goal_label',mutate(0,'answer','wrong'))
case('duplicate_record_id',lambda x:x['records'][1].__setitem__('id',x['records'][0]['id']))
case('remove_record',lambda x:x['records'].pop())
case('wrong_schema',lambda x:x.__setitem__('schema','unfrozen'))
case('wrong_split',mutate(0,'split','CHALLENGE'))
case('wrong_variant',mutate(0,'variant',1))
case('alter_question',mutate(0,'question','What happens now?'))
case('invalid_goal_action',mutate(0,'story',original['records'][0]['story'].replace('plans to ','plans to teleport ',1)))
case('invalid_owner_entity',mutate(128,'story',original['records'][128]['story'].replace('belongs to ','belongs to Robot ',1)))
case('extra_line',mutate(0,'story',original['records'][0]['story']+'\nLan plans to read the book.'))
case('remove_line',mutate(0,'story','\n'.join(original['records'][0]['story'].splitlines()[:3])))
case('swap_order_without_answer_relabel',mutate(0,'story',original['records'][1]['story']))
case('replace_story_with_other',mutate(0,'story',original['records'][2]['story']))
case('duplicate_pair_label',mutate(0,'pair_id',original['records'][2]['pair_id']))
case('missing_update',mutate(0,'story',original['records'][0]['story'].replace(' plans to ',' wanted to ',1)))
case('tamper_family',mutate(0,'family','ownership'))
case('tamper_first_event',mutate(0,'story',original['records'][0]['story'].replace(original['records'][0]['story'].splitlines()[2],original['records'][0]['story'].splitlines()[0])))
case('malformed_pair_id',mutate(0,'pair_id','O000'))
case('non_string_story',mutate(0,'story',5))
case('duplicate_story',mutate(2,'story',original['records'][0]['story']))
# Positive property: changing only source_events is not grounds for a PASS claim: checker ignores source_events by design.
tampered=copy.deepcopy(original)
tampered['records'][0]['source_events']=[{'type':'assign','object':'key','person':'Lan'}]
source_events_ignored=(check(tampered)['oracle_text_parser_correct']==256)
assert source_events_ignored
bad=[name for name,z in cases.items() if z['status']!='REJECTED_AS_REQUIRED']
result={'overall':'PASS' if not bad else 'FAIL','negative_cases':len(cases),'rejected':len(cases)-len(bad),
        'failed_negative_cases':bad,'source_events_field_not_used_by_independent_parser':source_events_ignored,
        'scope':'synthetic protocol only; no neural network training or inference','cases':cases}
(p/'negative_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
print('NEGATIVE_AUDIT',result['overall'],result['rejected'],'/',result['negative_cases'], 'source_events_ignored=',source_events_ignored)
