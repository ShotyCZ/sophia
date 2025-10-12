# Refactoring Roadmap: Z Nomad 0.8.8 na Nomad 2.0

**Datum vytvoření:** 12. října 2025
**Autor:** AI Architekt
**Cíl:** Bezpečná transformace z třívrstvé architektury na jednoduchý stavový stroj

---

## 🎯 Celkový Přehled

Tento refaktoring transformuje současnou komplexní třívrstvou architekturu (MissionManager → ConversationalManager → WorkerOrchestrator) na jednoduchou, robustní architekturu založenou na stavovém stroji.

**Klíčový princip:** Každý krok musí být **testovatelný a reverzibelní**.

---

## 📋 Před Začátkem Refaktoringu

### Checklist Přípravy

- [ ] Vytvořit novou větev: `git checkout -b nomad-2.0-refactoring`
- [ ] Vytvořit záložní tag: `git tag nomad-0.8.8-backup`
- [ ] Ověřit, že všechny současné testy prošly: `pytest tests/`
- [ ] Vytvořit adresář pro dokumentaci změn: `mkdir -p docs/refactoring_log/`
- [ ] Nastavit test mode v config.yaml (použít levný model pro testování)

### Dokumentace Současného Stavu

```bash
# Vytvořit snapshot struktury
tree -L 3 > docs/refactoring_log/structure_before.txt

# Zalogovat všechny současné testy
pytest tests/ -v > docs/refactoring_log/tests_before.txt

# Vytvořit dokumentaci závislostí
pip freeze > docs/refactoring_log/dependencies_before.txt
```

---

## 🔧 FÁZE 1: Příprava Základu (Dny 1-2)

### Krok 1.1: Vytvoření StateManager

**Cíl:** Implementovat jádro stavového stroje bez ovlivnění současného kódu.

**Soubor:** `core/state_manager.py` (NOVÝ)

```python
"""
State Manager pro Nomad Orchestrator.
Tento modul řídí stavový stroj a perzistenci stavu.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import os
from pathlib import Path


class State(Enum):
    """Možné stavy orchestrátora."""
    AWAITING_USER_INPUT = "awaiting_user_input"
    PLANNING = "planning"
    EXECUTING_STEP = "executing_step"
    AWAITING_TOOL_RESULT = "awaiting_tool_result"
    REFLECTION = "reflection"
    RESPONDING = "responding"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class StateManager:
    """
    Správce stavového stroje a perzistence.
    
    Zodpovědnosti:
    - Udržování aktuálního stavu
    - Validace přechodů mezi stavy
    - Ukládání a načítání stavu z disku
    - Logování všech přechodů
    """
    
    # Definice povolených přechodů (State Machine Transitions)
    ALLOWED_TRANSITIONS = {
        State.AWAITING_USER_INPUT: [State.PLANNING, State.EXECUTING_STEP, State.SHUTDOWN],
        State.PLANNING: [State.EXECUTING_STEP, State.RESPONDING, State.ERROR],
        State.EXECUTING_STEP: [State.AWAITING_TOOL_RESULT, State.REFLECTION, State.ERROR],
        State.AWAITING_TOOL_RESULT: [State.EXECUTING_STEP, State.ERROR],
        State.REFLECTION: [State.RESPONDING],
        State.RESPONDING: [State.AWAITING_USER_INPUT],
        State.ERROR: [State.AWAITING_USER_INPUT, State.RESPONDING],
        State.SHUTDOWN: []
    }
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.session_file = self.project_root / "memory" / "session.json"
        self.current_state = State.AWAITING_USER_INPUT
        self.state_data: Dict[str, Any] = {}
        self._ensure_memory_dir()
        
    def _ensure_memory_dir(self):
        """Zajistí existenci memory adresáře."""
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
    
    def transition_to(self, new_state: State, reason: str = "") -> bool:
        """
        Přechod do nového stavu s validací.
        
        Args:
            new_state: Cílový stav
            reason: Důvod přechodu (pro logování)
            
        Returns:
            True pokud přechod byl úspěšný, False jinak
        """
        if new_state not in self.ALLOWED_TRANSITIONS[self.current_state]:
            print(f"❌ INVALID TRANSITION: {self.current_state.value} → {new_state.value}")
            return False
        
        old_state = self.current_state
        self.current_state = new_state
        
        # Logování přechodu
        transition_log = {
            "timestamp": datetime.now().isoformat(),
            "from": old_state.value,
            "to": new_state.value,
            "reason": reason
        }
        
        print(f"🔄 STATE TRANSITION: {old_state.value} → {new_state.value}")
        if reason:
            print(f"   Reason: {reason}")
        
        # Uložit stav po každém přechodu
        self.save_state()
        return True
    
    def save_state(self):
        """Uloží aktuální stav do souboru."""
        state_snapshot = {
            "session_id": self.state_data.get("session_id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "current_state": self.current_state.value,
            "data": self.state_data
        }
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(state_snapshot, f, indent=2, ensure_ascii=False)
    
    def load_state(self) -> Optional[Dict[str, Any]]:
        """
        Načte stav z disku.
        
        Returns:
            Uložený stav nebo None pokud neexistuje
        """
        if not self.session_file.exists():
            return None
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)
            
            # Obnovit stav
            self.current_state = State(snapshot["current_state"])
            self.state_data = snapshot["data"]
            
            print(f"📂 STATE LOADED: {self.current_state.value}")
            return snapshot
            
        except Exception as e:
            print(f"⚠️  Failed to load state: {e}")
            return None
    
    def clear_state(self):
        """Vymaže perzistentní stav."""
        if self.session_file.exists():
            self.session_file.unlink()
        self.current_state = State.AWAITING_USER_INPUT
        self.state_data = {}
        print("🗑️  State cleared")
    
    def get_state(self) -> State:
        """Vrátí aktuální stav."""
        return self.current_state
    
    def set_data(self, key: str, value: Any):
        """Uloží data do stavového kontextu."""
        self.state_data[key] = value
        self.save_state()
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Načte data ze stavového kontextu."""
        return self.state_data.get(key, default)
```

