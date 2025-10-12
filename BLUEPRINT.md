# Finální Architektonický Plán pro Nomáda 2.0

**Dokument:** Technický blueprint pro reimplementaci
**Datum:** 12. října 2025
**Účel:** Definovat jasnou, jednoduchou a robustní architekturu pro novou verzi

---

## 1. Hlavní Cíl

> **Vytvořit autonomního AI softwarového inženýra, který je schopen:**
> - Samostatně rozložit komplexní úkol na podúkoly
> - Provést implementaci pomocí dostupných nástrojů
> - Udržet kontext a pokračovat po restartu
> - Učit se ze svých zkušeností
> - Autonomně se zdokonalovat (včetně úpravy vlastního kódu)

---

## 2. Klíčové Principy Návrhu

### 2.1. Jednoduchost (Simplicity First)
**Princip:** Žádné zbytečné vrstvy. Jeden centrální orchestrátor je jediným "mozkem" systému.

**Důsledky:**
- Jeden hlavní proces řídí vše.
- Žádné "Manager", "Dispatcher", "Coordinator" vrstvy.
- Všechny rozhodovací pravomoci jsou v jednom místě.

### 2.2. Stavovost (Explicit State Machine)
**Princip:** Orchestrátor je stavový stroj. Vždy ví, v jakém stavu se nachází, a může tento stav uložit a obnovit.

**Důsledky:**
- Jasně definované stavy (PLANNING, EXECUTING, REFLECTING, atd.).
- Každý přechod mezi stavy je explicitní a logovaný.
- Stav je perzistentní - po pádu lze pokračovat.

### 2.3. Robustnost (Resilience by Design)
**Princip:** Datové toky jsou jednoduché, předvídatelné a bez skrytých závislostí.

**Důsledky:**
- Žádná fragmentace kontextu mezi vrstvami.
- Historie kroků je vždy dostupná pro reflexi.
- Chyby jsou zachytávány a řešeny lokálně, ne propagovány nahoru.

---

## 3. Cílová Architektura: "Jeden Mozek - Stavový Stroj"

### 3.1. Koncepční Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         UŽIVATELSKÉ ROZHRANÍ                        │
│                              (TUI)                                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      NOMAD ORCHESTRATOR                             │
│                     (Centrální Mozek)                               │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │              STAVOVÝ STROJ (State Machine)                │    │
│  │                                                           │    │
│  │  • AWAITING_USER_INPUT    → Čeká na pokyn                │    │
│  │  • PLANNING               → Generuje plán kroků           │    │
│  │  • EXECUTING_STEP         → Provádí jeden krok            │    │
│  │  • AWAITING_TOOL_RESULT   → Čeká na výsledek nástroje     │    │
│  │  • REFLECTION             → Analyzuje výkon               │    │
│  │  • RESPONDING             → Formuje odpověď               │    │
│  │                                                           │    │
│  └───────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │              PERZISTENTNÍ STAV                            │    │
│  │                                                           │    │
│  │  • current_state: EXECUTING_STEP                          │    │
│  │  • mission_goal: "Refactor database layer"               │    │
│  │  • plan: [ "Step 1", "Step 2", ... ]                     │    │
│  │  • current_step_index: 3                                  │    │
│  │  • step_history: [ {...}, {...}, ... ]                   │    │
│  │                                                           │    │
│  └───────────────────────────────────────────────────────────┘    │
└─────────────┬───────────────────────────────────────┬───────────────┘
              │                                       │
              ▼                                       ▼
┌──────────────────────────┐           ┌──────────────────────────────┐
│   MCP NÁSTROJE           │           │  DLOUHODOBÁ PAMĚŤ (LTM)     │
│   (Tools Servers)        │           │  (Poučení & Historie)        │
│                          │           │                              │
│ • file_system_server     │           │ • Vektorová databáze         │
│ • shell_server           │           │ • Reflexe z minulých úkolů   │
│ • git_server             │           │ • Naučené postupy            │
│ • code_analysis_server   │           │                              │
└──────────────────────────┘           └──────────────────────────────┘
```

### 3.2. Centrální Orchestrátor: `NomadOrchestrator`

**Soubor:** `core/orchestrator.py`

**Zodpovědnosti:**
1. **Příjem úkolu od uživatele** (přes TUI).
2. **Rozhodnutí o přístupu:** Jednoduchý úkol (direct execution) vs. komplexní úkol (plánování).
3. **Generování plánu** (pokud je potřeba).
4. **Exekuce kroků** (volání nástrojů).
5. **Správa stavu** (ukládání po každém kroku).
6. **Sebereflexe** (po dokončení mise).
7. **Generování odpovědi** pro uživatele.

**Klíčové metody:**
```python
class NomadOrchestrator:
    def __init__(self, project_root: str):
        self.state_manager = StateManager()  # Správce stavu
        self.mcp_client = MCPClient()        # Přístup k nástrojům
        self.llm = LLMManager()              # LLM rozhraní
        self.ltm = LongTermMemory()          # Dlouhodobá paměť
        
    async def handle_user_input(self, user_input: str):
        """Hlavní vstupní bod pro komunikaci s uživatelem."""
        
    async def run(self):
        """Hlavní smyčka stavového stroje."""
        
    async def transition_to(self, new_state: State):
        """Přechod do nového stavu s perzistencí."""
        
    async def _state_planning(self):
        """Logika pro stav PLANNING."""
        
    async def _state_executing_step(self):
        """Logika pro stav EXECUTING_STEP."""
        
    async def _state_reflection(self):
        """Logika pro stav REFLECTION."""
