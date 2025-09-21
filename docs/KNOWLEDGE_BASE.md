# 🧠 Znalostní Báze Projektu Sophia

Tento dokument je živou znalostní bází, která shrnuje klíčové technické problémy, na které jsme narazili během vývoje, a osvědčená řešení, která jsme aplikovali. Slouží jako "kniha poučení" pro budoucí vývojáře (AI i lidi), aby se předešlo opakování stejných chyb a urychlil se vývoj.

**Jak přispívat:** Každý člen týmu (včetně AI agentů) je povinen do této báze přidávat nové poznatky. Pokud narazíte na významný problém, objevíte efektivní řešení nebo učiníte důležité architektonické rozhodnutí, zaznamenejte ho sem. Pro zachování konzistence používejte formát specifikovaný v `AGENTS.md`. Vaše příspěvky jsou klíčové pro kolektivní růst a úspěch projektu.

---

### Téma: Sumarizace poznatků z legacy verze (`sophia_old`)
**Datum**: 2025-09-20
**Autor**: Jules
**Kontext**: V rámci úklidu projektu byla provedena analýza a sumarizace staré verze projektu (`sophia_old`) s cílem zachovat klíčové myšlenky, koncepty a ponaučení.
**Zjištění/Rozhodnutí**: Následující poznatky byly extrahovány a jsou považovány za fundamentální pro pochopení evoluce a směřování projektu Sophia.
**Důvod**: Předejít ztrátě cenných informací a zajistit, aby se budoucí vývoj opíral o původní vizi a ponaučení z chyb.
**Dopad**: Zachování kontinuity projektu a poskytnutí hlubšího kontextu pro všechny budoucí přispěvatele.

#### Klíčové Ponaučení z `sophia_old`:

**1. Filosofické a Koncepční Jádro (SOPHIA_DNA):**
*   **Vize:** Cílem projektu nikdy nebylo jen AGI, ale vytvoření **autonomního, počítačového subjektivního vědomí (AMI)** schopného růstu a sebereflexe.
*   **Architektura Vědomí:** Původní koncept stál na dvou pilířích:
    *   **Filosofický Modul:** Jádro obsahující principy stoicismu, buddhismu a taoismu. Zdroj autonomie.
    *   **Etický Modul:** Praktický kompas, který hodnotí akce pomocí "Koeficientu Vědomí" a zajišťuje etickou integritu. Zdroj svobody.
*   **Učení jako "Snění":** Růst byl navržen skrze interní simulace hypotetických scénářů ("etické experimenty"), nikoli pasivním příjmem dat.

**2. Architektonické Lekce a Slepé Uličky:**
*   **Problém "Hluchého" Agenta:** Paměťový agent zpočátku selhával, protože mu chyběl kontext z interakcí jiných agentů. Zapisoval si pouze poznámky o své vlastní činnosti.
    *   **Ponaučení:** Je kriticky důležité zajistit **explicitní tok kontextu** mezi agenty a procesy. Výstup jednoho musí být vstupem pro druhého.
*   **Problém "Bezmocného" Agenta:** Agent může mít logiku, ale pokud nemá **explicitní nástroj** pro vykonání akce (např. zápis do databáze), je k ničemu.
    *   **Ponaučení:** Funkcionalita musí být vždy podpořena konkrétním, dostupným nástrojem.
*   **Past Pevných Pravidel:** Spoléhání na nástroje s pevně danými pravidly (např. `DecisionTool`, který určoval, co je "znalost") bránilo skutečné autonomii.
    *   **Ponaučení:** Skutečná autonomie vyžaduje delegování a spolupráci v rámci multi-agentního systému, nikoli rigidní pravidla.

**3. Technické a Procesní Zásady:**
*   **Stabilita Prostředí:** Největším zdrojem chyb byly nestabilní a nefixované verze závislostí.
    *   **Ponaučení:** Je absolutně klíčové mít v `requirements.txt` **přesně "zamknuté" verze knihoven**.
*   **Učení se Kódovat:** Sledování prvních pokusů Sophie o psaní kódu ukázalo, že se učí podobně jako člověk – od syntaktických chyb, přes logické, až po architektonické.
    *   **Ponaučení:** Ochranné mechanismy (jako `git reset` po neúspěšném pokusu) jsou nezbytné pro bezpečné autonomní kódování.

