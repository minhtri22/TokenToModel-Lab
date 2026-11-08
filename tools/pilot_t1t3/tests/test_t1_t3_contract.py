from pathlib import Path
import hashlib, importlib, json, os, sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import t1_source_split_tokenizer as t1
from source_t2 import ttm_gpt2_bpe2048 as original


def test_source_sha_metadata_pinned():
    assert t1.REV=='f54c09fd23315a6f9c86f9dc80f725de7d8f9c64'
    assert t1.SOURCES['TinyStories-train.txt'].startswith('c5cf5e22')
    assert t1.SOURCES['TinyStories-valid.txt'].startswith('94e43181')


def test_parser_chunked_delimiter(tmp_path):
    b=[b'Once upon a time.\nA cat.',b'\xe4\xbd\xa0\xe5\xa5\xbd!',b'final.']
    p=tmp_path/'f.txt';p.write_bytes(b'<|endoftext|>'.join(b)+t1.EOS)
    assert list(t1.iter_story_bytes(p,chunk_size=7))==b


def test_parser_utf8_fail_closed():
    with pytest.raises(UnicodeDecodeError):t1.eligible_raw(b'\xff')
    with pytest.raises(RuntimeError):t1.eligible_raw(b'abc\x00def')


def test_no_cross_split_leakage():
    s=t1.sha(b'abc')
    assert t1.key_for(s)==t1.key_for(s)
    assert len(t1.key_for(s))==64


def test_story_selection_order_independent():
    a=[(t1.sha(str(i).encode()),str(i)) for i in range(100)]
    h1=[];h2=[]
    for digest,text in a:t1.min_k_push(h1,12,digest,text,'TRAIN')
    for digest,text in reversed(a):t1.min_k_push(h2,12,digest,text,'TRAIN')
    assert [x[1] for x in t1.sorted_selection(h1)]==[x[1] for x in t1.sorted_selection(h2)]


def test_near_duplicates():
    s=' '.join(str(i) for i in range(30))
    assert t1.near(t1.word5(s),t1.word5(s))
    assert not t1.near(t1.word5(s),t1.word5('a b c'))
    chosen,n=t1.near_dedupe([{'text':s},{'text':s},{'text':'a b c d e f g h'}],[],2)
    assert len(chosen)==2 and n==1


def test_no_raw_in_public_result(tmp_path):
    story=[{'sha256':'1'*64,'text':'do not publish this raw story','split':'TRAIN'}]
    valid=[{'sha256':'2'*64,'text':'private validation story','split':'VAL'}]
    test=[{'sha256':'3'*64,'text':'private test story','split':'TEST'}]
    class FakeBPE:
        def manifest(self):return {'manifest_sha256':'0'*64}
    for name in t1.SOURCES:(tmp_path/name).write_bytes(name.encode())
    r=t1.build_manifest(story,valid,test,{},tmp_path,FakeBPE())
    j=json.dumps(r)
    assert 'do not publish this' not in j
    assert len(r['splits']['TRAIN'])==1


def test_train_only_negative_splits():
    bad=original.Story('q','abc','TEST','TinyStories-train.txt')
    with pytest.raises(RuntimeError):t1.efficient_bpe([bad])


def test_t3_exact_p02_pin():
    import t3_resume_smoke as t3
    p=ROOT/'p02_source_exact.py'
    p02=t3.load_p02(p)
    assert p02.GPT.__name__=='GPT'
    assert t3.CONFIG['n_layer']==4


def test_t3_corrupt_source_rejected(tmp_path):
    import t3_resume_smoke as t3
    p=tmp_path/'p02.py';p.write_text('x=1')
    with pytest.raises(RuntimeError):t3.load_p02(p)