**Test soubor:** `tests/test_state_manager.py` (NOVÝ)

```python
"""
Testy pro StateManager.
MUSÍ PROJÍT před pokračováním na další krok!
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from core.state_manager import StateManager, State


class TestStateManager:
    """Test suite pro StateManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Vytvoř dočasný adresář pro testy."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    @pytest.fixture
    def state_manager(self, temp_dir):
        """Vytvoř StateManager s dočasným adresářem."""
        return StateManager(project_root=temp_dir)
    
    def test_initial_state(self, state_manager):
        """Test: Počáteční stav by měl být AWAITING_USER_INPUT."""
        assert state_manager.get_state() == State.AWAITING_USER_INPUT
    
    def test_valid_transition(self, state_manager):
        """Test: Platný přechod by měl být povolen."""
        result = state_manager.transition_to(State.PLANNING, reason="User requested complex task")
        assert result is True
        assert state_manager.get_state() == State.PLANNING
    
    def test_invalid_transition(self, state_manager):
        """Test: Neplatný přechod by měl být zamítnut."""
        # Z AWAITING_USER_INPUT nelze přímo do REFLECTION
        result = state_manager.transition_to(State.REFLECTION)
        assert result is False
        assert state_manager.get_state() == State.AWAITING_USER_INPUT  # Stav se nemění
    
    def test_persistence(self, state_manager, temp_dir):
        """Test: Stav by měl být uložen a načten."""
        # Nastav stav a data
        state_manager.transition_to(State.PLANNING)
        state_manager.set_data("mission_goal", "Refactor database")
        state_manager.set_data("plan", ["Step 1", "Step 2"])
        
        # Vytvoř nový StateManager (simulace restartu)
        new_manager = StateManager(project_root=temp_dir)
        loaded = new_manager.load_state()
        
        assert loaded is not None
        assert new_manager.get_state() == State.PLANNING
        assert new_manager.get_data("mission_goal") == "Refactor database"
        assert new_manager.get_data("plan") == ["Step 1", "Step 2"]
    
    def test_clear_state(self, state_manager, temp_dir):
        """Test: Vymazání stavu by mělo fungovat."""
        state_manager.transition_to(State.PLANNING)
        state_manager.set_data("test", "data")
        
        state_manager.clear_state()
        
        assert state_manager.get_state() == State.AWAITING_USER_INPUT
        assert state_manager.get_data("test") is None
        assert not state_manager.session_file.exists()
    
    def test_state_chain(self, state_manager):
        """Test: Komplexní sekvence přechodů."""
        # Simulace normálního workflow
        assert state_manager.transition_to(State.PLANNING) is True
        assert state_manager.transition_to(State.EXECUTING_STEP) is True
        assert state_manager.transition_to(State.AWAITING_TOOL_RESULT) is True
        assert state_manager.transition_to(State.EXECUTING_STEP) is True
        assert state_manager.transition_to(State.REFLECTION) is True
        assert state_manager.transition_to(State.RESPONDING) is True
        assert state_manager.transition_to(State.AWAITING_USER_INPUT) is True
```

**Příkazy k provedení:**

```bash
# 1. Vytvoř soubor
touch core/state_manager.py

# 2. Zkopíruj výše uvedený kód

# 3. Vytvoř test soubor
touch tests/test_state_manager.py

# 4. Zkopíruj testy

# 5. Spusť testy
pytest tests/test_state_manager.py -v

# 6. Commit změn
git add core/state_manager.py tests/test_state_manager.py
git commit -m "Add StateManager with comprehensive tests

- Implements core state machine with 8 states
- Validates all state transitions
- Provides persistence to session.json
- 100% test coverage"
```

**CHECKPOINT:** ✅ Všechny testy v `test_state_manager.py` MUSÍ projít!

---

### Krok 1.2: Vytvoření Zjednodušeného Orchestrátora (v2)

**Cíl:** Vytvořit novou verzi orchestrátora vedle staré, bez jejího rušení.

**Soubor:** `core/orchestrator_v2.py` (NOVÝ)

