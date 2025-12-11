# FastAPI RAG Application - Postman Collection

This directory contains a comprehensive Postman collection for testing the FastAPI RAG Application API endpoints.

## 📁 **Files Included**

- **`FastAPI_RAG_Application.postman_collection.json`** - Main collection with all API tests
- **`FastAPI_RAG_Environment.postman_environment.json`** - Environment variables and configuration
- **`README.md`** - This documentation file

## 🚀 **Quick Start**

### **1. Import Collection and Environment**

1. **Open Postman**
2. **Import Collection**:
   - Click "Import" button
   - Select `FastAPI_RAG_Application.postman_collection.json`
   - Click "Import"

3. **Import Environment**:
   - Click "Import" button  
   - Select `FastAPI_RAG_Environment.postman_environment.json`
   - Click "Import"

4. **Select Environment**:
   - In the top-right corner, select "FastAPI RAG Environment"

### **2. Start the Application**

```bash
# Make sure your FastAPI application is running
cd /path/to/llm-chatbot-with-rag
python src/main.py
```

### **3. Run Tests**

- **Individual Tests**: Click on any request and hit "Send"
- **Collection Runner**: Click "Run Collection" to execute all tests
- **Automated Testing**: Use Newman CLI for CI/CD integration

## 📋 **Collection Structure**

### **1. Health Checks** (4 requests)
- ✅ **Root Endpoint** - Application information
- ✅ **Simple Health Check** - Local service status
- ✅ **External API Health (Unauthenticated)** - Basic external API check
- ✅ **External API Health (Authenticated)** - Full external API check

### **2. Chat Completion** (4 requests)
- ✅ **Simple Chat Completion** - Basic single-turn conversation
- ✅ **Simple Chat with Custom Parameters** - Custom temperature/tokens
- ✅ **Advanced Chat Completion** - Multi-parameter control
- ✅ **Multi-turn Conversation** - Context-aware conversation

### **3. Error Scenarios** (6 requests)
- ❌ **Missing Message** - Validation error testing
- ❌ **Empty Message** - Business logic error testing
- ❌ **Invalid Parameters** - Parameter validation testing
- ❌ **Empty Messages Array** - Advanced chat validation
- ❌ **Invalid Role** - Message role validation
- ❌ **Non-existent Endpoint** - 404 error testing

### **4. Documentation** (3 requests)
- 📚 **OpenAPI Documentation** - Swagger UI access
- 📚 **ReDoc Documentation** - Alternative docs
- 📚 **OpenAPI Schema** - JSON schema download

## 🔧 **Environment Variables**

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `base_url` | `http://localhost:8000` | API base URL |
| `api_timeout` | `30000` | Request timeout (ms) |
| `test_message` | `Hello! This is a test...` | Default test message |
| `max_tokens_default` | `150` | Default max tokens |
| `temperature_default` | `0.7` | Default temperature |
| `model_default` | `gpt-4o-mini` | Default AI model |

### **Customizing Environment**

1. **Click the environment name** in top-right corner
2. **Edit variables** as needed:
   - Change `base_url` for different deployments
   - Adjust `api_timeout` for slower networks
   - Modify default parameters for testing

## 🧪 **Test Scenarios**

### **Successful Scenarios**

#### **Basic Health Check**
```http
GET {{base_url}}/health/simple
```
**Expected**: 200 OK with healthy status

#### **Simple Chat**
```http
POST {{base_url}}/chat/completion
Content-Type: application/json

{
    "message": "Hello, how are you?",
    "max_tokens": 100,
    "temperature": 0.7
}
```
**Expected**: 200 OK with AI response (if configured) or 401/500 (if not configured)

#### **Advanced Chat**
```http
POST {{base_url}}/chat/advanced
Content-Type: application/json

{
    "messages": [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"}
    ],
    "max_tokens": 200,
    "temperature": 0.5
}
```

### **Error Scenarios**

#### **Validation Errors (422)**
- Missing required fields
- Invalid parameter ranges
- Wrong data types

#### **Business Logic Errors (400)**
- Empty message strings
- Invalid chat roles
- Empty message arrays

#### **Configuration Errors (500/401)**
- Missing API credentials
- Invalid configuration
- Authentication failures

