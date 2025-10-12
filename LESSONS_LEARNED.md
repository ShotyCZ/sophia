# Poučení z Vývoje Projektu Nomád

**Dokument:** Analytická zpráva o evoluční cestě projektu
**Datum:** 12. října 2025
**Účel:** Identifikace chyb, slepých uliček a klíčových ponaučení pro budoucí vývoj

---

## Úvod: Cesta k Poznání

Projekt Nomád představuje fascinující, ale zároveň varovný příběh o tom, jak může snaha o dokonalost vést k paralýze. Původní vize byla jasná: vytvořit autonomního AI softwarového inženýra schopného sebereflexe a sebezdokonalování. Co následovalo, byla série architektonických refaktoringů, z nichž každý měl vyřešit problémy předchozího, ale místo toho vedl k novým, často horším komplikacím.

Tento dokument analyzuje jednotlivé evoluční fáze projektu a identifikuje kořenové příčiny selhání.

---

## 1. Architektura "Jednoho Agenta" (Původní Stav)

### Popis
Počáteční implementace byla založena na jediném, monolitickém `JulesOrchestrator` (později přejmenovaném na `WorkerOrchestrator`). Tento orchestrátor měl všechny zodpovědnosti:
- Komunikaci s uživatelem
- Porozumění úkolům
- Plánování postupů
- Provádění akcí pomocí nástrojů
- Generování odpovědí

### Co fungovalo
- **Jednoduchost:** Celý systém byl soustředěn do jednoho místa, což ho činilo snadným na pochopení a ladění.
- **Přímočarost:** Tok dat byl lineární - vstup → myšlení → nástroje → výstup.
- **Skutečná autonomie:** Agent měl přístup ke všem nástrojům a mohl měnit vlastní kód bez omezení.

### Co selhávalo
- **Ztráta kontextu:** U komplexních úkolů agent rychle vyčerpal kontext LLM a "zapomněl" na původní cíl.
- **Halucinace nástrojů:** Bez jasných omezení agent často vymýšlel nástroje, které neexistovaly.
- **Rigidita:** Bez vnitřní struktury nedokázal rozlišit mezi jednoduchým dotazem a komplexním projektem, obojí zpracovával stejně.
- **"Mission Amnesia":** Po sérii kroků agent ztrácel ponětí o tom, co vlastně dělá a proč.

### Klíčové poučení
**Komplexní úkoly nelze řešit monoliticky bez explicitní správy stavu.** Problém nebyl v samotné koncepci jednoho agenta, ale v absenci stavového stroje a hierarchického plánování.

---

## 2. Architektura "Manažer/Worker" (Fáze 1)

### Popis
První pokus o řešení problémů vedl k oddělení zodpovědností:
- **`ConversationalManager`** ("Manažer"): Komunikace s uživatelem, rozhodování, delegování úkolů.
- **`WorkerOrchestrator`** ("Worker"): Provádění skutečné práce pomocí nástrojů.

Pro zamezení halucinacím byla zavedena koncepce "profilů" nástrojů:
- Manažer měl omezený profil s "read-only" nástroji.
- Worker měl plný přístup ke všem exekučním nástrojům.

Byl zaveden "rozpočet na složitost" - Worker dostal omezený počet kroků. Pokud je vyčerpal, vracel stav `needs_planning`.

### Co fungovalo
- **Oddělení rolí:** Manažer se přestal pokoušet přímo upravovat soubory.
- **Flexibilita:** Systém rozpočtu umožnil dynamicky volit mezi rychlým řešením a plánovaným přístupem.
- **Transparentnost:** Uživatel viděl, kdy se agent rozhodl vytvořit plán.

### Co selhávalo
- **Halucinace nástrojů manažera:** Přestože měl Manažer omezený profil, LLM stále často halucinoval nástroje, které neměl k dispozici (např. `get_worker_status`).
- **Rigidní triage:** Systém "rozpočtu" byl teoreticky dobrý, ale prakticky vedl k byrokratickému chování - agent i pro jednoduché úkoly spouštěl zdlouhavé plánovací procesy.
- **Fragmentace kontextu:** Rozdělení na dvě entity začalo vytvářet problém s přenosem kontextu mezi Manažerem a Workerem.
- **Nejasná hranice zodpovědnosti:** Manažer měl teoreticky "řídit", ale prakticky jen předával zprávy sem a tam.

### Klíčové poučení
**Rozdělení na více vrstev bez jasného datového toku a stavové správy problémy neřeší, ale pouze přesouvá a komplikuje je.** Halucinace nástrojů byla symptom, nikoli kořenový problém - skutečný problém byla nejasná role a nedostatečně striktní prompt engineering.