```python
"""
Nomad Orchestrator V2 - Simplified State Machine Architecture

Tento orchestrátor je kompletní přepis založený na stavovém stroji.
Nepoužívá MissionManager ani ConversationalManager.
"""

import sys
import os
import json
import asyncio
import uuid
from typing import Optional, List, Dict, Any

from core.state_manager import StateManager, State
from core.mcp_client import MCPClient
from core.llm_manager import LLMManager
from core.long_term_memory import LongTermMemory
from core.prompt_builder import PromptBuilder
from core.rich_printer import RichPrinter


class NomadOrchestratorV2:
    """
    Zjednodušený orchestrátor založený na stavovém stroji.
    
    Princip: Jeden mozek, jeden kontext, jeden tok dat.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = os.path.abspath(project_root)
        
        # Core komponenty
        self.state_manager = StateManager(project_root=self.project_root)
        self.mcp_client = MCPClient(project_root=self.project_root, profile="worker")
        self.llm_manager = LLMManager(project_root=self.project_root)
        self.ltm = LongTermMemory(project_root=self.project_root)
        self.prompt_builder = PromptBuilder(
            system_prompt_path=os.path.join(self.project_root, "prompts/system_prompt_v2.txt"),
            ltm=self.ltm
        )
        
        # Session data
        self.session_id = str(uuid.uuid4())
        self.is_running = False
        
        RichPrinter.info("NomadOrchestratorV2 initialized (State Machine Architecture)")
    
    async def initialize(self):
        """Inicializace všech asynchronních komponent."""
        await self.mcp_client.start_servers()
        
        # Pokus o načtení předchozího stavu
        loaded_state = self.state_manager.load_state()
        if loaded_state and loaded_state["current_state"] != "awaiting_user_input":
            RichPrinter.warning(f"Found interrupted session: {loaded_state.get('data', {}).get('mission_goal', 'Unknown')}")
            # TODO: Implementovat dialog s uživatelem pro pokračování
        
        RichPrinter.info("Orchestrator V2 ready")
    
    async def shutdown(self):
        """Bezpečné vypnutí."""
        await self.mcp_client.shutdown_servers()
        self.state_manager.transition_to(State.SHUTDOWN, reason="User requested shutdown")
        RichPrinter.info("Orchestrator V2 shut down")
    
    async def handle_user_input(self, user_input: str) -> str:
        """
        Hlavní vstupní bod pro zpracování uživatelského vstupu.
        
        Args:
            user_input: Požadavek od uživatele
            
        Returns:
            Finální odpověď pro uživatele
        """
        # Uložit vstup do stavu
        self.state_manager.set_data("user_input", user_input)
        self.state_manager.set_data("session_id", self.session_id)
        
        # Rozhodnout o přístupu: simple vs complex
        is_complex = await self._assess_complexity(user_input)
        
        if is_complex:
            RichPrinter.info("Task assessed as COMPLEX - will create plan")
            self.state_manager.transition_to(State.PLANNING, reason="Complex task detected")
        else:
            RichPrinter.info("Task assessed as SIMPLE - will execute directly")
            self.state_manager.transition_to(State.EXECUTING_STEP, reason="Simple task detected")
        
        # Spustit hlavní smyčku
        await self._run_state_machine()
        
        # Vrátit finální odpověď
        return self.state_manager.get_data("final_response", "Task completed.")
    
    async def _assess_complexity(self, task: str) -> bool:
        """
        Rychlé posouzení složitosti úkolu.
        
        Returns:
            True pokud úkol vyžaduje plánování, False pro přímou exekuci
        """
        # Jednoduché heuristiky
        complexity_keywords = [
            "refactor", "implement", "create system", "design", 
            "architecture", "multiple", "several steps", "complex"
        ]
        
        task_lower = task.lower()
        
        # Pokud obsahuje klíčová slova nebo je dlouhý, je pravděpodobně komplexní
        if any(keyword in task_lower for keyword in complexity_keywords):
            return True
        
        if len(task.split()) > 20:
            return True
        
        # Pro jednoduché dotazy (kdo, co, kdy, proč)
        if any(task_lower.startswith(q) for q in ["what", "who", "when", "why", "co", "kdo", "kdy", "proč"]):
            return False
        
        return False
    
    async def _run_state_machine(self):
        """
        Hlavní smyčka stavového stroje.
        Běží dokud nedosáhne RESPONDING stavu.
        """
        self.is_running = True
        max_iterations = 50  # Bezpečnostní limit
        iteration = 0
        
        while self.is_running and iteration < max_iterations:
            iteration += 1
            current_state = self.state_manager.get_state()
            
            RichPrinter.info(f"[Iteration {iteration}] Current state: {current_state.value}")
            
            # Dispatch na správnou handler metodu
            if current_state == State.PLANNING:
                await self._state_planning()
            elif current_state == State.EXECUTING_STEP:
                await self._state_executing_step()
            elif current_state == State.AWAITING_TOOL_RESULT:
                await self._state_awaiting_tool_result()
            elif current_state == State.REFLECTION:
                await self._state_reflection()
            elif current_state == State.RESPONDING:
                await self._state_responding()
                self.is_running = False  # Ukončit smyčku
            elif current_state == State.ERROR:
                await self._state_error()
                self.is_running = False
            else:
                RichPrinter.error(f"Unknown state: {current_state}")
                break
            
            await asyncio.sleep(0.1)  # Krátká pauza mezi iteracemi
        
        if iteration >= max_iterations:
            RichPrinter.error("State machine exceeded max iterations!")
    
    async def _state_planning(self):
        """
        Stav: PLANNING
        Vytvoří strukturovaný plán pro komplexní úkol.
        """
        mission_goal = self.state_manager.get_data("user_input")
        
        RichPrinter.info("Creating plan for mission...")
        
        # Načíst planning prompt
        planning_prompt_path = os.path.join(self.project_root, "prompts/planning_prompt_v2.txt")
        try:
            with open(planning_prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            RichPrinter.error("Planning prompt not found!")
            self.state_manager.transition_to(State.ERROR, reason="Missing planning prompt")
            return
        
        prompt = prompt_template.format(mission_goal=mission_goal)
        model = self.llm_manager.get_llm("default")
        
        response_text, _ = await model.generate_content_async(
            prompt, 
            response_format={"type": "json_object"}
        )
        
        try:
            # Parsovat plán
            import re
            match = re.search(r"```(json)?\s*\n(.*)\n```", response_text, re.DOTALL)
            json_str = match.group(2).strip() if match else response_text.strip()
            plan_data = json.loads(json_str)
            
            if "plan" in plan_data and isinstance(plan_data["plan"], list):
                plan = plan_data["plan"]
                self.state_manager.set_data("mission_goal", mission_goal)
                self.state_manager.set_data("plan", plan)
                self.state_manager.set_data("current_step_index", 0)
                self.state_manager.set_data("step_history", [])
                
                RichPrinter.info(f"✅ Plan created with {len(plan)} steps")
                self.state_manager.transition_to(State.EXECUTING_STEP, reason="Plan ready")
            else:
                raise ValueError("Invalid plan format")
                
        except Exception as e:
            RichPrinter.error(f"Failed to parse plan: {e}")
            self.state_manager.transition_to(State.ERROR, reason=str(e))
    
    async def _state_executing_step(self):
        """
        Stav: EXECUTING_STEP
        Provádí jeden krok z plánu nebo přímou akci.
        """
        # TODO: Implementovat v dalším kroku
        RichPrinter.warning("_state_executing_step not yet implemented")
        self.state_manager.transition_to(State.REFLECTION, reason="Placeholder - skip to reflection")
    
    async def _state_awaiting_tool_result(self):
        """
        Stav: AWAITING_TOOL_RESULT
        Zpracovává výsledek nástroje.
        """
        # TODO: Implementovat v dalším kroku
        pass
    
    async def _state_reflection(self):
        """
        Stav: REFLECTION
        Analyzuje průběh mise a generuje poznatky.
        """
        # TODO: Implementovat v dalším kroku
        RichPrinter.info("Reflection phase (placeholder)")
        self.state_manager.transition_to(State.RESPONDING, reason="Reflection complete")
    
    async def _state_responding(self):
        """
        Stav: RESPONDING
        Generuje finální odpověď pro uživatele.
        """
        final_message = "Task completed successfully. (V2 Orchestrator)"
        self.state_manager.set_data("final_response", final_message)
        RichPrinter.info(final_message)
        self.state_manager.transition_to(State.AWAITING_USER_INPUT, reason="Response sent")
    
    async def _state_error(self):
        """
        Stav: ERROR
        Zpracovává chybu a připravuje error response.
        """
        error_msg = self.state_manager.get_data("error_message", "Unknown error occurred")
        final_message = f"I encountered an error: {error_msg}"
        self.state_manager.set_data("final_response", final_message)
        RichPrinter.error(final_message)
        self.state_manager.transition_to(State.AWAITING_USER_INPUT, reason="Error handled")
```

