# Improvement Ideas & Known Issues

## 🐛 Known Issues

### ~~Issue #1: LLM Tool Timeout Missing~~ ✅ RESOLVED
**Date:** 2025-10-29  
**Severity:** HIGH  
**Component:** `plugins/tool_llm.py`  
**Status:** **FIXED** (2025-10-29)

**Problem:**  
LLM calls had no timeout, causing WebUI to hang indefinitely when API was slow, incorrect model, or network issues.

**Solution Implemented:**  
Added `asyncio.wait_for()` wrapper around `litellm.acompletion()`:
```python
response = await asyncio.wait_for(
    litellm.acompletion(
        model=self.model, 
        messages=messages,
        timeout=30.0  # LiteLLM internal timeout
    ),
    timeout=35.0  # asyncio enforced timeout
)
```

**Tests Added:**  
- `test_llm_tool_timeout_handling` - Verifies timeout triggers correctly
- Updated `test_llm_tool_execute_with_config` - Includes timeout parameter

**Result:**  
WebUI now returns error message within 35 seconds instead of hanging indefinitely.

---

## 💡 Future Improvements

(Add improvement ideas below)