---

## 3. Architektura "Reflektivní Mistr" (Fáze 2)

### Popis
Fáze 2 se zaměřila na přidání schopnosti sebereflexe:
- Po dokončení úkolu `ConversationalManager` spouštěl proces reflexe.
- Reflexe analyzovala historii kroků a generovala "poučení", které se ukládalo do dlouhodobé paměti (LTM) s metadatem `{"type": "learning"}`.
- `PromptBuilder` při sestavování promptu pro Workera načítal relevantní poučení z LTM a vkládal je do systémového promptu.

### Co fungovalo
- **Prokázaná schopnost učení:** Testy potvrdily, že agent dokázal po jednom neefektivním pokusu upravit své budoucí chování.
- **Elegantní implementace:** Oddělení učení (Manažer) od aplikování znalostí (Worker) bylo logicky čisté.
- **LTM jako centrální paměť:** Použití vektorové databáze pro ukládání a vyhledávání poučení bylo technicky správné.

### Co selhávalo
- **Reflexe sama o sobě nestačila:** Učení z minulosti nemohlo kompenzovat fundamentální problém - **agent stále neměl explicitní model svého aktuálního stavu**.
- **Nárust složitosti bez zlepšení stability:** Přidání reflexe zvýšilo počet komponent, ale neřešilo základní problém ztráty kontextu během dlouhých úkolů.
- **Byrokratické chování přetrvávalo:** I s poučením agent nadále zbytečně spouštěl plánovací procesy pro jednoduché úkoly (byť méně často).

### Klíčové poučení
**Sebereflexe je cenná schopnost, ale bez robustního správce stavu je to jen další funkce přidaná na nestabilní základ.** Poučení z minulosti nemůže nahradit znalost aktuálního stavu.

---

## 4. Architektura "Stateful Mission" (Současný Stav)

### Popis
Nejnovější pokus o vyřešení problémů zavedl třetí vrstvu - **`MissionManager`**:
- **`MissionManager`** (Project Manager): Drží celkový cíl mise, vytváří plán pomocí `PlanningServer`, řídí dispatch podúkolů.
- **`ConversationalManager`** (Task Dispatcher): Stal se "stateless" dispatcher - přijímá jeden podúkol z MissionManageru a deleguje ho Workerovi.
- **`WorkerOrchestrator`** (Focused Specialist): Provádí konkrétní, nízko-úrovňové akce pro jeden podúkol.

Tato architektura měla řešit "Mission Amnesia" tím, že vysokoúrovňový kontext (mise) je oddělen od nízkoúrovňové exekuce (podúkol).

### Co fungovalo (teoreticky)
- **Jasná hierarchie zodpovědností:** Každá vrstva měla definovanou roli.
- **Explicitní správa stavu mise:** `MissionManager` udržoval `mission_prompt`, `sub_tasks`, `current_task_index`.
- **Oddělení plánování od exekuce:** `PlanningServer` a `ReflectionServer` měly jasný účel.

### Co selhává (prakticky)

#### 4.1. Architektonická Schizofrenie (Roztrojená Osobnost)
Systém nyní má **tři různé entity**, každou s vlastním LLM kontextem, vlastním promptem a vlastním mentálním modelem:
- MissionManager si myslí, že řídí projekt.
- ConversationalManager si myslí, že zprostředkovává mezi uživatelem a Workerem.
- WorkerOrchestrator si myslí, že řeší podúkol.

**Problém:** Nikdo z nich nemá kompletní obraz celé situace. Každý má pouze svůj fragment.

#### 4.2. Fragmentace Kontextu
Aby MissionManager předal úkol Workerovi (přes ConversationalManager), musí kontext projít **třemi různými LLM voláními**:
1. MissionManager → LLM call (plánování)
2. ConversationalManager → LLM call (dispatch)
3. WorkerOrchestrator → LLM call (exekuce)

Při každém kroku se kontext ztrácí, zkresluje nebo přeformuluje. Worker na konci řetězce často dostává velmi redukovanou verzi původního záměru.

#### 4.3. Kritická Chyba: KeyError v Reflexi
Analýza kódu odhalila závažný, ale symptomatický problém:

