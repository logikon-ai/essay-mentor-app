# argumentative essay analysis data model

from typing import List, Dict

import uuid
import dataclasses


@dataclasses.dataclass
class BaseContentItem:
    text: str
    uid: str = dataclasses.field(init=False)

    def __post_init__(self):
        self.uid = str(uuid.uuid4())


@dataclasses.dataclass
class EssayContentItem(BaseContentItem):
    name: str
    html: str
    heading_level: int = 0
    label: str = ""

    def formatted_label(self) -> str:
        format = "¶{label}" if self.name=="p" else "⋮{label}"
        return format.format(label=self.label)


@dataclasses.dataclass
class MainQuestion(BaseContentItem):
    claim_refs: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class MapContentItem(BaseContentItem):
    label: str

@dataclasses.dataclass
class MainClaim(MapContentItem):
    question_refs: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Reason(MapContentItem):
    parent_uid: str
    essay_text_refs: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ArgumentativeEssayAnalysis:
    essaytext_md: str = ""
    essaytext_html: str = ""
    essay_content_items: List[EssayContentItem] = dataclasses.field(default_factory=list)
    main_questions: List[MainQuestion] = dataclasses.field(default_factory=list)
    main_claims: List[MainClaim] = dataclasses.field(default_factory=list)
    reasons: List[Reason] = dataclasses.field(default_factory=list)
    objections: List[Reason] = dataclasses.field(default_factory=list)
    rebuttals: List[Reason] = dataclasses.field(default_factory=list)


    def get_map_node_by_uid(self, uid: str) -> MapContentItem:
        for item in self.main_claims + self.reasons + self.objections + self.rebuttals:
            if item.uid == uid:
                return item
        raise ValueError(f"Could not find map node with uid {uid}")


    def get_reason_by_uid(self, uid: str) -> Reason:
        for reason in self.reasons + self.objections + self.rebuttals:
            if reason.uid == uid:
                return reason
        raise ValueError(f"Could not find reason with uid {uid}")


    def get_essay_item_by_uid(self, uid: str) -> EssayContentItem:
        for essay_item in self.essay_content_items:
            if essay_item.uid == uid:
                return essay_item
        raise ValueError(f"Could not find essay_item with uid {uid}")


    def as_api_argmap(self) -> Dict:
        nodelist = []
        edgelist = []
        for claim in self.main_claims:
            nodelist.append(
                dict(
                    id=claim.uid,
                    text=claim.text,
                    label=claim.label,
                    nodeType="proposition",
                    annotationReferences=[],
                )
            )
        arguments = self.reasons if self.reasons else []
        if self.objections:
            arguments += self.objections
        if self.rebuttals:
            arguments += self.rebuttals
        for argument in arguments:
            nodelist.append(
                dict(
                    id=argument.uid,
                    text=argument.text,
                    label=argument.label,
                    nodeType="proposition",
                    annotationReferences=[
                        dict(textContentId=ref, start=0,end=-1)
                        for ref in argument.essay_text_refs
                    ]
                )
            )
            edgelist.append(
                dict(
                    source=argument.uid,
                    target=argument.parent_uid,
                    valence="pro" if argument in self.reasons else "con",
                )
            )

        return dict(
            nodelist = nodelist,
            edgelist = edgelist,
        )


    def as_api_textContentItems(self) -> List[Dict]:
        text_content_items = []
        for essay_element in self.essay_content_items:
            text_content_items.append(
                dict(
                    id = essay_element.uid,
                    text = essay_element.text,
                    name = essay_element.label,
                )
            )
        return text_content_items