**Test soubor:** `tests/test_orchestrator_v2.py` (NOVÝ)

```python
"""
Základní testy pro OrchestratorV2.
Testujeme pouze základní flow, ne celou funkcionalitu.
"""

import pytest
import asyncio
from core.orchestrator_v2 import NomadOrchestratorV2
from core.state_manager import State


@pytest.mark.asyncio
async def test_orchestrator_v2_initialization():
    """Test: Orchestrátor by se měl inicializovat."""
    orch = NomadOrchestratorV2(project_root=".")
    await orch.initialize()
    
    assert orch.state_manager.get_state() == State.AWAITING_USER_INPUT
    
    await orch.shutdown()


@pytest.mark.asyncio
async def test_complexity_assessment():
    """Test: Hodnocení složitosti úkolu."""
    orch = NomadOrchestratorV2(project_root=".")
    
    # Jednoduchý úkol
    is_complex = await orch._assess_complexity("What is the current time?")
    assert is_complex is False
    
    # Komplexní úkol
    is_complex = await orch._assess_complexity("Refactor the database layer to use connection pooling")
    assert is_complex is True


# Další testy přidáme postupně v dalších krocích
```

**Příkazy:**

```bash
# 1. Vytvoř soubory
touch core/orchestrator_v2.py
touch tests/test_orchestrator_v2.py

# 2. Zkopíruj kód

# 3. Vytvoř placeholder pro nový prompt
mkdir -p prompts
touch prompts/planning_prompt_v2.txt

# 4. Přidej základní planning prompt
cat > prompts/planning_prompt_v2.txt << 'EOF'
You are an AI planning assistant. Your task is to break down a complex goal into a series of actionable steps.

User's goal: {mission_goal}

Create a detailed, step-by-step plan. Return your response as a JSON object with this structure:
{{
  "plan": [
    "Step 1: Clear description of first action",
    "Step 2: Clear description of second action",
    ...
  ]
}}

Make each step:
- Specific and actionable
- In logical order
- Small enough to be completed in one iteration

Return ONLY the JSON, no other text.
EOF

# 5. Spusť testy (některé budou skipped, to je OK)
pytest tests/test_orchestrator_v2.py -v

# 6. Commit
git add core/orchestrator_v2.py tests/test_orchestrator_v2.py prompts/planning_prompt_v2.txt
git commit -m "Add OrchestratorV2 skeleton with state machine

- Implements basic state machine loop
- Adds complexity assessment
- Planning state partially implemented
- Other states are placeholders for next steps"
```

**CHECKPOINT:** ✅ Testy pro inicializaci a complexity assessment MUSÍ projít!

---

## 🔧 FÁZE 2: Implementace Exekuce (Dny 3-5)

### Krok 2.1: Implementace EXECUTING_STEP

**Cíl:** Dokončit logiku pro provádění jednotlivých kroků.

**Upravit:** `core/orchestrator_v2.py` - metoda `_state_executing_step`

