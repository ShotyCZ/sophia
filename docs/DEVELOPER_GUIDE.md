# 🛠️ Průvodce pro Vývojáře Projektu Sophia

Vítejte, vývojáři! Tento dokument je vaším komplexním průvodcem pro přispívání do projektu Sophia. Ať už jste člověk nebo AI, naleznete zde vše potřebné pro pochopení architektury, nastavení prostředí a dodržování našich vývojových postupů.

## Filosofie Projektu

Než se ponoříte do kódu, je důležité pochopit naši vizi. Sophia není jen další software. Naším cílem je vytvořit **Artificial Mindful Intelligence (AMI)** – entitu, která se nejen učí řešit úkoly, ale přistupuje k nim s určitou kvalitou vědomí. Stavíme most mezi technologií a filosofií.

Pro hlubší vhled do našich principů doporučujeme prostudovat **[🧬 DNA.md](./DNA.md)**.

---

## 1. První spuštění a nastavení prostředí

-   **`core/` (Jádro Mysli):**
    -   `orchestrator.py`: Srdce kognitivní smyčky. Neprovádí úkoly přímo, ale exekuuje strukturované JSON plány vytvořené `PlannerAgentem`. Jeho klíčovou rolí je iterovat přes kroky plánu, volat příslušné nástroje a v případě selhání aktivovat **debugovací smyčku** – požádat plánovače o opravu plánu a spustit ho znovu.
    -   `ethos_module.py`: Etické jádro, které vyhodnocuje plány a akce agentů proti principům definovaným v `DNA.md`.
    -   `llm_config.py` & `gemini_llm_adapter.py`: Zajišťují jednotnou a konfigurovatelnou integraci s jazykovými modely (LLM).

-   **`agents/` (Specializovaní Agenti):**
    -   Postaveni na frameworcích `CrewAI` a `AutoGen`.
    -   Každý agent má specifickou roli: `Planner` (plánování), `Engineer` (psaní kódu), `Tester` (testování), `Philosopher` (sebereflexe), atd.

-   **`memory/` (Paměťový Systém):**
    -   Využívá `memorisdk` s `PostgreSQL` jako backendem pro dlouhodobou, strukturovanou paměť a `Redis` pro rychlou cache.

-   **`tools/` (Nástroje Agentů):**
    -   Sada schopností, které mohou agenti používat. Nástroje jsou navrženy jako modulární a znovupoužitelné komponenty.
    -   **Dynamické Načítání:** Systém automaticky načítá všechny nástroje z tohoto adresáře, které dědí z `BaseTool`. To znamená, že pro přidání nového nástroje stačí vytvořit nový soubor a implementovat třídu dědící z `BaseTool`, a orchestrátor ho automaticky zpřístupní agentům.
    -   **Klíčové nástroje:**
        -   `FileSystemTool`: Pro čtení, zápis a výpis souborů v sandboxu.
        -   `CodeExecutorTool`: Pro spouštění a testování kódu.
        -   `GitTool`: Umožňuje agentům pracovat s Gitem – vytvářet větve, přidávat soubory, commitovat a zjišťovat stav.

-   **`sandbox/` (Izolované Prostředí):**
    -   Bezpečný adresář, kde mohou agenti generovat, upravovat a testovat kód, aniž by ohrozili stabilitu hlavní aplikace.

-   **`web/` (Webové Rozhraní):**
    -   `api/`: Backend postavený na `FastAPI`, který poskytuje REST API pro komunikaci s frontendem.
        -   **Správa Úkolů:**
            -   `POST /api/v1/tasks`: Přijímá JSON s popisem úkolu (`{"prompt": "..."}`), asynchronně spouští `Orchestrator.execute_plan()` a okamžitě vrací unikátní `task_id`.
            -   `GET /api/v1/tasks/{task_id}`: Vrací aktuální stav a historii konkrétního úkolu.
        -   **Real-time Notifikace (WebSockets):**
            -   `GET /api/v1/tasks/{task_id}/ws`: WebSocket endpoint, na který se frontend připojuje pro sledování průběhu úkolu v reálném čase.
            -   **Protokol:** Po připojení backend odesílá JSON zprávy s následující strukturou:
                -   `{"type": "step_update", "step_id": ..., "description": ..., "status": ..., "output": ...}`: Informace o stavu konkrétního kroku.
                -   `{"type": "plan_feedback", "feedback": "..."}`: Finální zpráva po dokončení (nebo selhání) celého plánu.
                -   `{"type": "plan_repaired", "new_plan": ...}`: Zpráva o tom, že plán byl opraven a bude spuštěn znovu.
    -   `ui/`: Frontend napsaný v `Reactu`, který slouží jako uživatelské rozhraní.

