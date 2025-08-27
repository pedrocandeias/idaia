# Ollama 500 Error Troubleshooting Guide

## 🔍 **What the Error Means**
HTTP 500 errors from Ollama typically indicate **server-side issues**, most commonly:
- **Memory exhaustion** (most common)
- **Model crash** or instability
- **Resource conflicts**

## ⚡ **Quick Fixes**

### **1. Restart Ollama Service**
```bash
# Kill Ollama
pkill ollama

# Restart Ollama
ollama serve
```

### **2. Check System Memory**
```bash
free -h
```
If memory is low (< 500MB free), close other applications or try a smaller model.

### **3. Switch to Smaller Model**
In VibeDesign AI Settings:
- Change from `llama3.1:8b` to `llama3.2:3b` (faster, uses less memory)
- Or try `phi3:mini` (very lightweight)

### **4. Clear Ollama Cache**
```bash
# Stop Ollama
pkill ollama

# Clear model cache (optional - will need to re-download models)
rm -rf ~/.ollama/models

# Restart and re-download your model
ollama serve
ollama pull llama3.1:8b
```

## 🔧 **Recent Improvements**

VibeDesign now includes better error handling for Ollama issues:

### **Enhanced Error Messages**
- **500 errors**: "Ollama server error (500) - likely memory/resource issue. Try a smaller model or restart Ollama."
- **Timeout errors**: "Request timed out. Try increasing timeout in AI settings or using a faster model."
- **Connection errors**: "Could not connect to Ollama. Make sure Ollama is running: ollama serve"

### **Improved Memory Management**
- **Reduced conversation history** (5 messages max vs unlimited)
- **Increased timeout** (120s vs 60s)
- **Better retry logic** with exponential backoff
- **Automatic JSON cleanup** (handles markdown code blocks)

### **Retry Strategy**
- **2 retries** instead of 3 (reduces memory pressure)
- **Smart delays** (5s for server errors, 10s for rate limits)
- **Automatic fallback** to rule-based parser on failure

## 📊 **Memory Usage Solutions**

### **Check Current Usage**
```bash
# System memory
free -h

# Ollama process memory
ps aux | grep ollama | grep -v grep
```

### **If Memory is Low:**

#### **Option 1: Use Smaller Model**
```bash
ollama pull llama3.2:3b    # ~2GB vs 4.9GB
# OR
ollama pull phi3:mini      # ~2.3GB, very fast
```

#### **Option 2: Close Other Applications**
- Close web browsers
- Stop other AI applications
- Free up system resources

#### **Option 3: Increase Swap Space**
```bash
# Check current swap
swapon --show

# If needed, increase swap (advanced)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 🎯 **Model Recommendations**

| Model | Size | Speed | Quality | Memory Use | Best For |
|-------|------|-------|---------|------------|----------|
| `phi3:mini` | 2.3GB | ⚡⚡⚡ | ⭐⭐⭐ | Low | Low-memory systems |
| `llama3.2:3b` | 2GB | ⚡⚡ | ⭐⭐⭐⭐ | Low | Balanced performance |
| `qwen2.5:7b` | 4.4GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Medium | Good coding |
| `llama3.1:8b` | 4.9GB | ⚡ | ⭐⭐⭐⭐⭐ | High | Best quality |

## 🔄 **Testing Your Setup**

### **1. Test Ollama Directly**
```bash
curl -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 10}'
```

### **2. Test with VibeDesign**
1. Open VibeDesign
2. Enable AI mode
3. Try simple prompt: "create a small box"
4. Check console output for detailed error messages

### **3. Monitor Ollama Logs**
```bash
# In one terminal
ollama serve

# Watch for error messages during requests
```

## 🚨 **When to Restart Ollama**

Restart Ollama if you see:
- Multiple 500 errors in a row
- Very slow response times (>2 minutes)
- High memory usage by Ollama process
- "model crashed" or similar errors

## 💡 **Pro Tips**

1. **Use a dedicated terminal** for `ollama serve` to watch for errors
2. **Monitor system resources** with `htop` during AI requests
3. **Try simple prompts first** to verify Ollama is working
4. **Switch models** if one consistently fails
5. **Check VibeDesign console** for detailed error messages

## 🔍 **Debug Commands**

```bash
# Check Ollama status
ps aux | grep ollama

# Check available models
ollama list

# Check system resources
free -h
df -h

# Test model directly
ollama run llama3.1:8b "Say hello"

# Check network connectivity
curl http://localhost:11434/api/tags
```

## 📞 **Still Having Issues?**

If problems persist:
1. **Check your system specs** - Ollama needs sufficient RAM
2. **Try different models** - some work better than others
3. **Update Ollama** - `ollama --version` and update if needed
4. **Use fallback mode** - disable AI in VibeDesign for basic shapes
5. **Report issues** - include error messages and system info

---

**The improved VibeDesign error handling should now provide much clearer feedback about what's happening with Ollama!** 🚀