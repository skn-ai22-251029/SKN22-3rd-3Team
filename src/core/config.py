import os
from dataclasses import dataclass
from typing import List, Dict, Any, Literal

@dataclass
class VersionPolicy:
    version: str
    db_name: str
    collection_name: str = "care_guides"
    breed_collection: str = "breeds"
    raw_data_path: str = "data/bemypet_catlab.json"
    processed_data_path: str = ""
    breed_data_path: str = ""
    
    # Taxonomic Settings
    is_multi_label: bool = False
    has_specialists: bool = False
    categories: List[str] = None
    specialists: List[str] = None

# V1 Legacy Policy
V1_POLICY = VersionPolicy(
    version="v1",
    db_name="catfit",
    processed_data_path="data/v1/bemypet_catlab_preprocessed.json",
    breed_data_path="data/v1/cat_breeds_integrated.json",
    is_multi_label=False,
    has_specialists=False,
    categories=["Health", "Nutrition", "Behavior", "Care", "Grooming", "Product", "General"]
)

# V2 Pro Policy
V2_POLICY = VersionPolicy(
    version="v2",
    db_name="catfit_v2",
    processed_data_path="data/v2/bemypet_catlab_v2_preprocessed.json",
    breed_data_path="data/v2/cat_breeds_integrated.json",
    is_multi_label=True,
    has_specialists=True,
    categories=[
        "Health (건강/질병)", "Nutrition (영양/식단)", "Behavior (행동/심리)",
        "Care (양육/관리)", "Living (생활/환경)", "Product (제품/용품)",
        "Legal/Social (법률/사회)", "Farewell (이별/상실)", "General Info (상식/정보)"
    ],
    specialists=[
        "Matchmaker (맞춤 추천)", "Liaison (실전 입양/구조)",
        "Peacekeeper (갈등 조정/행동)", "Physician (건강/의료)"
    ]
)

class ZipsaConfig:
    POLICIES = {
        "v1": V1_POLICY,
        "v2": V2_POLICY
    }

    @classmethod
    def get_policy(cls, version: str) -> VersionPolicy:
        if version not in cls.POLICIES:
            raise ValueError(f"Unknown version: {version}")
        return cls.POLICIES[version]
