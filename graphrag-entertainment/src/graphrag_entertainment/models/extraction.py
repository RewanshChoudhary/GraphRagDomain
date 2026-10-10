from enum import StrEnum

from pydantic import BaseModel, Field

from graphrag_entertainment.models.schema import EntityType


class ExtractedEntity(BaseModel):
    name: str
    type: EntityType
    description: str


class RelationshipType(StrEnum):
    DIRECTED_BY = "DIRECTED_BY"
    WRITTEN_BY = "WRITTEN_BY"
    STARRED = "STARRED"
    FEATURES_CHARACTER = "FEATURES_CHARACTER"
    HAS_GENRE = "HAS_GENRE"
    PRODUCED_BY = "PRODUCED_BY"
    DISTRIBUTED_BY = "DISTRIBUTED_BY"
    PART_OF_FRANCHISE = "PART_OF_FRANCHISE"
    SEQUEL_OF = "SEQUEL_OF"
    PREQUEL_OF = "PREQUEL_OF"
    ADAPTED_FROM = "ADAPTED_FROM"
    ACTED_AS = "ACTED_AS"
    CREATED_BY = "CREATED_BY"
    COLLABORATED_WITH = "COLLABORATED_WITH"
    REVIEWED_BY = "REVIEWED_BY"
    PUBLISHED_BY = "PUBLISHED_BY"
    RATED = "RATED"
    PRAISED = "PRAISED"
    CRITICIZED = "CRITICIZED"
    LIKED = "LIKED"
    DISLIKED = "DISLIKED"
    RECOMMENDED = "RECOMMENDED"
    COMPARED_TO = "COMPARED_TO"
    RELATED_TO = "RELATED_TO"
    SET_IN = "SET_IN"
    TAKES_PLACE_IN = "TAKES_PLACE_IN"
    INFLUENCED_BY = "INFLUENCED_BY"


class ExtractedRelationship(BaseModel):
    source: str
    target: str
    type: RelationshipType
    description: str
    source_chunk_id: str


class ExtractedClaim(BaseModel):
    entity_name: str
    entity_type: EntityType
    description: str


class GraphExtraction(BaseModel):
    entities: list[ExtractedEntity]
    relationships: list[ExtractedRelationship]
    claims: list[ExtractedClaim] = Field(default_factory=list)
