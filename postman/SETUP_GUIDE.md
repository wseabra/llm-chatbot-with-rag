# FastAPI RAG Application - Postman Setup Guide

This guide will help you quickly set up and run the Postman collection for testing the FastAPI RAG Application.

## 🚀 **Quick Setup (5 minutes)**

### **Step 1: Install Prerequisites**

```bash
# Install Node.js (if not already installed)
# Download from: https://nodejs.org/

# Install Newman CLI globally
npm install -g newman

# Optional: Install HTML reporter for better reports
npm install -g newman-reporter-htmlextra
```

### **Step 2: Start the Application**

```bash
# Navigate to your project directory
cd /path/to/llm-chatbot-with-rag

# Start the FastAPI application
python src/main.py
```

You should see:
```
Starting FastAPI RAG Application server...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **Step 3: Import to Postman (GUI Method)**

1. **Open Postman**
2. **Import Collection**:
   - Click "Import" button
   - Drag & drop `FastAPI_RAG_Application.postman_collection.json`
   - Click "Import"

3. **Import Environment**:
   - Click "Import" button
   - Drag & drop `FastAPI_RAG_Environment.postman_environment.json`
   - Click "Import"

4. **Select Environment**:
   - Top-right dropdown → Select "FastAPI RAG Environment"

5. **Run Tests**:
   - Click "Run Collection" → "Run FastAPI RAG Application"

### **Step 4: Run via Command Line (Alternative)**

```bash
# Navigate to postman directory
cd postman/

# Run all tests (Linux/Mac)
./run_tests.sh

# Run all tests (Windows)
run_tests.bat

# Run with custom options
./run_tests.sh -u http://localhost:8000 -o html
```

## 📋 **What Gets Tested**

### ✅ **Health Checks**
- Application info endpoint
- Local service health
- External API connectivity (with/without auth)

### ✅ **Chat Completion**
- Simple single-turn conversations
- Advanced multi-turn conversations
- Custom parameters (temperature, max_tokens)
- System message handling

### ❌ **Error Scenarios**
- Missing required fields (422 errors)
- Empty/invalid inputs (400 errors)
- Parameter validation (422 errors)
- Non-existent endpoints (404 errors)

### 📚 **Documentation**
- Swagger UI accessibility
- ReDoc documentation
- OpenAPI schema download

## 🔧 **Configuration Options**

### **Environment Variables**

| Variable | Purpose | Default |
|----------|---------|---------|
| `base_url` | API endpoint | `http://localhost:8000` |
| `api_timeout` | Request timeout | `30000ms` |
| `test_message` | Default test message | `"Hello! This is..."` |

### **Custom Configuration**

Edit environment variables in Postman:
1. Click environment name (top-right)
2. Modify values as needed
3. Save changes

## 🎯 **Expected Results**

### **With Proper Configuration**
- ✅ Health checks: All pass
- ✅ Chat completion: Returns AI responses
- ❌ Error scenarios: Proper error codes
- 📚 Documentation: Accessible

### **Without External API Configuration**
- ✅ Health checks: Local passes, external may fail
- ❌ Chat completion: 401/500 errors (expected)
- ❌ Error scenarios: Still test validation
- ✅ Documentation: Still accessible

## 🛠 **Troubleshooting**

### **Common Issues & Solutions**

#### **"Newman not found"**
```bash
# Install Newman globally
npm install -g newman

# Verify installation
newman --version
```

#### **"Connection refused"**
```bash
# Check if app is running
curl http://localhost:8000/health/simple

# Start the application
python src/main.py
```

#### **"Authentication failed" (401 errors)**
```bash
# Configure environment variables
cp .env.example .env
# Edit .env with your credentials
```

#### **"Tests timing out"**
- Increase `api_timeout` in environment
- Check network connectivity
- Verify external API availability

### **Debug Mode**

Enable Postman Console for detailed logs:
1. View → Show Postman Console
2. Run tests and check console output

## 📊 **Advanced Usage**

### **Load Testing**
```bash
# Run 10 iterations with 2-second delays
./run_tests.sh -n 10 -d 2000

# Generate HTML report
./run_tests.sh -o html
```

### **Specific Test Categories**
```bash
# Run only health checks
./run_tests.sh -f "Health Checks"

# Run only chat completion tests
./run_tests.sh -f "Chat Completion"

# Run only error scenarios
./run_tests.sh -f "Error Scenarios"
```

### **CI/CD Integration**
```bash
# Generate JUnit XML for CI systems
./run_tests.sh -o junit

# Generate JSON results for processing
./run_tests.sh -o json
```

### **Remote API Testing**
```bash
# Test against staging environment
./run_tests.sh -u https://staging-api.yourcompany.com

# Test against production (be careful!)
./run_tests.sh -u https://api.yourcompany.com -f "Health Checks"
```

## 📈 **Interpreting Results**

### **Success Indicators**
- ✅ Green checkmarks in Postman
- ✅ "Tests completed successfully!" message
- ✅ Response times under thresholds
- ✅ Proper response structures

### **Failure Analysis**
- ❌ Red X marks indicate failures
- 📊 Check response times for performance issues
- 🔍 Review error messages for root causes
- 📋 Verify request/response formats

### **Performance Metrics**
- Response times should be < 1000ms for health checks
- Response times should be < 30000ms for chat completion
- Success rate should be 100% for properly configured tests

## 🔐 **Security Considerations**

### **Credential Management**
- Never commit real credentials to version control
- Use environment-specific configurations
- Rotate API keys regularly

### **Test Data**
- Use non-sensitive test messages
- Avoid personal information in test requests
- Clean up test data if persistent

## 📚 **Next Steps**

1. **Customize Tests**: Add your own test scenarios
2. **Automate**: Integrate with CI/CD pipelines
3. **Monitor**: Set up regular health checks
4. **Scale**: Use for load testing and performance monitoring

## 🆘 **Getting Help**

- **Postman Documentation**: https://learning.postman.com/
- **Newman CLI**: https://github.com/postmanlabs/newman
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Project Issues**: Create an issue in the repository

---

**Happy Testing!** 🎉