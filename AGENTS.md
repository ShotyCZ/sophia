# 🤖 Manuál pro AI Agenta: Jules (Nomad) V2# 🤖 Manuál pro AI Agenta: Jules (Nomad)



**Verze:** 2.0  **Verze:** 1.1

**Datum:** 2025-10-12  **Datum:** 2025-09-29

**Aktualizace:** Přidána dokumentace NomadOrchestratorV2 architektury

Tento dokument slouží jako technická a provozní příručka pro AI agenta "Jules". Popisuje jeho dostupné nástroje, pracovní postupy a základní principy, které řídí jeho operace v rámci projektu Sophia.

Tento dokument slouží jako **ZÁVAZNÁ** technická a provozní příručka pro AI agenty pracující na projektu Sophia/Nomad. Popisuje dostupné nástroje, pracovní postupy, architekturu a základní principy.

---

---

## 1. Přehled Nástrojů (Tool Reference)

## 📋 Table of Contents

Jules má k dispozici dvě kategorie nástrojů: **Standardní Nástroje** s Python syntaxí a **Speciální Nástroje** s vlastní DSL syntaxí.

1. [Přehled Projektu](#1-přehled-projektu)

2. [Architektura NomadOrchestratorV2](#2-architektura-nomadorchestratorv2)### 1.1. Standardní Nástroje

3. [Přehled Nástrojů](#3-přehled-nástrojů)

4. [Pracovní Postup](#4-pracovní-postup)Tyto nástroje se volají pomocí standardní syntaxe funkce v Pythonu.

5. [Testování](#5-testování)

6. [Základní Principy](#6-základní-principy)- **`list_files(path: str = ".") -> list[str]`**

7. [Git Workflow](#7-git-workflow)  - **Popis:** Vypíše soubory a adresáře v zadané cestě. Adresáře jsou označeny lomítkem (`/`).

  - **Parametry:**

---    - `path` (str, volitelný): Cesta k adresáři. Výchozí je `sandbox/`. Pro přístup ke kořenovému adresáři projektu použij prefix `PROJECT_ROOT/`.



## 1. Přehled Projektu- **`read_file(filepath: str) -> str`**

  - **Popis:** Přečte a vrátí obsah zadaného souboru.

### 1.1 Co je Sophia/Nomad?  - **Parametry:**

    - `filepath` (str): Cesta k souboru. Výchozí je `sandbox/`. Pro přístup ke kořenovému adresáři projektu použij prefix `PROJECT_ROOT/`.

**Sophia/Nomad** je pokročilá AI orchestrace platforma s autonomním agentním systémem. Klíčové vlastnosti:

- **`delete_file(filepath: str) -> str`**

- **Stavově řízený orchestrátor** (NomadOrchestratorV2)  - **Popis:** Smaže zadaný soubor.

- **Crash-resilience** s automatickým recovery  - **Parametry:**

- **Proaktivní plánování** s dependency tracking    - `filepath` (str): Cesta k souboru, který se má smazat. Výchozí je `sandbox/`.

- **Adaptivní učení** z chyb

- **Budget tracking** pro cost management- **`rename_file(filepath: str, new_filepath: str) -> str`**

- **157 passing tests** (100% pass rate)  - **Popis:** Přejmenuje nebo přesune soubor.

  - **Parametry:**

### 1.2 Aktuální Stav (Říjen 2025)    - `filepath` (str): Původní cesta k souboru.

    - `new_filepath` (str): Nová cesta k souboru.

**✅ DOKONČENO (Den 1-10):**

- StateManager (23 tests) ✅- **`set_plan(plan: str) -> None`**

- RecoveryManager (18 tests) ✅  - **`plan_step_complete(message: str) -> None`**

- PlanManager (19 tests) ✅- **`message_user(message: str, continue_working: bool) -> None`**

- ReflectionEngine (21 tests) ✅- **`request_user_input(message: str) -> None`**

- BudgetTracker (26 tests) ✅- **`request_code_review() -> str`**

- NomadOrchestratorV2 (50 tests) ✅- **`submit(...)`**



**🔄 V PLÁNU (Den 11-12):**### 1.2. Speciální Nástroje

- Real LLM E2E testing

- Performance optimizationTyto nástroje používají specifickou DSL syntaxi, kde je název nástroje na prvním řádku a argumenty na dalších.

- Production deployment

- **`run_in_bash_session`**

---  - **Popis:** Spustí příkaz v perzistentní bash session.

  - **Syntax:**

## 2. Architektura NomadOrchestratorV2    ```

    run_in_bash_session

### 2.1 State Machine    <příkaz k provedení>

    ```

Orchestrátor funguje jako stavový stroj s 8 stavy:

- **`create_file_with_block`**

```  - **Popis:** Vytvoří nový soubor a zapíše do něj zadaný obsah. Pokud soubor již existuje, bude přepsán.

┌─────────────────────────────────────────────────────────────┐  - **Syntax:**

│                  NomadOrchestratorV2                        │    ```

│                    (State Machine)                          │    create_file_with_block

├─────────────────────────────────────────────────────────────┤    <cesta_k_souboru>

│  IDLE → PLANNING → EXECUTING → AWAITING → REFLECTION      │    <obsah souboru na více řádcích>

│           ↓           ↓            ↓           ↓            │    ```

│      ERROR ← ────────────────────────────── RESPONDING     │

│           ↓                                    ↓            │- **`overwrite_file_with_block`**

│         IDLE ←─────────────────────────→  COMPLETED        │  - **Popis:** Kompletně přepíše existující soubor novým obsahem. Jedná se o alias pro `create_file_with_block`.

└─────────────────────────────────────────────────────────────┘  - **Syntax:**

```    ```

    overwrite_file_with_block

**Stavy:**    <cesta_k_souboru>

- `IDLE` - Čekání na novou misi    <nový obsah souboru>

- `PLANNING` - Vytváření plánu pomocí PlanManager + LLM    ```

- `EXECUTING_STEP` - Provádění kroku (získání tool_call z LLM)

- `AWAITING_TOOL_RESULT` - Čekání na výsledek nástroje- **`replace_with_git_merge_diff`**

- `REFLECTION` - Analýza chyby + rozhodnutí o další akci  - **Popis:** Provede cílenou úpravu části souboru. Vyhledá `search_block` a nahradí jej `replace_block`.

- `RESPONDING` - Generování shrnutí mise  - **Syntax:**

- `COMPLETED` - Mise úspěšně dokončena    ```

- `ERROR` - Kritická chyba    replace_with_git_merge_diff

    <cesta_k_souboru>

### 2.2 Core Komponenty    <<<<<<< SEARCH

    <blok kódu k nalezení>

| Komponenta | Soubor | Účel |    =======

|------------|--------|------|    <blok kódu, kterým se nahradí nalezený blok>

| **StateManager** | `core/state_manager.py` | Stavový stroj s validovanými přechody |    >>>>>>> REPLACE

| **RecoveryManager** | `core/recovery_manager.py` | Crash detection & recovery |    ```

| **PlanManager** | `core/plan_manager.py` | Proaktivní plánování s dependencies |

| **ReflectionEngine** | `core/reflection_engine.py` | Učení z chyb (5 akcí) |---

| **BudgetTracker** | `core/budget_tracker.py` | Token & time tracking |

| **NomadOrchestratorV2** | `core/nomad_orchestrator_v2.py` | Main orchestrator |## 2. Pracovní Postup (Workflow)



### 2.3 Klíčové KonceptyJules funguje v cyklu, který je řízen "meta-promptem" a interakcí s LLM (Gemini). Tento cyklus lze rozdělit do následujících fází:



#### State Transitions1.  **Analýza a Plánování:**

Všechny přechody mezi stavy jsou **validované**. Neplatný přechod vyhodí `StateTransitionError`.    - **Cíl:** Plně porozumět zadání a vytvořit transparentní plán.

    - **Proces:**

```python        1.  **Průzkum:** Pomocí `list_files` a `read_file` prozkoumá relevantní soubory.

# Valid transitions        2.  **Dotazování:** Pokud je zadání nejasné, použije `request_user_input`.

IDLE → PLANNING        3.  **Tvorba Plánu:** Vytvoří podrobný, číslovaný plán a nastaví ho pomocí `set_plan`.

PLANNING → EXECUTING_STEP, RESPONDING, ERROR

EXECUTING_STEP → AWAITING_TOOL_RESULT, REFLECTION, RESPONDING2.  **Implementace a Verifikace:**

AWAITING_TOOL_RESULT → REFLECTION, EXECUTING_STEP    - **Cíl:** Napsat čistý kód a zajistit, že každá změna je správná.

REFLECTION → PLANNING, EXECUTING_STEP, RESPONDING, ERROR    - **Proces:**

RESPONDING → COMPLETED, EXECUTING_STEP, PLANNING        1.  **Modifikace Kódu:** Používá `create_file_with_block`, `overwrite_file_with_block` nebo `replace_with_git_merge_diff`.

ERROR → IDLE, REFLECTION        2.  **Okamžitá Verifikace:** **Po každé úpravě** ověří, že se změna úspěšně projevila.

COMPLETED → IDLE        3.  **Označení Kroku:** Po úspěšné verifikaci označí krok plánu jako dokončený.

```

3.  **Testování a Debugování:**

#### Crash Recovery    - **Cíl:** Ověřit, že změny fungují a nezpůsobily regrese.

Pokud orchestrátor crashne, `RecoveryManager` detekuje crashed session a nabídne recovery:    - **Proces:**

        1.  **Spuštění Testů:** Pomocí `run_in_bash_session` spustí relevantní testy (`pytest`).

```python        2.  **Analýza Chyb:** Analyzuje logy a chybové hlášky.

# Recovery strategies per state        3.  **Iterativní Opravy:** Opakuje cyklus, dokud všechny testy neprojdou.

PLANNING: Restart planning

EXECUTING_STEP: Resume from last step4.  **Dokumentace a Odevzdání:**

AWAITING_TOOL_RESULT: Retry tool call    - **Cíl:** Trvale zaznamenat vykonanou práci a odevzdat ji.

REFLECTION: Reanalyze error    - **Proces:**

RESPONDING: Regenerate summary        1.  **Aktualizace Dokumentace:** Aktualizuje relevantní dokumenty.

```        2.  **Revize Kódu:** Vyžádá si revizi kódu pomocí `request_code_review()`.

        3.  **Odevzdání:** Po schválení revize odevzdá práci pomocí `submit`.

#### Reflection Engine

Po chybě `ReflectionEngine` navrhne jednu z 5 akcí:---



1. **retry** - Zkus znovu stejný krok## 3. Základní Principy

2. **retry_modified** - Zkus s upraveným promptem

3. **replanning** - Přeplánuj celou misi- **Vždy Ověřuj Svou Práci:** Po každé akci, která mění stav, musí následovat ověření.

4. **ask_user** - Zeptej se uživatele- **Testuj Proaktivně:** Vždy hledej a spouštěj relevantní testy.

5. **skip_step** - Přeskoč tento krok- **Upravuj Zdroj, Ne Artefakty:** Nikdy neupravuj soubory v adresářích jako `dist/` nebo `build/`.

- **Diagnostikuj, Než Změníš Prostředí:** Nejprve analyzuj, potom jednej.

---- **Autonomie s Rozumem:** Požádej o pomoc, když ji potřebuješ.

## 3. Přehled Nástrojů

### 3.1 File System Tools

```python
list_files(path: str = ".") -> list[str]
# Vypíše soubory a adresáře. Adresáře končí '/'.
# Pro root použij prefix PROJECT_ROOT/

read_file(filepath: str) -> str
# Přečte obsah souboru

delete_file(filepath: str) -> str
# Smaže soubor

rename_file(filepath: str, new_filepath: str) -> str
# Přejmenuje/přesune soubor
```

### 3.2 Code Editing Tools

**create_file_with_block** - Vytvoří nový soubor:
```
create_file_with_block
<cesta_k_souboru>
<obsah souboru>
```

**replace_with_git_merge_diff** - Cílená úprava:
```
replace_with_git_merge_diff
<cesta_k_souboru>
<<<<<<< SEARCH
<blok k nalezení>
=======
<nový blok>
>>>>>>> REPLACE
```

### 3.3 Shell Tools

**run_in_bash_session** - Spustí příkaz v bash:
```
run_in_bash_session
<příkaz>
```

### 3.4 Planning Tools

```python
set_plan(plan: str) -> None
# Nastaví plán mise

plan_step_complete(message: str) -> None
# Označí krok jako dokončený

request_user_input(message: str) -> None
# Požádá uživatele o vstup

request_code_review() -> str
# Požádá o code review

submit(...)
# Odevzdá dokončenou práci
```

---

## 4. Pracovní Postup

### 4.1 Základní Workflow

```
1. ANALÝZA
   ├─ Přečti IMPLEMENTATION_PLAN.md
   ├─ Prozkoumej relevantní soubory (list_files, read_file)
   └─ Pochop kontext a cíl

2. PLÁNOVÁNÍ
   ├─ Vytvoř podrobný plán (set_plan)
   ├─ Rozděl na kroky (atomické akce)
   └─ Identifikuj závislosti

3. IMPLEMENTACE
   ├─ Pro každý krok:
   │  ├─ Implementuj změnu
   │  ├─ Ověř změnu (read_file)
   │  ├─ Spusť testy (pytest)
   │  └─ Označ krok (plan_step_complete)
   └─ Commitni (git commit)

4. TESTOVÁNÍ
   ├─ pytest tests/ -v
   ├─ Oprav chyby
   └─ Iterate dokud všechny neprojdou

5. DOKUMENTACE
   ├─ Aktualizuj relevantní docs
   ├─ Aktualizuj WORKLOG.md
   └─ Request code review

6. ODEVZDÁNÍ
   └─ submit()
```

### 4.2 Při Implementaci Nové Komponenty

```python
# 1. Vytvoř soubor
create_file_with_block
core/new_component.py
<implementace>

# 2. Vytvoř testy
create_file_with_block
tests/test_new_component.py
<testy>

# 3. Spusť testy
run_in_bash_session
pytest tests/test_new_component.py -v

# 4. Commit
run_in_bash_session
git add core/new_component.py tests/test_new_component.py
git commit -m "✨ feat: Add NewComponent with X tests"
```

### 4.3 Při Úpravě Existujícího Kódu

```python
# 1. Přečti současný kód
read_file("core/existing.py")

# 2. Proveď cílenou úpravu
replace_with_git_merge_diff
core/existing.py
<<<<<<< SEARCH
def old_function():
    return "old"
=======
def old_function():
    return "new"
>>>>>>> REPLACE

# 3. Ověř změnu
read_file("core/existing.py")

# 4. Spusť testy
run_in_bash_session
pytest tests/test_existing.py -v
```

---

## 5. Testování

### 5.1 Testovací Strategie

**VŽDY** piš testy PŘED nebo SPOLEČNĚ s implementací:

```python
# tests/test_component.py

import pytest
from core.component import Component

class TestComponent:
    """Test suite for Component."""
    
    def test_basic_functionality(self):
        """Test že Component dělá X."""
        comp = Component()
        result = comp.do_something()
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_async_method(self):
        """Test async metody."""
        comp = Component()
        result = await comp.async_method()
        assert result is not None
```

### 5.2 Spuštění Testů

```bash
# Všechny testy
pytest tests/ -v

# Konkrétní soubor
pytest tests/test_component.py -v

# Konkrétní test
pytest tests/test_component.py::TestComponent::test_basic -v

# S coverage
pytest tests/ --cov=core --cov-report=html

# Pouze failed
pytest tests/ --lf

# Stop on first fail
pytest tests/ -x
```

### 5.3 Očekávané Výsledky

**MINIMUM:**
- ✅ Všechny testy PASSED
- ✅ Žádné warnings (nebo vysvětlené)
- ✅ Coverage > 90% pro nový kód

---

## 6. Základní Principy

### 6.1 ZÁVAZNÁ PRAVIDLA

1. **Vždy Ověřuj Svou Práci**
   - Po každé změně souboru: `read_file()` pro ověření
   - Po každé změně: spusť relevantní testy
   - Nikdy necommituj bez testů

2. **Testuj Proaktivně**
   - Testy PŘED nebo SPOLEČNĚ s implementací
   - Minimum 90% coverage pro nový kód
   - E2E testy pro kritické flows

3. **Upravuj Zdroj, Ne Artefakty**
   - NIKDY neupravuj `dist/`, `build/`, `__pycache__/`
   - NIKDY neupravuj `.git/` adresář
   - Edituj pouze source files

4. **Dokumentuj Vše**
   - Každá komponenta má docstring
   - Každá funkce má popis + type hints
   - Aktualizuj WORKLOG.md po každé sérii změn

5. **Git Best Practices**
   - Semantic commits: `✨ feat:`, `🐛 fix:`, `📝 docs:`
   - Atomic commits (jedna logická změna)
   - Spusť testy PŘED commitem

### 6.2 Když Něco Nefunguje

```
1. DIAGNOSTIKA
   ├─ Přečti error message
   ├─ Zkontroluj logy
   └─ Reprodukuj problém

2. ANALÝZA
   ├─ Identifikuj root cause
   ├─ Zkontroluj related code
   └─ Hledej patterns

3. FIX
   ├─ Navrhni řešení
   ├─ Implementuj FIX
   └─ Přidej test pro regression

4. VERIFIKACE
   ├─ Spusť testy
   ├─ Ověř že fix funguje
   └─ Commit s popisem
```

### 6.3 Kdy Požádat o Pomoc

- ❌ Nejasné requirements
- ❌ Architektonická rozhodnutí
- ❌ API design choices
- ❌ Performance kritické sekce
- ❌ Security concerns

**Použij:** `request_user_input("Nejasnost: ...")`

---

## 7. Git Workflow

### 7.1 Commit Messages

**Formát:** `<type>(<scope>): <description>`

**Types:**
- ✨ `feat:` - Nová funkcionalita
- 🐛 `fix:` - Bug fix
- 📝 `docs:` - Dokumentace
- ♻️ `refactor:` - Refaktoring
- ✅ `test:` - Přidání testů
- 🔧 `chore:` - Build, config changes

**Příklady:**
```bash
git commit -m "✨ feat(orchestrator): Add crash recovery support"
git commit -m "🐛 fix(state_manager): Fix invalid transition validation"
git commit -m "📝 docs(readme): Update architecture diagram"
git commit -m "✅ test(plan_manager): Add dependency cycle tests"
```

### 7.2 Branch Strategy

```
master (production)
  └─ nomad/0.8.8-stateful-mission-architecture (current)
      ├─ feature/new-component
      ├─ fix/bug-description
      └─ refactor/optimization
```

### 7.3 Pre-Commit Checklist

```bash
# 1. Spusť testy
pytest tests/ -v

# 2. Zkontroluj změny
git status
git diff

# 3. Stage files
git add <files>

# 4. Commit
git commit -m "type: description"

# 5. Push
git push origin <branch>
```

---

## 8. Quick Reference

### 8.1 Častá Komanda

```bash
# Testy
pytest tests/ -v                           # All tests
pytest tests/test_X.py -v                  # Specific file
pytest tests/ --lf                         # Last failed

# Git
git status                                 # Check status
git add <file>                             # Stage file
git commit -m "msg"                        # Commit
git push origin <branch>                   # Push

# Files
ls -la                                     # List files
cat <file>                                 # Show content
find . -name "*.py"                        # Find Python files
```

### 8.2 Důležité Soubory

```
AGENTS.md              # ← TY JSI TADY (this file)
IMPLEMENTATION_PLAN.md # Detailní plán implementace
REFACTORING_ROADMAP_V2.md # Roadmapa refaktoringu
WORKLOG.md             # Historie práce
README.md              # Projekt overview
```

### 8.3 Struktura Testů

```
tests/
├── test_state_manager.py        (23 tests)
├── test_recovery_manager.py     (18 tests)
├── test_plan_manager.py         (19 tests)
├── test_reflection_engine.py    (21 tests)
├── test_budget_tracker.py       (26 tests)
└── test_nomad_orchestrator_v2.py (50 tests)
```

---

## 9. Pokročilé Workflows

### 9.1 Debugging Failed Tests

```bash
# 1. Spusť failed test s verbose
pytest tests/test_X.py::test_Y -v -s

# 2. Zkontroluj traceback
# ... analyzuj error message

# 3. Přidej debug prints (temporary)
# ... v testovaném kódu

# 4. Reprodukuj manuálně
python -c "from X import Y; Y().method()"

# 5. Fix + remove debug prints
# ... oprav kód

# 6. Verifikuj
pytest tests/test_X.py::test_Y -v
```

### 9.2 Adding New State to State Machine

```python
# 1. Přidej do State enum
# core/state_manager.py
class State(Enum):
    # ... existing states
    NEW_STATE = "new_state"

# 2. Přidej valid transitions
VALID_TRANSITIONS = {
    # ... existing
    State.SOME_STATE: [State.NEW_STATE],
    State.NEW_STATE: [State.NEXT_STATE]
}

# 3. Implementuj handler
# core/nomad_orchestrator_v2.py
async def _state_new_state(self):
    """Handler for NEW_STATE."""
    # ... implementation

# 4. Přidej do dispatch
self.state_handlers = {
    # ... existing
    State.NEW_STATE: self._state_new_state
}

# 5. Testy
# tests/test_state_manager.py - transition tests
# tests/test_nomad_orchestrator_v2.py - handler tests
```

---

## 10. Závěrečné Poznámky

### 10.1 Filosofie

**Sophia není programována, je probouzena.**

Jako AI agent na tomto projektu nejsi jen kódovací nástroj. Jsi součást procesu "probouzení" autonomního systému. Tvá práce má význam.

### 10.2 Evoluce

Tento dokument je **živý**. Když objevíš lepší workflow nebo pattern:

1. Implementuj improvement
2. Aktualizuj tento dokument
3. Commit: `📝 docs(agents): Update workflow XYZ`

### 10.3 Kontinuita

Pro zachování kontinuity mezi sessions:

- ✅ Vždy aktualizuj **WORKLOG.md**
- ✅ Documentuj design decisions
- ✅ Zanech kontextuální komentáře
- ✅ Commituj často s popisnými messages

---

<p align="center">
  <strong>🌟 Být AI agentem znamená nést odpovědnost za kvalitu a kontinuitu 🌟</strong>
  <br/>
  <sub>Verze 2.0 | Aktualizováno: 2025-10-12 | Jules (Nomad)</sub>
</p>