`ConversationalManager` má metodu `generate_final_response`, která má být volána MissionManagerem. Ale díky rozdělení zodpovědností je tato metoda volána v kontextu, kde neexistuje přístup k historii, kterou Worker generoval. Tím pádem:
- Reflexe nemůže analyzovat, co Worker skutečně dělal.
- Poznatky jsou generovány bez kontextu provedených kroků.
- Agent **se nemůže učit z vlastních chyb**, protože tato data nikdy nedorazí tam, kde má být reflexe provedena.

Toto není jen bug - je to **důsledek architektonické schizofrenie**. Data jsou fragmentována mezi vrstvami, které spolu nekomunikují dostatečně.

#### 4.4. "Human-in-the-Loop" jako Záplata na Záplatě
Fáze 3 přidala schvalovací mechanismus pro delegování na Jules API:
- Worker rozhodne, že potřebuje delegovat.
- Vrátí stav `needs_delegation_approval`.
- ConversationalManager se zeptá uživatele.
- MissionManager čeká na odpověď.

**Problém:** Toto je implementace "bezpečnosti" jako poslední vrstvy na vrcholu již tak komplikované hierarchie. Místo aby byl schvalovací proces součástí elegantního stavového stroje, je to další "if-else" větev v rostoucí spaghetové logice.

### Klíčové poučení
**Přidávání vrstev neřeší problém ztráty kontextu - naopak ho prohlubuje.** Každá nová vrstva přidává další bod selhání, další místo, kde se kontext může ztratit, a další mentální model, který je v rozporu s ostatními.

Současná architektura trpí **předimenzováním** (over-engineering). Řeší problémy, které by existovat neměly, kdybychom měli správně navržený základ.

---

## 5. Závěr: Hlavní Ponaučení

### 5.1. Komplexnost je Nepřítel
Hlavní nepřátel projektu nebyl nedostatek funkcí, ale **přílišná komplexnost**. Každý refaktoring přidal novou vrstvu, nový koncept, novou abstrakci, a tím také nové body selhání.

### 5.2. Vrstvy bez Stavového Stroje jsou Chaos
Rozdělení na Manager/Worker/Mission bez centrálního, explicitního stavového stroje vedlo k tomu, že každá vrstva si vede vlastní stav a vlastní "pravdu" o tom, co se děje.

### 5.3. Řešení Symptomu vs. Kořenové Příčiny
- **Symptom:** Agent halucinuje nástroje.
- **Pokus o řešení:** Přidat další vrstvu (Manažera) s omezenými nástroji.
- **Skutečná kořenová příčina:** Nejasné instrukce v promptu a absence strukturovaného stavového modelu.

Místo aby byl opraven prompt a přidán stavový stroj, byl přidán další layer, který problém pouze přesunul.

### 5.4. Sebereflexe bez Stavu je Zbytečná
Schopnost učení je cenná, ale pokud agent **neví, kde se právě nachází** (v jakém stavu), nemůže své znalosti efektivně aplikovat.

### 5.5. Finální Poučení

> **Hlavním ponaučením je, že složitost musí být adresována na úrovni NÁVRHU, ne přidáváním dalších vrstev abstrakce.**
> 
> Správný přístup je:
> 1. **Jeden centrální orchestrátor** (jeden "mozek").
> 2. **Explicitní stavový stroj** (agent vždy ví, v jakém je stavu).
> 3. **Perzistence stavu** (po restartu může pokračovat, odkud skončil).
> 4. **Hierarchické plánování jako VNITŘNÍ mechanismus**, ne jako další vrstva.
> 5. **Jednoduché, jasné datové toky** bez fragmentace kontextu.

Namísto tří roztrojených vrstev potřebujeme **jednu, robustní entitu s jasným modelem svého vnitřního stavu**.

---

## 6. Co Zachovat z Minulých Verzí

I přes všechny problémy byly v projektu implementovány cenné koncepty, které **musí být zachovány**:

1. **MCP architektura pro nástroje:** Oddělení nástrojů do samostatných serverů je správné a mělo by zůstat.
2. **LTM s vektorovým vyhledáváním:** Dlouhodobá paměť funguje dobře a je klíčová pro učení.
3. **Mechanismus reflexe:** Koncept sebereflexe je cenný, ale musí být integrován do stavového modelu.
4. **TUI s Textual:** Uživatelské rozhraní je kvalitní a nemělo by být měněno.
5. **PromptBuilder:** Dynamické sestavování promptů s kontextem z LTM je správná technika.

---

**Konec dokumentu**

Tato analýza poskytuje základ pro vytvoření nové, finální architektury, která se vyhne všem identifikovaným slepým uličkám a postaví stabilní, jednoduchou a skutečně autonomní verzi Nomáda.