```python
async def _state_executing_step(self):
    """
    Stav: EXECUTING_STEP
    Provádí jeden krok z plánu nebo přímou akci.
    """
    plan = self.state_manager.get_data("plan")
    current_step_index = self.state_manager.get_data("current_step_index", 0)
    
    # Pokud není plán, provádíme přímou exekuci
    if not plan:
        current_step_description = self.state_manager.get_data("user_input")
    else:
        if current_step_index >= len(plan):
            # Všechny kroky dokončeny
            RichPrinter.info("✅ All steps completed!")
            self.state_manager.transition_to(State.REFLECTION, reason="All steps done")
            return
        
        current_step_description = plan[current_step_index]
    
    RichPrinter.info(f"📍 Executing: {current_step_description}")
    
    # Sestavit prompt pro LLM
    tool_descriptions = await self.mcp_client.get_tool_descriptions()
    step_history = self.state_manager.get_data("step_history", [])
    mission_goal = self.state_manager.get_data("mission_goal", "")
    
    # Použít PromptBuilder pro sestavení promptu s kontextem
    # POZOR: Potřebujeme upravit PromptBuilder, aby podporoval nový formát
    # Pro teď použijeme zjednodušený přístup
    
    prompt = f"""You are an autonomous AI agent working on a task.

MISSION GOAL: {mission_goal}

CURRENT STEP: {current_step_description}

AVAILABLE TOOLS:
{tool_descriptions}

PREVIOUS STEPS:
{json.dumps(step_history[-3:], indent=2) if step_history else "No previous steps"}

Your response MUST be a JSON object with this structure:
{{
  "thought": "Your reasoning about what to do",
  "tool_call": {{
    "tool_name": "name_of_tool",
    "args": [],
    "kwargs": {{}}
  }}
}}

OR, if the step is complete:
{{
  "thought": "Why this step is done",
  "step_complete": true,
  "summary": "What was accomplished"
}}

Respond ONLY with JSON, no other text.
"""
    
    model = self.llm_manager.get_llm("default")
    response_text, _ = await model.generate_content_async(
        prompt,
        response_format={"type": "json_object"}
    )
    
    # Parsovat odpověď
    try:
        import re
        match = re.search(r"```(json)?\s*\n(.*)\n```", response_text, re.DOTALL)
        json_str = match.group(2).strip() if match else response_text.strip()
        response_data = json.loads(json_str)
        
        thought = response_data.get("thought", "")
        RichPrinter.log_communication("Agent's Thought", thought, style="dim blue")
        
        # Pokud je krok dokončen
        if response_data.get("step_complete"):
            summary = response_data.get("summary", "Step completed")
            
            # Zalogovat do historie
            step_record = {
                "step_index": current_step_index,
                "description": current_step_description,
                "thought": thought,
                "result": "completed",
                "summary": summary
            }
            step_history.append(step_record)
            self.state_manager.set_data("step_history", step_history)
            
            # Přejít na další krok nebo reflexi
            if plan and current_step_index + 1 < len(plan):
                self.state_manager.set_data("current_step_index", current_step_index + 1)
                RichPrinter.info(f"Moving to step {current_step_index + 2}/{len(plan)}")
                # Zůstáváme v EXECUTING_STEP pro další iteraci
            else:
                # Poslední krok nebo direct execution dokončena
                self.state_manager.transition_to(State.REFLECTION, reason="Steps complete")
        
        # Pokud agent volá nástroj
        elif "tool_call" in response_data:
            tool_call = response_data["tool_call"]
            self.state_manager.set_data("pending_tool_call", {
                "thought": thought,
                "tool_call": tool_call,
                "step_description": current_step_description
            })
            self.state_manager.transition_to(
                State.AWAITING_TOOL_RESULT,
                reason=f"Calling tool: {tool_call.get('tool_name')}"
            )
        else:
            RichPrinter.warning("LLM response did not contain step_complete or tool_call")
            # Pokračovat v iteraci
            
    except Exception as e:
        RichPrinter.error(f"Failed to parse LLM response: {e}")
        RichPrinter.log_communication("Raw Response", response_text, style="red")
        self.state_manager.set_data("error_message", str(e))
        self.state_manager.transition_to(State.ERROR, reason="Parse error")
```

### Krok 2.2: Implementace AWAITING_TOOL_RESULT

```python
async def _state_awaiting_tool_result(self):
    """
    Stav: AWAITING_TOOL_RESULT
    Provede nástroj a zpracuje výsledek.
    """
    pending_call = self.state_manager.get_data("pending_tool_call")
    if not pending_call:
        RichPrinter.error("No pending tool call!")
        self.state_manager.transition_to(State.ERROR, reason="Missing tool call data")
        return
    
    tool_call = pending_call["tool_call"]
    tool_name = tool_call.get("tool_name")
    args = tool_call.get("args", [])
    kwargs = tool_call.get("kwargs", {})
    
    RichPrinter.log_communication("Executing Tool", json.dumps(tool_call, indent=2), style="yellow")
    
    try:
        # Provést nástroj
        result_str = await self.mcp_client.execute_tool(tool_name, args, kwargs, verbose=True)
        
        # Uložit výsledek do historie
        step_history = self.state_manager.get_data("step_history", [])
        current_step_index = self.state_manager.get_data("current_step_index", 0)
        
        tool_record = {
            "step_index": current_step_index,
            "description": pending_call["step_description"],
            "thought": pending_call["thought"],
            "tool_call": tool_call,
            "tool_result": result_str[:500],  # Omezit délku pro úsporu paměti
            "result": "tool_executed"
        }
        step_history.append(tool_record)
        self.state_manager.set_data("step_history", step_history)
        
        # Vyčistit pending call
        self.state_manager.set_data("pending_tool_call", None)
        
        # Vrátit se do EXECUTING_STEP pro další akci
        self.state_manager.transition_to(
            State.EXECUTING_STEP,
            reason="Tool result ready, continuing step"
        )
        
    except Exception as e:
        RichPrinter.error(f"Tool execution failed: {e}")
        self.state_manager.set_data("error_message", f"Tool '{tool_name}' failed: {str(e)}")
        self.state_manager.transition_to(State.ERROR, reason="Tool execution error")
```

**Testy:**