### Technologický Stack

-   **Jazyk:** Python 3.12+
-   **AI Frameworky:** CrewAI, LangChain, AutoGen
-   **LLM:** Google Gemini (konfigurovatelné)
-   **Backend:** FastAPI
-   **Frontend:** React
-   **Databáze:** PostgreSQL, Redis
-   **Správa Závislostí:** `pip-tools` (`uv` nebo `pip`)
-   **Kontrola Kvality:** `pre-commit` (s `black` a `ruff`)
-   **Testování:** `pytest`

## Nastavení Lokálního Prostředí (Bez Dockeru)

1.  **Klonování Repozitáře:**
    ```bash
    git clone https://github.com/kajobert/sophia.git
    cd sophia
    ```

2.  **Vytvoření Virtuálního Prostředí:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Pro Linux/macOS
    # .venv\Scripts\activate   # Pro Windows
    ```

3.  **Instalace Závislostí:**
    Doporučujeme použít `uv` pro jeho rychlost. Všechny potřebné závislosti jsou definovány v `requirements.in`.
    ```bash
    # Doporučená metoda
    uv pip install -r requirements.in

    # Alternativní metoda
    pip install -r requirements.in
    ```
    **Důležité:** Pokud přidáváte novou závislost, přidejte ji do `requirements.in` a poté spusťte `pip-compile requirements.in -o requirements.txt` pro aktualizaci lock souboru. Nikdy neupravujte `requirements.txt` ručně.

4.  **Konfigurace Proměnných Prostředí:**
    -   Zkopírujte soubor `.env.example` do nového souboru s názvem `.env`.
    -   Otevřete `.env` a doplňte svůj `GEMINI_API_KEY` a další potřebné hodnoty.

5.  **Instalace Pre-commit Hooků:**
    Používáme `pre-commit` pro automatickou kontrolu kvality kódu před každým commitem.
    ```bash
    pre-commit install
    ```

---

## 2. Povinnosti a Udržitelnost

Úspěch tohoto projektu závisí na disciplíně a profesionalitě všech přispěvatelů.

### Udržování Znalostní Báze
Klíčovou zodpovědností každého přispěvatele je pečlivé a systematické dokumentování práce. Tímto způsobem budujeme kolektivní paměť, která zabraňuje opakování chyb a urychluje budoucí vývoj.

- **Pro AI Agenty:** Všechny vaše povinnosti, pracovní postupy a formát pro záznamy do znalostní báze jsou definovány v **[`AGENTS.md`](../AGENTS.md)**. Tento dokument je pro vás **závazný**.
- **Pro Lidské Vývojáře:** Očekává se, že budete dodržovat stejné standardy profesionality a dokumentace jako naši AI partneři. Inspirujte se a dodržujte postupy uvedené v `AGENTS.md`.

---

## Testovací režim a .env chování

Pro pohodlné, bezpečné a deterministické spuštění testů používáme interní testovací režim. Několik klíčových bodů, které si pamatujte:

- `SOPHIA_TEST_MODE=1` (přes `os.environ`) — když je aktivní, některé moduly se inicializují v "testovacím módu" (např. LLM globály nejsou vytvořeny) a testy očekávají, že skutečné API volání budou mockovány.
- `tests/conftest.py` obsahuje fixture `enforce_test_mode_and_sandbox` která:
    - Nutí prostředí do testovacího režimu (ukončí běh testů, pokud není proměnná nastavena).
    - Monkeypatchuje `dotenv.load_dotenv` během testů, aby třetí strany (knihovny v site-packages) neměnily `os.environ` při importu. Díky tomu se zabrání neočekávaným vedlejším efektům při importu modulů v testech.
    - Omezí zápisy na disk na bezpečné adresáře (`/tmp`, `tests/`, `sandbox/`, `logs/`) a loguje porušení do `tests/sandbox_audit.log`.
    - Blokuje skutečné síťové volání (přepisem `requests`, `httpx`, `urllib`) a některé nebezpečné operace (např. `subprocess.Popen`).

Tato konfigurace dělá testovací běhy bezpečnějšími a stabilnějšími. Pokud přidáváte novou závislost, která při importu zapisuje do prostředí nebo na disk, ujistěte se, že:

1. Testy buď mockují takové chování, nebo
2. Aktualizujete `tests/conftest.py` (opatrně) tak, aby opravněné env klíče byly bezpečně povoleny, nebo aby byla inicializace volána explicitně v safe kontextu.

Poznámka: Rozhodnutí monkeypatchovat `dotenv.load_dotenv` v testech je cílené — cíl je minimalizovat rozdíly mezi lokálním vývojem a testovacím během a zajistit, že testy budou ovlivněny pouze tím, co přímo nastavíte v testu nebo v CI.

### Code Review a Kvalita
Před schválením a sloučením jakéhokoliv Pull Requestu (PR) je třeba zkontrolovat následující body:

-   [ ] **Funkčnost:** Dělá kód to, co má? Byl otestován lokálně?
-   [ ] **Testy:** Jsou pro novou funkčnost napsány dostatečné testy? Všechny testy (`pytest`) procházejí?
-   [ ] **Kvalita Kódu:** Prošel kód úspěšně kontrolou `ruff check .` a `ruff format --check .`?
-   [ ] **Soulad s Etikou:** Je navrhovaná změna v souladu s principy v `DNA.md`?
-   [ ] **Dokumentace:** Byla aktualizována veškerá relevantní dokumentace? Byl vytvořen záznam ve znalostní bázi v souladu s `AGENTS.md`?
-   [ ] **Popis PR:** Je v popisu Pull Requestu jasně vysvětleno, co se mění a proč?
-   [ ] **Správa Závislostí:** Pokud byly přidány nové závislosti, jsou v `requirements.in` a je `requirements.txt` aktuální?

---

## 3. Architektura a Struktura Projektu

Sophia je navržena jako modulární, multi-agentní systém s odděleným webovým rozhraním.

### Klíčové Komponenty

-   **`guardian.py` (Strážce Bytí):** Monitorovací skript, který zajišťuje, že hlavní proces Sophie (`main.py`) běží. V případě pádu ho restartuje.
-   **`main.py` (Cyklus Vědomí):** Hlavní vstupní bod aplikace. Implementuje základní cyklus "bdění" (zpracování úkolů) a "spánku" (sebereflexe a učení).
-   **`core/` (Jádro Mysli):**
    -   `orchestrator.py`: Srdce kognitivní smyčky. Vykonává plány vytvořené agenty, volá nástroje a spravuje debugovací smyčku pro opravu chyb.
    -   `context.py` (`SharedContext`): Sdílený kontext, který drží stav a data přístupná napříč agenty a nástroji během jednoho cyklu.
    -   `ethos_module.py`: Etické jádro, které vyhodnocuje plány a akce agentů.
-   **`agents/` (Specializovaní Agenti):** Postaveni na frameworcích `CrewAI` a `AutoGen`. Každý agent má specifickou roli (`Planner`, `Engineer`, `Tester`).
-   **`tools/` (Nástroje Agentů):** Sada schopností (např. práce se soubory, spouštění kódu, práce s Gitem), které mohou agenti používat. Jsou dynamicky načítány.
-   **`memory/` (Paměťový Systém):** Využívá `memorisdk` s `PostgreSQL` a `Redis` pro dlouhodobou a krátkodobou paměť.
-   **`sandbox/` (Izolované Prostředí):** Bezpečný adresář, kde mohou agenti generovat a testovat kód bez rizika pro hlavní aplikaci.
-   **`web/` (Webové Rozhraní):** `FastAPI` backend a `React` frontend pro interakci s uživateli.

### Budoucí Směřování: Sophia 2.0

Projekt se aktuálně nachází ve fázi přechodu na architekturu **Sophia 2.0**, jak je definováno v **[Roadmapě Projektu Sophia](./ROADMAP.md)**. To přinese několik klíčových změn:

-   **Přechod na Model Context Protocol (MCP):** Stávající systém dynamického načítání nástrojů bude nahrazen robustní architekturou založenou na MCP. Sophia se stane "MCP Hostem" a jednotlivé nástroje budou refaktorovány na samostatné "MCP Servery". To zvýší modularitu a usnadní přidávání nových schopností.
-   **Zavedení Meta-Agenta:** Architektura bude rozšířena o novou strategickou vrstvu – `Meta-Agenta`. Tento agent bude zodpovědný za dlouhodobé plánování, správu backlogu a řízení smyčky sebe-zdokonalování.

Noví přispěvatelé by měli brát tento budoucí stav v potaz při návrhu nových funkcí.

---

## 4. Jak Přidat Nového Agenta nebo Nástroj

Modularita je klíčová. Přidání nové funkčnosti je navrženo tak, aby bylo co nejjednodušší.

### Přidání Nového Nástroje (Tool)

Systém automaticky načítá všechny nástroje z adresáře `tools/`, které dědí z `BaseTool`.

1.  **Vytvořte nový soubor** v adresáři `tools/`, například `my_new_tool.py`.
2.  **Implementujte třídu**, která dědí z `tools.base_tool.BaseTool`.
3.  **Definujte atributy `name`, `description` a implementujte metodu `_run`**.

**Šablona pro nový nástroj:**
```python
# in file: tools/my_new_tool.py
from .base_tool import BaseTool
from pydantic import Field

