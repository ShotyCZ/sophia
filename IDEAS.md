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

### Issue #2: Free Tier LLM API Instability
**Date:** 2025-10-29  
**Severity:** HIGH  
**Component:** `plugins/cognitive_planner.py`, OpenRouter Free Tier Models  
**Status:** **OPEN**

**Problem:**  
Free tier LLM models (Meta Llama 3.2 3B, Gemini 2.0 Flash Exp) frequently timeout after 35 seconds, causing:
- Poor user experience (long waits, "unable to create plan" errors)
- Every user message requires LLM call via planner
- Simple greetings like "ahoj" trigger full planning cycle
- API instability varies by time/load (sometimes 2s, sometimes >35s timeout)

**Impact:**  
- WebUI appears broken/non-responsive to users
- Simple conversations impossible
- User frustration and abandonment

**Current Architecture:**
```
User Input → Planner (LLM) → Execute Plan → Response
```
Every message goes through planner which calls LLM to generate JSON plan.

**Root Causes:**
1. Free tier models are overloaded/unreliable
2. Planning overhead for simple conversational messages
3. No fallback mechanism when LLM is unavailable
4. No direct chat mode for non-task messages

**Proposed Solutions:**

**Option A: Dual-Mode Architecture**
- Add `cognitive_chat` plugin for simple conversations
- Use planner only for explicit tasks (keywords: "create", "read", "execute", "analyze")
- Fallback: If planner LLM fails, route to chat mode

**Option B: Paid Tier Migration**
- Use reliable paid API (Claude, GPT-4) for production
- Keep free tier for development only
- Cost: ~$0.01-0.05 per conversation

**Option C: Local LLM Integration**
- Run small local model (Llama 3.2 1B) for planning
- Use cloud LLM only for complex reasoning
- Requires: GPU or CPU optimization

**Option D: Smart Planning**
- Classify input intent first (fast regex/small model)
- Skip planning for greetings, simple questions
- Full planning only for action requests

**Recommended:** **Option D** (short term) + **Option A** (medium term)

**Implementation Notes:**
- Must comply with AGENTS.md Rule #1 (no core modifications)
- Solution must be plugin-based
- Tests required before deployment

**Workaround:**  
Currently users must wait 35s for timeout, then retry. Sometimes works on 2nd/3rd attempt.

---

## 💡 Future Improvements

(Add improvement ideas below)