```

---

## 4. Stavový Stroj: Detailní Definice

### Stav 1: AWAITING_USER_INPUT
**Popis:** Orchestrátor čeká na vstup od uživatele.

**Možné přechody:**
- Uživatel zadá úkol → `PLANNING` nebo `EXECUTING_STEP` (podle složitosti)
- Uživatel ukončí session → `SHUTDOWN`

**Perzistovaná data:**
- `current_state = "AWAITING_USER_INPUT"`

---

### Stav 2: PLANNING
**Popis:** Orchestrátor analyzuje komplexní úkol a generuje strukturovaný seznam kroků.

**Co se děje:**
1. LLM dostane `mission_goal` a systémový prompt s instrukcemi pro plánování.
2. LLM vrátí seznam kroků ve formátu:
   ```json
   {
     "plan": [
       "Analyzovat současnou strukturu databázové vrstvy",
       "Identifikovat duplicitní kód",
       "Navrhnout novou architekturu",
       "Implementovat refactored verzi",
       "Spustit testy"
     ]
   }
   ```
3. Orchestrátor uloží plán do `state.plan`.

**Možné přechody:**
- Plán úspěšně vytvořen → `EXECUTING_STEP`
- Selhání generování plánu → `RESPONDING` (s chybovou zprávou)

**Perzistovaná data:**
```json
{
  "current_state": "PLANNING",
  "mission_goal": "Refactor database layer",
  "plan": [...],
  "current_step_index": 0
}
```

---

### Stav 3: EXECUTING_STEP
**Popis:** Orchestrátor provádí jeden konkrétní krok z plánu.

**Co se děje:**
1. Načte aktuální krok: `current_step = state.plan[state.current_step_index]`.
2. Sestaví prompt pro LLM s instrukcemi: "Tvým úkolem je provést tento krok: {current_step}. Máš k dispozici následující nástroje: {tools}."
3. LLM analyzuje krok a rozhodne se, který nástroj použít.
4. Orchestrátor přechází do `AWAITING_TOOL_RESULT`.

**Možné přechody:**
- Nástroj je vybrán → `AWAITING_TOOL_RESULT`
- Krok je označen jako dokončený (LLM vrátí `step_complete`) → kontrola:
  - Jsou další kroky? → `EXECUTING_STEP` (inkrementace `current_step_index`)
  - Není další krok? → `REFLECTION`

**Perzistovaná data:**
```json
{
  "current_state": "EXECUTING_STEP",
  "mission_goal": "...",
  "plan": [...],
  "current_step_index": 2,
  "step_history": [
    {
      "step_number": 1,
      "description": "Analyzovat současnou strukturu",
      "tool_calls": [...],
      "result": "completed"
    },
    ...
  ]
}
```

---

### Stav 4: AWAITING_TOOL_RESULT
**Popis:** Orchestrátor čeká na dokončení volání nástroje.

**Co se děje:**
1. Nástroj je proveden (např. `read_file`, `run_command`).
2. Výsledek je zalogován do `step_history`.
3. Orchestrátor vrací kontext LLM: "Výsledek nástroje: {result}. Co dál?"

**Možné přechody:**
- Nástroj vrátil výsledek → zpět do `EXECUTING_STEP` (LLM pokračuje v práci na aktuálním kroku)
- Chyba nástroje → `EXECUTING_STEP` (s chybovou zprávou pro LLM, který se pokusí problém vyřešit)

**Perzistovaná data:**
```json
{
  "current_state": "AWAITING_TOOL_RESULT",
  "last_tool_call": {
    "tool": "read_file",
    "args": {"filepath": "core/database.py"},
    "result": "pending"
  }
}
```

---

### Stav 5: REFLECTION
**Popis:** Orchestrátor analyzuje průběh celé mise a generuje poznatky.

**Co se děje:**
1. Načte kompletní `step_history` a `mission_goal`.
2. Sestaví prompt pro reflexi:
   ```
   "Analyzuj následující serii kroků, které jsi provedl pro dosažení cíle '{mission_goal}'.
   Identifikuj:
   - Co fungovalo dobře?
   - Co bylo neefektivní?
   - Jaké poučení si z toho odnášíš pro budoucnost?
   
   Historie kroků: {step_history}"
   ```
3. LLM vrátí textový poznatek.
4. Poznatek je uložen do LTM s metadatem `{"type": "learning"}`.

**Možné přechody:**
- Reflexe dokončena → `RESPONDING`

**Perzistovaná data:**
```json
{
  "current_state": "REFLECTION",
  "reflection_result": "Pro analýzu kódu je efektivnější nejprve použít grep_search než číst celé soubory..."
}
```

---

### Stav 6: RESPONDING
**Popis:** Orchestrátor formuje finální odpověď pro uživatele.

**Co se děje:**
1. Shrne výsledek mise (úspěch/neúspěch).
2. Vygeneruje uživatelsky přívětivou zprávu (v češtině).
3. Uvede seznam upravených souborů (pokud nějaké jsou).
4. Odešle zprávu do TUI.

**Možné přechody:**
- Odpověď odeslána → `AWAITING_USER_INPUT`

**Perzistovaná data:**
```json
{
  "current_state": "RESPONDING",
  "final_message": "Dokončil jsem refactoring databázové vrstvy. Upravené soubory: core/database.py, tests/test_database.py"
}
```

---

## 5. Perzistence Stavu

### 5.1. Mechanismus
Orchestrátor po každém přechodu stavu (a po každém kroku) uloží svůj aktuální stav do souboru:

**Cesta:** `memory/session.json`

**Struktura:**
```json
{
  "session_id": "uuid-1234-5678",
  "timestamp": "2025-10-12T14:30:00Z",
  "current_state": "EXECUTING_STEP",
  "mission_goal": "Refactor database layer to use connection pooling",
  "plan": [
    "Krok 1: Analyzovat současnou implementaci",
    "Krok 2: Navrhnout connection pool architekturu",
    "Krok 3: Implementovat změny",
    "Krok 4: Aktualizovat testy",
    "Krok 5: Spustit kompletní test suite"
  ],
  "current_step_index": 2,
  "step_history": [
    {
      "step_number": 1,
      "description": "Analyzovat současnou implementaci",
      "thought_process": "Musím načíst soubor core/database.py a identifikovat současný způsob připojení...",
      "tool_calls": [
        {"tool": "read_file", "args": {"filepath": "core/database.py"}, "result": "...obsah..."}
      ],
      "result": "completed",
      "timestamp": "2025-10-12T14:25:00Z"
    },
    {
      "step_number": 2,
      "description": "Navrhnout connection pool architekturu",
      "thought_process": "Na základě analýzy navrhuji použít SQLAlchemy pooling...",
      "tool_calls": [],
      "result": "in_progress",
      "timestamp": "2025-10-12T14:28:00Z"
    }
  ],
  "total_tokens_used": 15420,
  "touched_files": ["core/database.py"]
}
```

### 5.2. Obnova po Pádu
Při startu orchestrátor:
1. Zkontroluje, zda existuje `memory/session.json`.
2. Pokud ano a `current_state != "AWAITING_USER_INPUT"`:
   - Načte stav.
   - Zobrazí uživateli: "Detekoval jsem přerušenou misi: '{mission_goal}'. Byl jsem v kroku {current_step_index} z {len(plan)}. Chceš pokračovat?"
   - Pokud ano → pokračuje od `current_state`.
   - Pokud ne → smaže session a začne znovu.

---

## 6. Adresářová Struktura a Klíčové Soubory

```
sophia/
├── core/                           # Jádro systému
│   ├── orchestrator.py             # ⭐ NomadOrchestrator (hlavní mozek)
│   ├── state_manager.py            # Správa a perzistence stavů
│   ├── llm_manager.py              # Rozhraní pro komunikaci s LLM
│   ├── prompt_builder.py           # Sestavování promptů (se znalostmi z LTM)
│   ├── mcp_client.py               # Klient pro MCP nástroje
│   ├── long_term_memory.py         # Dlouhodobá paměť (LTM)
│   └── cost_manager.py             # Sledování nákladů na LLM volání
│
├── mcp_servers/                    # MCP Nástroje
│   ├── file_system_server.py      # Práce se soubory
│   ├── shell_server.py             # Spouštění příkazů
│   ├── git_server.py               # Git operace
│   ├── code_analysis_server.py    # Analýza kódu (pylint, radon)
│   └── planning_helpers_server.py # Pomocné nástroje pro plánování
│
├── prompts/                        # Systémové prompty
│   ├── system_prompt.txt           # ⭐ Hlavní prompt pro orchestrátora
│   ├── planning_prompt.txt         # Prompt pro generování plánů
│   └── reflection_prompt.txt       # Prompt pro sebereflexe
│
├── memory/                         # Perzistentní data
│   ├── session.json                # ⭐ Aktuální stav orchestrátora
│   ├── ltm.db                      # Dlouhodobá paměť (ChromaDB nebo similar)
│   └── logs/                       # Logy
│
├── tui/                            # Textové uživatelské rozhraní
│   └── app.py                      # TUI aplikace (Textual)
│
├── tests/                          # Testy
│   ├── test_orchestrator.py       # Testy hlavní logiky
│   ├── test_state_machine.py      # Testy přechodů stavů
│   └── test_recovery.py            # Testy obnovy po pádu
│
├── config/
│   └── config.yaml                 # Konfigurace (LLM modely, API klíče)
│
├── main.py                         # Hlavní vstupní bod
└── requirements.in                 # Závislosti
```

---

## 7. Klíčové Změny Oproti Současnému Stavu

| Co ODSTRAŇUJEME | Proč |
|----------------|------|
| `MissionManager` | Zbytečná vrstva. Orchestrátor zvládne plánování sám. |
| `ConversationalManager` | Zbytečný dispatcher. Orchestrátor komunikuje přímo s TUI. |
| Rozdělení na "Manager" a "Worker" profily | Všechny nástroje jsou dostupné orchestrátorovi, ale systémový prompt jasně definuje, jak je používat. |
| `PlanningServer` a `ReflectionServer` jako samostatné MCP servery | Plánování a reflexe jsou interní metody orchestrátora, ne externí nástroje. |

| Co PŘIDÁVÁME | Proč |
|--------------|------|
| `StateManager` | Explicitní správa stavového stroje. |
| `memory/session.json` | Perzistence stavu pro obnovu po pádu. |
| Jasně definované stavy v orchestrátoru | Transparentnost a predictability. |
| Recovery logika při startu | Odolnost proti pádům. |

| Co ZACHOVÁVÁME | Proč |
|----------------|------|
| MCP architektura pro nástroje | Je správná a modulární. |
| `LongTermMemory` (LTM) | Klíčová pro učení. |
| `PromptBuilder` s LTM integrací | Funguje dobře. |
| TUI s Textual | Není důvod měnit. |

---

## 8. Implementační Plán (Pro Budoucí Práci)

### Fáze 1: Základ (MVP)
1. Vytvořit `core/state_manager.py` s definicí stavů a perzistencí do `session.json`.
2. Refaktorovat `core/orchestrator.py`:
   - Odstranit závislost na `MissionManager` a `ConversationalManager`.
   - Implementovat stavový stroj s metodami `_state_planning`, `_state_executing_step`, atd.
   - Implementovat hlavní smyčku `run()`.
3. Upravit `main.py` a `tui/app.py`:
   - Odstranit inicializaci starých manažerů.
   - Vytvořit pouze `NomadOrchestrator` a předat mu vstup z TUI.
4. Aktualizovat `prompts/system_prompt.txt`:
   - Jasně definovat role a pravidla.
   - Instruovat LLM, aby při plánování vracel strukturovaný JSON.
   - Instruovat LLM, aby signalizoval dokončení kroku pomocí speciální odpovědi.

### Fáze 2: Perzistence a Recovery
1. Implementovat ukládání stavu po každém kroku.
2. Implementovat logiku obnovy při startu.
3. Otestovat scénář přerušení a pokračování.

### Fáze 3: Reflexe a Učení
1. Implementovat `_state_reflection()`.
2. Propojit s LTM.
3. Ověřit, že poznatky jsou skutečně aplikovány v budoucích úkolech.

### Fáze 4: End-to-End Test
1. Zadat komplexní úkol: "Analyzuj svůj stavový stroj a navrhni vylepšení".
2. Ověřit, že agent dokáže úkol rozložit, provést a poučit se.

---

## 9. Očekávané Výhody

Po implementaci tohoto blueprintu bude Nomád 2.0:

✅ **Jednodušší:** Jedna třída místo tří vrstev.
✅ **Robustnější:** Explicitní stav, který lze uložit a obnovit.
✅ **Transparentnější:** Každý přechod stavu je logovaný a pochopitelný.
✅ **Schopnější učení:** Reflexe má přístup ke kompletní historii, ne fragmentům.
✅ **Odolný proti pádům:** Po restartu může pokračovat, odkud skončil.
✅ **Skutečně autonomní:** Může upravovat vlastní kód bez architektonických překážek.

---

**Konec dokumentu**

Tento blueprint představuje návrat k principům jednoduchosti a robustnosti. Je to reaktivní návrh, který se poučil ze všech předchozích chyb a poskytuje jasnou cestu vpřed.