## 📊 **Automated Testing**

### **Collection Runner**

1. **Click "Run Collection"**
2. **Select requests** to run (or run all)
3. **Configure iterations** and delays
4. **View results** in real-time

### **Newman CLI**

```bash
# Install Newman
npm install -g newman

# Run collection
newman run FastAPI_RAG_Application.postman_collection.json \
  -e FastAPI_RAG_Environment.postman_environment.json \
  --reporters cli,json \
  --reporter-json-export results.json

# Run with custom environment
newman run FastAPI_RAG_Application.postman_collection.json \
  -e FastAPI_RAG_Environment.postman_environment.json \
  --env-var "base_url=https://your-api.com"
```

### **CI/CD Integration**

```yaml
# GitHub Actions example
- name: Run API Tests
  run: |
    newman run postman/FastAPI_RAG_Application.postman_collection.json \
      -e postman/FastAPI_RAG_Environment.postman_environment.json \
      --reporters cli,junit \
      --reporter-junit-export test-results.xml
```

## 🔍 **Test Assertions**

Each request includes comprehensive test assertions:

### **Status Code Validation**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
```

### **Response Structure Validation**
```javascript
pm.test("Response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('message');
    pm.expect(jsonData).to.have.property('status');
});
```

### **Performance Testing**
```javascript
pm.test("Response time is less than 1000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});
```

### **Content Validation**
```javascript
pm.test("Content is not empty", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.content).to.be.a('string');
    pm.expect(jsonData.content.length).to.be.above(0);
});
```

## 🛠 **Troubleshooting**

### **Common Issues**

#### **Connection Refused**
- ✅ Ensure FastAPI application is running
- ✅ Check `base_url` in environment variables
- ✅ Verify port 8000 is not blocked

#### **Authentication Errors (401)**
- ✅ Configure `.env` file with valid credentials
- ✅ Check `CLIENT_ID` and `CLIENT_SECRET`
- ✅ Verify external API access

#### **Timeout Errors**
- ✅ Increase `api_timeout` environment variable
- ✅ Check network connectivity
- ✅ Verify external API availability

#### **Validation Errors**
- ✅ Check request body format
- ✅ Verify required fields are present
- ✅ Ensure parameter values are within valid ranges

### **Debug Mode**

1. **Enable Postman Console**:
   - View → Show Postman Console
   - See detailed request/response logs

2. **Add Debug Logging**:
   ```javascript
   console.log('Request URL:', pm.request.url.toString());
   console.log('Response:', pm.response.json());
   ```

## 📈 **Performance Monitoring**

### **Response Time Tracking**
- All tests include response time assertions
- Monitor performance across different endpoints
- Set appropriate timeout thresholds

### **Load Testing**
```bash
# Run collection multiple times
newman run FastAPI_RAG_Application.postman_collection.json \
  -e FastAPI_RAG_Environment.postman_environment.json \
  -n 10 \
  --delay-request 1000
```

## 🔐 **Security Testing**

### **Authentication Testing**
- Tests both authenticated and unauthenticated endpoints
- Validates proper error responses for auth failures
- Checks credential handling

### **Input Validation**
- Tests various invalid input scenarios
- Validates proper error messages
- Ensures no sensitive data leakage

## 📝 **Customization**

### **Adding New Tests**

1. **Right-click collection** → "Add Request"
2. **Configure request** (method, URL, body)
3. **Add test assertions** in "Tests" tab
4. **Update documentation**

### **Modifying Existing Tests**

1. **Select request** to modify
2. **Update request parameters** as needed
3. **Modify test assertions** in "Tests" tab
4. **Test thoroughly** before saving

### **Environment Customization**

Create environment-specific configurations:
- **Development**: `http://localhost:8000`
- **Staging**: `https://staging-api.yourcompany.com`
- **Production**: `https://api.yourcompany.com`

## 📚 **Additional Resources**

- **Postman Documentation**: https://learning.postman.com/
- **Newman CLI**: https://github.com/postmanlabs/newman
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **API Testing Best Practices**: https://www.postman.com/api-testing/

---

**Happy Testing!** 🚀

For questions or issues, please refer to the main project documentation or create an issue in the repository.