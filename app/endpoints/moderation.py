from fastapi import APIRouter, HTTPException, Request
from .. import schemas, services

router = APIRouter()

@router.post("/add-rule/", status_code=201)
def add_rule(rule: schemas.Rule):
    """Add a new moderation rule with user's custom API key"""
    result = services.add_new_rule(rule.rule_id, rule.rule_text, rule.user_id, rule.api_key)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return {"message": result["message"]}

@router.delete("/delete-rule/{rule_id}/")
def delete_rule(rule_id: str, user_id: str, api_key: str):
    """Delete a specific moderation rule for the user's API key"""
    result = services.delete_rule(rule_id, user_id, api_key)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return {"message": result["message"]}

@router.get("/rules/{user_id}/{api_key}/")
def get_user_rules(user_id: str, api_key: str):
    """Get all moderation rules for a user and their custom API key"""
    result = services.get_user_rules(user_id, api_key)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return {"rules": result["rules"], "message": result["message"]}

@router.get("/api-rules/{api_key}/")
def get_api_key_rules(api_key: str):
    """Get all moderation rules for a custom API key (across all users)"""
    result = services.get_all_api_key_rules(api_key)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return {"rules": result["rules"], "message": result["message"]}

@router.put("/update-rule/{rule_id}/")
def update_rule(rule_id: str, updated_rule: schemas.UpdateRule):
    """Update an existing moderation rule for the user's API key"""
    result = services.update_rule(rule_id, updated_rule.rule_text, updated_rule.user_id, updated_rule.api_key)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return {"message": result["message"]}

@router.post("/moderate/", response_model=schemas.ModerationResponse)
def moderate(request_data: schemas.ModerationRequest):
    """Moderate text against user's rules using Gemini AI for the specific custom API key"""
    result = services.check_moderation(request_data.text_to_moderate, request_data.user_id, request_data.api_key)
    if result["is_violation"] is None:
        raise HTTPException(status_code=500, detail=result["reason"])
    return schemas.ModerationResponse(
        is_violation=result["is_violation"],
        reason=result["reason"]
    )