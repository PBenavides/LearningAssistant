from pydantic import BaseModel
from typing import Dict

class ScoreSchema(BaseModel):
    level: str
    score: str
    strenghts: str
    weaknesses: str

class BloomsSchemaEvaluation(BaseModel):
    Remember: Dict[str, ScoreSchema]
    Understand: Dict[str, ScoreSchema]
    Apply: Dict[str, ScoreSchema]
    Analyze: Dict[str, ScoreSchema]
    Evaluate: Dict[str, ScoreSchema]
    Create: Dict[str, ScoreSchema]

class TopicSchema(BaseModel):
    topic_id: str
    topic_name: str
    subtopics: Dict[str, BloomsSchemaEvaluation]