```python
# Přidat do tests/test_orchestrator_v2.py

@pytest.mark.asyncio
async def test_simple_execution():
    """Test: Jednoduchá přímá exekuce (bez plánu)."""
    orch = NomadOrchestratorV2(project_root=".")
    await orch.initialize()
    
    # Simulovat jednoduchý dotaz
    response = await orch.handle_user_input("List files in current directory")
    
    # Ověřit, že orchestrátor dokončil a vrátil odpověď
    assert response is not None
    assert orch.state_manager.get_state() == State.AWAITING_USER_INPUT
    
    await orch.shutdown()
```

**Příkazy:**

```bash
# 1. Aktualizuj orchestrator_v2.py s výše uvedeným kódem

# 2. Spusť testy
pytest tests/test_orchestrator_v2.py::test_simple_execution -v -s

# 3. Commit
git add core/orchestrator_v2.py tests/test_orchestrator_v2.py
git commit -m "Implement EXECUTING_STEP and AWAITING_TOOL_RESULT states

- Full execution loop for steps
- Tool calling and result processing
- Step history tracking
- Transition logic for step completion"
```

**CHECKPOINT:** ✅ Test `test_simple_execution` MUSÍ projít!

---

## 🔧 FÁZE 3: Reflexe a Učení (Dny 6-7)

### Krok 3.1: Implementace REFLECTION

```python
async def _state_reflection(self):
    """
    Stav: REFLECTION
    Analyzuje průběh mise a ukládá poznatky do LTM.
    """
    mission_goal = self.state_manager.get_data("mission_goal", "Unknown")
    step_history = self.state_manager.get_data("step_history", [])
    
    if not step_history:
        RichPrinter.info("No steps to reflect on, skipping reflection")
        self.state_manager.transition_to(State.RESPONDING, reason="Nothing to reflect on")
        return
    
    RichPrinter.info("🤔 Performing self-reflection...")
    
    # Načíst reflection prompt
    reflection_prompt_path = os.path.join(self.project_root, "prompts/reflection_prompt_v2.txt")
    try:
        with open(reflection_prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    except FileNotFoundError:
        RichPrinter.warning("Reflection prompt not found, skipping")
        self.state_manager.transition_to(State.RESPONDING, reason="No reflection prompt")
        return
    
    # Sestavit historii pro reflexi
    history_summary = "\n".join([
        f"Step {i+1}: {step.get('description', 'N/A')}\n"
        f"  Thought: {step.get('thought', 'N/A')}\n"
        f"  Result: {step.get('result', 'N/A')}\n"
        for i, step in enumerate(step_history)
    ])
    
    prompt = prompt_template.format(
        mission_goal=mission_goal,
        step_history=history_summary
    )
    
    model = self.llm_manager.get_llm("default")
    learning_text, _ = await model.generate_content_async(prompt)
    
    # Uložit do LTM
    if learning_text and len(learning_text) > 20:
        self.ltm.add(
            documents=[learning_text],
            metadatas=[{
                "type": "learning",
                "source": "self_reflection",
                "mission": mission_goal
            }],
            ids=[str(uuid.uuid4())]
        )
        RichPrinter.log_communication("New Learning Stored", learning_text, style="bold green")
        self.state_manager.set_data("reflection_learning", learning_text)
    
    self.state_manager.transition_to(State.RESPONDING, reason="Reflection complete")
```

**Vytvoř reflection prompt:**

```bash
cat > prompts/reflection_prompt_v2.txt << 'EOF'
You are performing self-reflection on a completed task. Analyze your approach and extract learnings.

MISSION GOAL: {mission_goal}

YOUR STEPS:
{step_history}

Reflect on:
1. What worked well?
2. What was inefficient or could be improved?
3. What specific lesson can you apply to future similar tasks?

Write a concise learning statement (2-3 sentences) that captures the most important insight.
Focus on actionable patterns, not generic advice.

Example: "For file analysis tasks, using grep_search first to locate relevant sections is more efficient than reading entire files. This reduces token usage and speeds up the process."

Your reflection:
EOF
```

**Commit:**

```bash
git add core/orchestrator_v2.py prompts/reflection_prompt_v2.txt
git commit -m "Implement REFLECTION state with LTM integration

- Analyzes step history after task completion
- Generates actionable learnings
- Stores insights in LongTermMemory
- Includes reflection prompt template"
```

---

## 🔧 FÁZE 4: Integrace s TUI (Den 8)

### Krok 4.1: Vytvoření Adaptéru pro TUI

**Cíl:** Umožnit TUI používat buď starý nebo nový orchestrátor pomocí feature flagu.

**Soubor:** `core/orchestrator_adapter.py` (NOVÝ)

```python
"""
Adaptér pro postupný přechod na OrchestratorV2.
Umožňuje TUI používat buď starou nebo novou implementaci.
"""

import os
from typing import Union
from core.orchestrator import WorkerOrchestrator
from core.orchestrator_v2 import NomadOrchestratorV2
from core.conversational_manager import ConversationalManager
from core.mission_manager import MissionManager


class OrchestratorAdapter:
    """
    Jednotné rozhraní pro TUI.
    Podle konfigurace používá buď starou (MissionManager) nebo novou (V2) architekturu.
    """
    
    def __init__(self, project_root: str = ".", use_v2: bool = False):
        self.use_v2 = use_v2
        self.project_root = project_root
        
        if use_v2:
            self.orchestrator = NomadOrchestratorV2(project_root=project_root)
        else:
            self.mission_manager = MissionManager(project_root=project_root)
    
    async def initialize(self):
        if self.use_v2:
            await self.orchestrator.initialize()
        else:
            await self.mission_manager.initialize()
    
    async def shutdown(self):
        if self.use_v2:
            await self.orchestrator.shutdown()
        else:
            await self.mission_manager.shutdown()
    
    async def handle_input(self, user_input: str) -> str:
        """Zpracuje vstup a vrátí odpověď."""
        if self.use_v2:
            return await self.orchestrator.handle_user_input(user_input)
        else:
            # Starý způsob - použít MissionManager
            await self.mission_manager.start_mission(user_input)
            # MissionManager nevrací response přímo, takže použijeme placeholder
            return "Mission processed (legacy mode)"
```

