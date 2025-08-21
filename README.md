# RAG Moderation API

A powerful content moderation API that uses **Vector Database (ChromaDB)** + **AI (Gemini)** to enforce custom moderation rules. Each API key maintains isolated rule sets with multi-user support.

## 🎯 **System Architecture**

### **🔑 Authentication vs Organization:**
- **`X-API-Key` header**: Backend secret for authentication (`your-strong-secret-key`)
- **`api_key` in request body**: Custom identifier for organizing rule sets (`sdsdusdhusdhsddsisjidjsdjsdj12223`)

### **📊 Rule Storage Structure:**
```json
{
  "rule_id": "my-app-key-001:no_profanity",
  "document": "Do not allow profanity or offensive language...",
  "metadata": {
    "user_id": "test_user",
    "api_key": "my-app-key-001", 
    "rule_id": "no_profanity",
    "created_at": "2025-08-21 ..."
  }
}
```

### **🚀 Technology Stack:**
- **FastAPI**: Modern Python web framework
- **ChromaDB**: Vector database for semantic rule matching
- **Google Gemini AI**: Content moderation decisions
- **Pydantic**: Data validation and schemas

## 📋 **Updated API Endpoints**

| Endpoint | Method | Body/Params | Description |
|----------|---------|-------------|-------------|
| `POST /add-rule/` | POST | `{user_id, api_key, rule_id, rule_text}` | Add new moderation rule |
| `GET /rules/{user_id}/{api_key}/` | GET | Path params | Get user's rules for specific API key |
| `GET /api-rules/{api_key}/` | GET | Path param | Get ALL rules for API key (all users) |
| `DELETE /delete-rule/{rule_id}/?user_id=X&api_key=Y` | DELETE | Path + Query params | Delete specific rule |
| `PUT /update-rule/{rule_id}/` | PUT | `{user_id, api_key, rule_text}` | Update existing rule |
| `POST /moderate/` | POST | `{user_id, api_key, text_to_moderate}` | Moderate text against rules |

### **📝 Request Examples:**

#### Add Rule:
```json
POST /add-rule/
Headers: X-API-Key: your-strong-secret-key
Body: {
    "user_id": "user123",
    "api_key": "sdsdusdhusdhsddsisjidjsdjsdj12223",
    "rule_id": "no_profanity", 
    "rule_text": "Do not allow profanity, swear words, or offensive language."
}
```

#### Moderate Text:
```json
POST /moderate/
Headers: X-API-Key: your-strong-secret-key
Body: {
    "user_id": "user123",
    "api_key": "sdsdusdhusdhsddsisjidjsdjsdj12223",
    "text_to_moderate": "This is some text to check"
}
```

## 🔄 **How It Works**

### **1. Rule Storage with Custom API Key:**
- Rules are stored with unique IDs: `{custom_api_key}:{rule_id}`
- Each custom API key maintains completely isolated rule sets
- Multiple users can share the same custom API key with different rules

### **2. Semantic Rule Matching:**
- Uses ChromaDB vector database for semantic similarity search
- Finds top 5 most relevant rules for the text being moderated
- Filters rules by both `user_id` and custom `api_key`

### **3. AI-Powered Moderation:**
- Sends relevant rules + text to Google Gemini AI
- AI determines if ANY rule is violated
- Returns detailed reasoning and violation status

### **4. Multi-Rule Support:**
- Users can add multiple rules (paragraphs supported)
- Each rule can be complex and detailed
- AI checks against ALL relevant rules simultaneously

## 💡 **Use Case Examples**

### **Scenario 1: Multiple Applications**
```json
// Mobile app rules (family-friendly)
{
    "user_id": "user123",
    "api_key": "mobile-app-v1-abc123",
    "rule_id": "family_friendly",
    "rule_text": "Block inappropriate content, violence, and adult themes for family app users."
}

// Web app rules (professional context)
{
    "user_id": "user123", 
    "api_key": "web-app-v2-xyz789",
    "rule_id": "professional",
    "rule_text": "Block unprofessional language, spam, and off-topic content for business platform."
}
```

### **Scenario 2: Environment Separation**
```json
// Development environment
{
    "user_id": "developer1",
    "api_key": "dev-env-testing-001",
    "rule_id": "test_rule",
    "rule_text": "Simple test rule for development."
}

// Production environment  
{
    "user_id": "developer1",
    "api_key": "prod-env-live-001", 
    "rule_id": "strict_moderation",
    "rule_text": "Comprehensive content moderation for production users..."
}
```

### **Scenario 3: Client Isolation**
```json
// Client A's rules
{
    "user_id": "admin",
    "api_key": "client-a-rules-2025",
    "rule_id": "brand_safety",
    "rule_text": "Protect brand image by blocking controversial topics..."
}

// Client B's rules (completely separate)
{
    "user_id": "admin",
    "api_key": "client-b-rules-2025",
    "rule_id": "legal_compliance", 
    "rule_text": "Ensure legal compliance for financial services content..."
}
```

## 🚀 **Getting Started**

### **Prerequisites:**
- Python 3.11+
- Google Gemini API key
- ChromaDB

### **Installation:**
```bash
# Clone repository
git clone <repo-url>
cd rag-moderation-api

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
GEMINI_API_KEY=your_gemini_api_key
DOT_NET_API_KEY=your-strong-secret-key
```

### **Run Server:**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### **Test with HTML Client:**
Open `test_client.html` in your browser and test the API endpoints.

## 📖 **API Documentation**

Once running, access interactive documentation at:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔧 **Key Features**

✅ **Custom API Key Organization**: Each API key has isolated rule sets  
✅ **Multi-User Support**: Multiple users per API key with separate rules  
✅ **Semantic Matching**: Vector database finds relevant rules intelligently  
✅ **AI-Powered Decisions**: Gemini AI provides detailed moderation reasoning  
✅ **Paragraph Rules**: Support for complex, multi-paragraph rules  
✅ **CORS Enabled**: Ready for frontend integration  
✅ **RESTful API**: Standard HTTP methods and status codes  
✅ **Type Safety**: Pydantic schemas for request/response validation  

## 🛡️ **Security Features**

- **API Key Authentication**: Secure access control
- **Request Validation**: Input sanitization and validation
- **Error Handling**: Graceful error responses
- **CORS Support**: Configurable cross-origin requests

## 📁 **Project Structure**

```
rag-moderation-api/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api.py               # API router setup
│   ├── schemas.py           # Pydantic models
│   ├── services.py          # Business logic
│   ├── core/
│   │   └── config.py        # Configuration
│   └── endpoints/
│       └── moderation.py    # API endpoints
├── chroma_db/               # ChromaDB storage
├── test_client.html         # HTML test interface
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.
