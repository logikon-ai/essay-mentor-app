# argumentative essay analysis data model

from typing import List

import dataclasses

@dataclasses.dataclass
class EssayContentItem:
    uid: str
    name: str
    text: str
    html: str
    heading_level: int = 0

@dataclasses.dataclass
class MainQuestion:
    uid: str
    text: str
    claim_refs: List[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class MainClaim:
    uid: str
    text: str
    question_refs: List[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Gist:
    uid: str
    text: str
    essay_text_refs: List[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class FOReasonGist(Gist):
    claim_ref: str = ""

@dataclasses.dataclass
class SOObjectionGist(Gist):
    for_ref: str = ""

@dataclasses.dataclass
class TORebuttalGist(Gist):
    soo_ref: str = ""

@dataclasses.dataclass
class ArgumentativeEssayAnalysis:
    essaytext_md: str = ""
    essaytext_html: str = ""
    essay_content_items: List[EssayContentItem] = dataclasses.field(default_factory=list)
    main_questions: List[MainQuestion] = dataclasses.field(default_factory=list)
    main_claims: List[MainClaim] = dataclasses.field(default_factory=list)
    reasons: List[FOReasonGist] = dataclasses.field(default_factory=list)
    objections: List[SOObjectionGist] = dataclasses.field(default_factory=list)
    rebuttals: List[TORebuttalGist] = dataclasses.field(default_factory=list)