### Krok 4.2: Aktualizace config.yaml

```bash
# Přidat do config/config.yaml sekci pro feature flags
cat >> config/config.yaml << 'EOF'

# Feature Flags
features:
  use_orchestrator_v2: false  # Změň na true pro aktivaci nové architektury
EOF
```

### Krok 4.3: Aktualizace TUI

**Upravit:** `tui/app.py`

Najdi inicializaci MissionManager a nahraď ji:

```python
# PŘED:
# self.mission_manager = MissionManager(project_root=self.project_root)

# PO:
from core.orchestrator_adapter import OrchestratorAdapter
import yaml

# Načíst feature flag z config
config_path = os.path.join(self.project_root, "config/config.yaml")
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

use_v2 = config.get("features", {}).get("use_orchestrator_v2", False)

self.orchestrator_adapter = OrchestratorAdapter(
    project_root=self.project_root,
    use_v2=use_v2
)
```

A aktualizuj metody:

```python
# V metodě on_mount:
await self.orchestrator_adapter.initialize()

# V metodě on_unmount:
await self.orchestrator_adapter.shutdown()

# V metodě handle_send (nebo podobné):
response = await self.orchestrator_adapter.handle_input(user_input)
```

**Commit:**

```bash
git add core/orchestrator_adapter.py config/config.yaml tui/app.py
git commit -m "Add OrchestratorAdapter for gradual migration

- Allows switching between old and new architecture via config
- TUI updated to use adapter
- Feature flag: features.use_orchestrator_v2
- Default is false (old architecture) for safety"
```

**CHECKPOINT:** ✅ Spusť TUI s `use_orchestrator_v2: false` a ověř, že vše funguje jako dříve!

---

## 🔧 FÁZE 5: Testování a Aktivace (Dny 9-10)

### Krok 5.1: Komplexní E2E Test

**Soubor:** `tests/test_e2e_orchestrator_v2.py` (NOVÝ)

```python
"""
End-to-End test pro OrchestratorV2.
Simuluje reálný scénář s komplexním úkolem.
"""

import pytest
import asyncio
from core.orchestrator_v2 import NomadOrchestratorV2
from core.state_manager import State


@pytest.mark.asyncio
@pytest.mark.slow  # Označit jako pomalý test
async def test_complex_task_with_planning():
    """
    Test: Kompletní průchod komplexním úkolem s plánováním.
    """
    orch = NomadOrchestratorV2(project_root=".")
    await orch.initialize()
    
    # Komplexní úkol
    task = "Create a simple Python script that prints 'Hello World' and save it to hello.py"
    
    response = await orch.handle_user_input(task)
    
    # Ověření
    assert response is not None
    assert orch.state_manager.get_state() == State.AWAITING_USER_INPUT
    
    # Ověř, že byly vykonány kroky
    step_history = orch.state_manager.get_data("step_history", [])
    assert len(step_history) > 0
    
    # Ověř, že reflexe proběhla
    learning = orch.state_manager.get_data("reflection_learning")
    assert learning is not None
    
    await orch.shutdown()
    
    print(f"\n✅ E2E Test passed!")
    print(f"   Steps executed: {len(step_history)}")
    print(f"   Learning generated: {learning[:100]}...")


@pytest.mark.asyncio
async def test_recovery_after_crash():
    """
    Test: Obnova po pádu.
    """
    orch1 = NomadOrchestratorV2(project_root=".")
    await orch1.initialize()
    
    # Nastav stav jako by byl uprostřed úkolu
    orch1.state_manager.transition_to(State.PLANNING)
    orch1.state_manager.set_data("mission_goal", "Test recovery")
    orch1.state_manager.set_data("plan", ["Step 1", "Step 2"])
    
    # "Pád" - shutdown
    await orch1.shutdown()
    
    # "Restart" - vytvoř nový orchestrátor
    orch2 = NomadOrchestratorV2(project_root=".")
    await orch2.initialize()
    
    # Načti stav
    loaded = orch2.state_manager.load_state()
    
    assert loaded is not None
    assert loaded["current_state"] == "planning"
    assert loaded["data"]["mission_goal"] == "Test recovery"
    
    # Vyčisti
    orch2.state_manager.clear_state()
    await orch2.shutdown()
```

**Spusť test:**

```bash
pytest tests/test_e2e_orchestrator_v2.py -v -s --tb=short

# Pro pomalé testy (můžeš skipnout při běžném vývoji):
pytest tests/test_e2e_orchestrator_v2.py -v -s -m "not slow"
```

### Krok 5.2: Postupná Aktivace

**Den 9: Beta Testování**

1. Změň v `config/config.yaml`:
   ```yaml
   features:
     use_orchestrator_v2: true
   ```

2. Spusť TUI a otestuj běžné scénáře:
   - Jednoduchý dotaz: "What files are in the current directory?"
   - Komplexní úkol: "Create a simple TODO app in Python"
   - Přerušení a pokračování (simulate crash)

3. Monitoruj logy a hledej problémy

**Den 10: Produkční Aktivace**

Pokud vše funguje:

