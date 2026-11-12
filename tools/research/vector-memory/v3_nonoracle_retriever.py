#!/usr/bin/env python3
"""V3 non-Oracle symbolic retriever. Explicit public question + public index only.

No Reader, gold, value, answer, case_id, stratum, checkpoint or TEST access.
The novel paraphrase lexicon remains PROPOSED until two independent rater
receipts validate semantics. Source QA MUST NOT score this on real V3 cases.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from collections.abc import Mapping, Sequence
import v3_fresh256_fixture as fixture

ALLOWED = frozenset({'key','source_id','retrieval_text'})
SOURCES = frozenset(fixture.SOURCES)

@dataclass(frozen=True)
class Decision:
    status: str
    indices: tuple[int,...]
    reason_code: str


def _normalize(s: str)->str:
    if not isinstance(s,str) or not s:
        raise ValueError('INVALID_TEXT')
    return s.casefold().strip()


def _lex():
    mapping={}
    for axis, terms in fixture.VOCAB.items():
        for word in terms:
            if word in mapping:raise ValueError('DUPLICATE_LEXEME')
            mapping[word]=(axis,word)
    for axis, terms in fixture.PROPOSED_P1.items():
        for i,word in enumerate(terms):
            if word in mapping:raise ValueError('DUPLICATE_NOVEL_P1_LEXEME')
            mapping[word]=(axis,fixture.VOCAB[axis][i])
    return mapping

LEXICON = _lex()
WORD_PATTERNS = tuple((word,re.compile(r'(?<![a-z0-9])'+re.escape(word)+r'(?![a-z0-9])'))
                      for word in sorted(LEXICON,key=lambda w:(-len(w),w)))


def _mentions(text:str)->dict[str,set[str]]:
    result={k:set() for k in fixture.ATTRS}
    for term,pattern in WORD_PATTERNS:
        if pattern.search(text):
            axis,canon=LEXICON[term]
            result[axis].add(canon)
    return result


def _indexed_attrs(text: str)->dict[str,str]:
    # Different from parse-query lexicon: uses structured public descriptor tags.
    s=_normalize(text)
    m=re.fullmatch(r'color ([a-z]+); shape ([a-z]+); material ([a-z]+)',s)
    if m is None:raise ValueError('INVALID_CANONICAL_DESCRIPTOR')
    attrs=dict(zip(fixture.ATTRS,m.groups()))
    if any(attrs[k] not in fixture.VOCAB[k] for k in fixture.ATTRS):
        raise ValueError('UNKNOWN_INDEX_VALUE')
    return attrs


def _public_cards(cards: Sequence[Mapping[str,str]])->list[dict]:
    if not isinstance(cards,Sequence) or len(cards)!=32:
        raise ValueError('BANK_SIZE_MUST_EQUAL_32')
    cleaned=[]
    for card in cards:
        if not isinstance(card,Mapping) or set(card)!=ALLOWED:
            raise ValueError('INDEX_HAS_UNAUTHORIZED_FIELDS')
        if any(not isinstance(card[k],str) or not card[k] for k in ALLOWED):
            raise ValueError('MISSING_PUBLIC_INDEX_FIELD')
        if card['source_id'] not in SOURCES:
            raise ValueError('INVALID_SOURCE_ID')
        cleaned.append(dict(card))
    if len({x['key'] for x in cleaned})!=32:
        raise ValueError('DUPLICATE_KEY_IN_INDEX')
    return cleaned


def _parse_query(question: str)->tuple[dict[str,str],dict[str,str],str|None,str|None]:
    text=_normalize(question)
    if len(text)>512:raise ValueError('QUESTION_TOO_LONG')
    if 'made of ' in text:
        # Unrecognized material forms are not allowed to silently fall back to
        # a partial color/shape match. Known material in this form also abstains
        # unless explicitly supported in a later frozen source version.
        return {},{},None,'UNSUPPORTED_OOV_MATERIAL_EXPRESSION'
    excluded={}
    if ' excluding ' in text:
        before,after=text.split(' excluding ',1)
        m=re.match(r'(color|shape|material) ([a-z-]+)(?:\?|\b)',after)
        if m is None:
            return {},{},None,'INVALID_NEGATION_GRAMMAR'
        axis,term=m.groups();mentions=_mentions(term)
        if len(mentions[axis])!=1:
            return {},{},None,'NEGATED_TERM_UNKNOWN_OR_AMBIGUOUS'
        excluded[axis]=next(iter(mentions[axis]))
        text=before
    src=None
    src_match=re.findall(r'from source (src-[a-z]+)',text)
    if len(src_match)>1:
        return {},{},None,'MULTIPLE_SOURCE_REFERENCES'
    if src_match:
        src=src_match[0]
        if src not in SOURCES:
            return {},{},None,'UNKNOWN_SOURCE'
        text=text.replace('from source '+src,'')
    elif 'from source ' in text:
        return {},{},None,'MALFORMED_SOURCE'
    attrs=_mentions(text)
    if any(len(v)>1 for v in attrs.values()):
        return {},{},None,'CONTRADICTORY_POSITIVE_ATTRIBUTES'
    present={k:next(iter(v)) for k,v in attrs.items() if v}
    if any(present.get(axis)==value for axis,value in excluded.items()):
        return {},{},None,'CONTRADICTORY_POSITIVE_NEGATIVE_CONSTRAINT'
    if not present and src is None:
        return {},{},None,'UNRESOLVED_QUERY'
    return present,excluded,src,None


def retrieve(question: str, public_index: Sequence[Mapping[str,str]])->Decision:
    cards=_public_cards(public_index)
    pos,neg,source,invalid=_parse_query(question)
    if invalid is not None:
        return Decision('ABSTAIN',(),invalid)
    candidate=[]
    for idx,card in enumerate(cards):
        attrs=_indexed_attrs(card['retrieval_text'])
        if source is not None and card['source_id']!=source:continue
        if any(attrs[k]!=v for k,v in pos.items()):continue
        if any(attrs[k]==v for k,v in neg.items()):continue
        candidate.append(idx)
    if len(candidate)==1:
        return Decision('SELECT',(candidate[0],),'UNIQUE_PUBLIC_CONSTRAINT_MATCH')
    if not candidate:
        return Decision('ABSTAIN',(),'NO_PUBLIC_MATCH')
    return Decision('ABSTAIN',(),'MULTIPLE_PUBLIC_MATCHES')


def mask(decision:Decision,bank_size:int=32)->tuple[bool,...]:
    if bank_size!=32:raise ValueError('BAD_BANK_SIZE')
    if decision.status=='ABSTAIN':
        if decision.indices:raise ValueError('ABSTAIN_CANNOT_SELECT_ANY')
        return (False,)*bank_size
    if decision.status!='SELECT' or len(decision.indices)!=1:
        raise ValueError('SELECT_MUST_HAVE_SINGLE_INDEX')
    i=decision.indices[0]
    if type(i) is not int or not 0<=i<bank_size:
        raise ValueError('BAD_SELECTED_INDEX')
    return tuple(j==i for j in range(bank_size))