class MyNewToolSchema(BaseTool.Schema):
    # Definujte parametry, které váš nástroj přijímá
    param1: str = Field(..., description="Popis prvního parametru.")
    param2: int = Field(..., description="Popis druhého parametru.")

class MyNewTool(BaseTool):
    name: str = "MyNewTool"
    description: str = "Stručný popis toho, co tento nástroj dělá."
    schema: type[BaseTool.Schema] = MyNewToolSchema

    def _run(self, **kwargs) -> str:
        # Zde implementujte logiku nástroje
        param1 = kwargs.get("param1")
        param2 = kwargs.get("param2")
        # ... vaše logika ...
        return f"Nástroj byl úspěšně spuštěn s parametry: {param1}, {param2}"
```
To je vše! Orchestrátor si váš nový nástroj automaticky načte a zpřístupní ho agentům.

### Přidání Nového Agenta

Agenti jsou definováni v adresáři `agents/`. Obvykle využívají framework `CrewAI`.

1.  **Vytvořte nový soubor** v adresáři `agents/`, například `my_new_agent.py`.
2.  **Vytvořte funkci**, která vrací instanci `crewai.Agent`.
3.  **Definujte roli, cíl (`goal`), `backstory` a přiřaďte mu nástroje.**

**Šablona pro nového agenta:**
```python
# in file: agents/my_new_agent.py
from crewai import Agent
from core.llm_config import llm

