
import chromadb
import requests
import json
import re
from datetime import datetime
from .core.config import GEMINI_API_KEY


chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="moderation_rules")

def add_new_rule(rule_id: str, rule_text: str, user_id: str, api_key: str):
    """Add a new moderation rule to ChromaDB with API key association"""
    try:
        # Create a unique rule ID that includes API key to avoid conflicts
        unique_rule_id = f"{api_key}:{rule_id}"
        
        # Check if rule_id already exists for this API key
        try:
            existing = collection.get(ids=[unique_rule_id])
            if existing['ids']:
                return {"success": False, "message": f"Rule with ID '{rule_id}' already exists for this API key"}
        except:
            pass  # Rule doesn't exist, which is what we want
        
        collection.add(
            documents=[rule_text],
            metadatas=[{
                "user_id": user_id, 
                "api_key": api_key,
                "rule_id": rule_id,  # Original rule ID for display purposes
                "created_at": str(datetime.now())
            }],
            ids=[unique_rule_id]
        )
        return {"success": True, "message": "Rule added successfully"}
    except Exception as e:
        return {"success": False, "message": f"Failed to add rule: {str(e)}"}

def delete_rule(rule_id: str, user_id: str, api_key: str):
    """Delete a specific rule for a user with API key"""
    try:
        unique_rule_id = f"{api_key}:{rule_id}"
        
        # First check if the rule exists and belongs to the user and API key
        try:
            existing = collection.get(ids=[unique_rule_id])
            if not existing['ids']:
                return {"success": False, "message": f"Rule with ID '{rule_id}' not found for this API key"}
            
            # Check if the rule belongs to the user and API key
            rule_metadata = existing['metadatas'][0]
            if rule_metadata.get('user_id') != user_id or rule_metadata.get('api_key') != api_key:
                return {"success": False, "message": "Rule not found or access denied"}
        except:
            return {"success": False, "message": f"Rule with ID '{rule_id}' not found for this API key"}
        
        collection.delete(ids=[unique_rule_id])
        return {"success": True, "message": "Rule deleted successfully"}
    except Exception as e:
        return {"success": False, "message": f"Failed to delete rule: {str(e)}"}

def get_user_rules(user_id: str, api_key: str):
    """Get all rules for a specific user and API key"""
    try:
        results = collection.get(
            where={"$and": [{"user_id": user_id}, {"api_key": api_key}]}
        )
        
        if not results['ids']:
            return {"success": True, "rules": [], "message": "No rules found for this user and API key"}
        
        rules = []
        for i, unique_rule_id in enumerate(results['ids']):
            # Extract the original rule_id from metadata
            original_rule_id = results['metadatas'][i].get('rule_id', unique_rule_id.split(':', 1)[1])
            rules.append({
                "rule_id": original_rule_id,
                "rule_text": results['documents'][i],
                "metadata": results['metadatas'][i]
            })
        
        return {"success": True, "rules": rules, "message": f"Found {len(rules)} rules for this API key"}
    except Exception as e:
        return {"success": False, "rules": [], "message": f"Failed to get rules: {str(e)}"}

def get_all_api_key_rules(api_key: str):
    """Get all rules for a specific API key (across all users)"""
    try:
        results = collection.get(
            where={"api_key": api_key}
        )
        
        if not results['ids']:
            return {"success": True, "rules": [], "message": "No rules found for this API key"}
        
        rules = []
        for i, unique_rule_id in enumerate(results['ids']):
            original_rule_id = results['metadatas'][i].get('rule_id', unique_rule_id.split(':', 1)[1])
            rules.append({
                "rule_id": original_rule_id,
                "rule_text": results['documents'][i],
                "metadata": results['metadatas'][i]
            })
        
        return {"success": True, "rules": rules, "message": f"Found {len(rules)} rules for this API key"}
    except Exception as e:
        return {"success": False, "rules": [], "message": f"Failed to get rules: {str(e)}"}

def update_rule(rule_id: str, new_rule_text: str, user_id: str, api_key: str):
    """Update an existing rule for a user with API key"""
    try:
        unique_rule_id = f"{api_key}:{rule_id}"
        
        # First verify the rule exists and belongs to the user and API key
        try:
            existing = collection.get(ids=[unique_rule_id])
            if not existing['ids']:
                return {"success": False, "message": f"Rule with ID '{rule_id}' not found for this API key"}
            
            rule_metadata = existing['metadatas'][0]
            if rule_metadata.get('user_id') != user_id or rule_metadata.get('api_key') != api_key:
                return {"success": False, "message": "Rule not found or access denied"}
        except:
            return {"success": False, "message": f"Rule with ID '{rule_id}' not found for this API key"}
        
        # Update the rule
        collection.update(
            ids=[unique_rule_id],
            documents=[new_rule_text],
            metadatas=[{
                "user_id": user_id,
                "api_key": api_key,
                "rule_id": rule_id,
                "updated_at": str(datetime.now())
            }]
        )
        return {"success": True, "message": "Rule updated successfully"}
    except Exception as e:
        return {"success": False, "message": f"Failed to update rule: {str(e)}"}

def extract_json(text):
    """Helper to extract JSON from text"""
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        return match.group(0)
    return text

def check_moderation(text: str, user_id: str, api_key: str):
    """Check if text violates user's moderation rules using Gemini API with API key filtering"""
    try:
        # Query ChromaDB for ALL relevant rules for this API key and user
        results = collection.query(
            query_texts=[text],
            n_results=5,  # Get top 5 most relevant rules
            where={"$and": [{"user_id": user_id}, {"api_key": api_key}]}
        )
        
        if not results['documents'] or not results['documents'][0]:
            return {
                "is_violation": False,
                "reason": "No moderation rules found for this user and API key"
            }
        
        # Get all retrieved rules
        retrieved_rules = results['documents'][0]
        rule_ids = [metadata.get('rule_id', 'unknown') for metadata in results['metadatas'][0]] if results['metadatas'] else []
        
        # Combine multiple rules into the prompt
        rules_text = ""
        for i, rule in enumerate(retrieved_rules):
            rule_id = rule_ids[i] if i < len(rule_ids) else f"rule_{i+1}"
            rules_text += f"Rule {i+1} (ID: {rule_id}): {rule}\n\n"
        
        # Enhanced prompt for multiple rules with API key context
        prompt = f"""
You are a content moderation AI. Your task is to determine if a piece of text violates ANY of the provided user-defined rules for a specific API key context.
You must respond ONLY with a valid JSON object with two keys: "is_violation" (boolean) and "reason" (a brief string explanation).

If ANY rule is violated, set "is_violation" to true and explain which rule was violated and why.
If NO rules are violated, set "is_violation" to false with a brief explanation.

API Key Context: Content moderation rules for API key ending in ...{api_key[-4:]}
User ID: {user_id}

User's Moderation Rules:
{rules_text}

Text to Moderate: "{text}"

JSON Response:
"""
        
        # Call Gemini API
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": GEMINI_API_KEY
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        gemini_response = resp.json()
        result_json = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
        
        # Parse JSON response
        json_str = extract_json(result_json)
        final_result = json.loads(json_str)
        
        return {
            "is_violation": final_result.get("is_violation", False),
            "reason": final_result.get("reason", "No reason provided")
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "is_violation": None,
            "reason": f"Gemini API call failed: {str(e)}"
        }
    except json.JSONDecodeError as e:
        return {
            "is_violation": None,
            "reason": f"Failed to parse Gemini response as JSON: {str(e)}"
        }
    except Exception as e:
        return {
            "is_violation": None,
            "reason": f"Moderation check failed: {str(e)}"
        }