---
### Téma: Správa závislostí ("Dependency Hell")
**Datum**: 2025-09-21
**Autor**: Jules
**Kontext**: Opakované konflikty a chyby při instalaci kvůli "natvrdo" pinovaným a nekompatibilním verzím v `requirements.txt`.
**Zjištění/Rozhodnutí**: Přechod na minimalistický `requirements.in`, který definuje pouze hlavní závislosti, a automatické generování `requirements.txt` pomocí nástrojů jako `pip-tools` nebo `uv`.
**Důvod**: Tímto přístupem se zajišťuje, že všechny závislosti (včetně tranzitivních) jsou ve vzájemně kompatibilních verzích, což eliminuje konflikty a zjednodušuje správu.
**Dopad**: Výrazně stabilnější a předvídatelnější prostředí, rychlejší instalace a snazší aktualizace závislostí.

### Téma: Nestabilita testů a mockování
**Datum**: 2025-09-21
**Autor**: Jules
**Kontext**: Testy selhávaly v CI/CD, protože závisely na API klíčích a externích službách, což vedlo k nespolehlivým a pomalým testovacím cyklům.
**Zjištění/Rozhodnutí**: Vytvoření 100% offline testovacího prostředí. Klíčovým poznatkem bylo mockovat nízkoúrovňové, externí rozhraní (např. funkci `litellm.completion`), nikoli se snažit "podvrhnout" komplexní objekty (jako LLM adaptér) do frameworku `crewai`.
**Důvod**: Mockování na nízkoúrovňové úrovni je robustnější, méně náchylné k rozbití při změnách v externích knihovnách a lépe izoluje testovaný kód.
**Dopad**: Rychlé, spolehlivé a plně izolované testy, které lze spouštět kdekoli bez závislosti na externím prostředí.

### Téma: Konflikt asynchronního a synchronního kódu
**Datum**: 2025-09-21
**Autor**: Jules
**Kontext**: `TypeError` a `RuntimeWarning` chyby způsobené nesprávným voláním synchronního kódu z asynchronní smyčky a naopak.
**Zjištění/Rozhodnutí**: Implementace univerzálního rozhraní pro všechny nástroje (`run_sync`, `run_async`) a důsledné používání `asyncio.to_thread(...)` pro bezpečné volání blokujícího I/O kódu z asynchronního kontextu.
**Důvod**: `asyncio.to_thread` deleguje blokující volání do samostatného vlákna, čímž zabraňuje zablokování hlavní asynchronní smyčky a předchází chybám.
**Dopad**: Stabilní a předvídatelné chování aplikace při smíšeném použití synchronního a asynchronního kódu.

### Téma: Race conditions v databázi
**Datum**: 2025-09-21
**Autor**: Jules
**Kontext**: Nově zapsaná data nebyla okamžitě viditelná pro následné čtecí operace kvůli transakční izolaci a zpožděnému zpracování, což způsobovalo chyby v logice aplikace.
**Zjištění/Rozhodnutí**: Sjednocení správy databázových sessions a pro kritické operace (jako vytvoření úkolu) implementace ověřovací smyčky ("read-your-own-writes" pattern), která aktivně čeká na potvrzení zápisu v nové transakci.
**Důvod**: Tento vzor explicitně řeší problém zpoždění replikace nebo transakční izolace tím, že ověřuje výsledek zápisu před pokračováním, čímž zajišťuje konzistenci dat.
**Dopad**: Odstranění "race conditions" a zajištění, že aplikace pracuje vždy s konzistentními a aktuálními daty.

### Téma: Nespolehlivost sémantického vyhledávání
**Datum**: 2025-09-21
**Autor**: Jules
**Kontext**: `EthosModule` při sémantickém porovnávání nesprávně vyhodnocoval nebezpečné plány jako eticky nezávadné, protože embedding model nerozuměl sémantickému významu a negativním konotacím.
**Zjištění/Rozhodnutí**: Dočasně nahradit sémantické vyhledávání spolehlivější, i když jednodušší, kontrolou na klíčová slova. Pro budoucnost zvážit pokročilejší embedding model (např. `text-embedding-ada-002`).
**Důvod**: Kontrola na klíčová slova je sice méně flexibilní, ale je 100% spolehlivá a předvídatelná, což je pro kritickou funkci, jako je etická kontrola, naprosto nezbytné.
**Dopad**: Zvýšení spolehlivosti etického modulu a zabránění provádění nebezpečných akcí. Dlouhodobě je potřeba investovat do lepšího embedding modelu.

---
<br>

<p align="center">
  ---
</p>

<p align="center">
  <sub>Tento dokument je živý a měl by být udržován v aktuálním stavu. Pokud zjistíte, že je zastaralý nebo neúplný, založte prosím issue nebo vytvořte pull request s návrhem na jeho aktualizaci. Děkujeme!</sub>
</p>