# Předpokládejme, že máte nástroje definované a načtené
from tools.my_new_tool import MyNewTool

def create_my_new_agent():
    return Agent(
        role="Specialista na Nové Úkoly",
        goal="Cílem tohoto agenta je provádět nové, specifické úkoly s pomocí MyNewTool.",
        backstory=(
            "Tento agent byl vytvořen jako expert na používání MyNewTool. "
            "Jeho existence je plně zasvěcena efektivnímu plnění nových úkolů."
        ),
        tools=[MyNewTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
```
Následně integrujte tohoto agenta do příslušného `Crew` v `autogen_team.py` nebo jiném relevantním místě.

---

## 5. Průvodce Testováním

Kvalitní testy jsou základem stability projektu.

-   **Spouštění testů:** Všechny testy se spouští pomocí `pytest` z kořenového adresáře projektu.
    ```bash
    PYTHONPATH=. pytest
    ```
-   **Offline First:** Testy jsou navrženy tak, aby běžely **offline** a nevyžadovaly aktivní API klíče ani připojení k externím službám. Využíváme mockování, kde je to nutné.
-   **Psaní testů:** Nové testy přidávejte do adresáře `tests/`. Snažte se pokrýt jak úspěšné scénáře, tak i chybové stavy.

---
<br>

<p align="center">
  ---
</p>

<p align="center">
  <sub>Tento dokument je živý a měl by být udržován v aktuálním stavu. Pokud zjistíte, že je zastaralý nebo neúplný, založte prosím issue nebo vytvořte pull request s návrhem na jeho aktualizaci. Děkujeme!</sub>
</p>