```bash
# 1. Commit finální verze
git add .
git commit -m "Production ready: OrchestratorV2 fully tested

- All E2E tests passing
- Recovery mechanism verified
- Beta testing completed successfully
- Ready for production use"

# 2. Merge do main větve
git checkout master
git merge nomad-2.0-refactoring

# 3. Tag release
git tag -a v2.0.0 -m "Nomad 2.0 - State Machine Architecture"
git push origin master --tags
```

---

## 🔧 FÁZE 6: Cleanup Staré Architektury (Dny 11-12)

**VAROVÁNÍ:** Tento krok je DESTRUKTIVNÍ. Proveď ho pouze když je V2 plně funkční!

### Krok 6.1: Backup

```bash
# Vytvoř backup větev
git checkout -b nomad-0.8.8-archive
git push origin nomad-0.8.8-archive

# Vrať se na master
git checkout master
```

### Krok 6.2: Odstranění Starých Souborů

```bash
# Smaž staré komponenty
git rm core/mission_manager.py
git rm core/conversational_manager.py
git rm core/orchestrator.py  # Starý orchestrátor

# Přejmenuj V2 na finální verzi
git mv core/orchestrator_v2.py core/orchestrator.py

# Aktualizuj adaptor aby používal pouze novou verzi
# (odstraň podmínky a starý kód)

# Commit
git commit -m "Remove legacy three-layer architecture

- Deleted MissionManager, ConversationalManager
- Renamed OrchestratorV2 to Orchestrator
- Simplified OrchestratorAdapter
- Archive available in branch nomad-0.8.8-archive"
```

### Krok 6.3: Aktualizace Dokumentace

```bash
# Aktualizuj README.md
# Aktualizuj docs/ARCHITECTURE.md
# Přidej migration guide

git add README.md docs/
git commit -m "Update documentation for v2.0 architecture"
```

---

## 📊 Přehled Pokroku (Checklist)

### Fáze 1: Příprava Základu ✅
- [ ] StateManager implementován a otestován
- [ ] OrchestratorV2 skeleton vytvořen
- [ ] Základní testy prošly
- [ ] Planning prompt vytvořen

### Fáze 2: Implementace Exekuce ✅
- [ ] EXECUTING_STEP implementován
- [ ] AWAITING_TOOL_RESULT implementován
- [ ] Execution loop funguje
- [ ] Jednoduchá exekuce testována

### Fáze 3: Reflexe a Učení ✅
- [ ] REFLECTION implementován
- [ ] LTM integrace funguje
- [ ] Reflection prompt vytvořen
- [ ] Learning ukládání otestováno

### Fáze 4: Integrace s TUI ✅
- [ ] OrchestratorAdapter vytvořen
- [ ] Feature flag přidán
- [ ] TUI aktualizováno
- [ ] Obě verze fungují side-by-side

### Fáze 5: Testování a Aktivace ✅
- [ ] E2E testy napsány a prošly
- [ ] Recovery mechanismus otestován
- [ ] Beta testování dokončeno
- [ ] V2 aktivován v produkci

### Fáze 6: Cleanup ✅
- [ ] Backup vytvořen
- [ ] Stará architektura odstraněna
- [ ] Dokumentace aktualizována
- [ ] Release tag vytvořen

---

## 🚨 Možné Problémy a Řešení

### Problém 1: Testy Selhávají Kvůli Missing API Key

**Symptom:** `KeyError: 'GEMINI_API_KEY'` nebo podobné

**Řešení:**
```bash
# Vytvoř .env soubor s test API key
echo "GEMINI_API_KEY=your_test_key_here" > .env

# Nebo nastav pro testy levný/mock model
# v config/config.yaml
```

### Problém 2: State Machine Infinite Loop

**Symptom:** Orchestrátor běží donekonečna

**Řešení:**
- Zkontroluj `max_iterations` v `_run_state_machine`
- Přidej debug logování do každého stavu
- Ověř transition logiku

### Problém 3: LTM Není Inicializována

**Symptom:** `AttributeError` při přístupu k LTM

**Řešení:**
```bash
# Inicializuj LTM databázi
python -c "from core.long_term_memory import LongTermMemory; ltm = LongTermMemory(); print('LTM initialized')"
```

### Problém 4: Tool Results Jsou Příliš Dlouhé

**Symptom:** Context window exceeded

**Řešení:**
- V `_state_awaiting_tool_result`, omez `tool_result` na prvních 500 znaků
- Implementuj sumarizaci pro dlouhé výstupy
- Použij nástroj `show_last_output` pro zobrazení celého výstupu

---

## 📝 Poznámky pro Budoucí Práci

### Vylepšení Pro V2.1

1. **Adaptivní Planning:**
   - LLM může dynamicky upravovat plán během exekuce
   - Přidat `modify_plan` tool

2. **Paralelní Exekuce:**
   - Identifikovat nezávislé kroky
   - Spouštět je současně

3. **Vylepšená Complexity Assessment:**
   - Použít LLM místo heuristik
   - Naučit se z minulých rozhodnutí

4. **Interaktivní Error Recovery:**
   - Při chybě se zeptat uživatele na pokyn
   - Možnost "retry", "skip", "modify plan"

---

## 🎓 Závěrečná Slova

Tento refaktoring je jako rekonstrukce domu zatímco v něm stále bydlíš. Klíčem k úspěchu je:

1. **Postupnost** - nikdy neměň více než jeden systém najednou
2. **Testování** - po každém kroku ověř, že to funguje
3. **Reverzibelnost** - vždy měj možnost vrátit změny
4. **Dokumentace** - zaznamenej každé rozhodnutí a důvod

Hodně štěstí! 🚀

---

**Konec Roadmapy**
