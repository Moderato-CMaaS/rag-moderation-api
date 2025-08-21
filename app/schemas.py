from pydantic import BaseModel

class Rule(BaseModel):
    user_id: str
    rule_text: str
    rule_id: str
    api_key: str  # User's custom API key for organizing rule sets

class UpdateRule(BaseModel):
    user_id: str
    rule_text: str
    api_key: str  # User's custom API key

class ModerationRequest(BaseModel):
    user_id: str
    text_to_moderate: str
    api_key: str  # User's custom API key

class ModerationResponse(BaseModel):
    is_violation: bool
    reason: str

