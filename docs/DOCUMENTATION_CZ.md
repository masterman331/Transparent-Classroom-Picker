# 📘 Kompletní Dokumentace a Kryptografický Rozbor

Vítejte v detailní dokumentaci k aplikaci **Transparent Classroom Picker** (Transparentní třídní losovač), kterou vytvořil [masterman331](https://github.com/masterman331).

## 1. Přehled záložek aplikace (Tabs)

### 📋 Select Mode (Výběr režimu)
Hlavní vstupní bod aplikace. Pomocí vyhledávacího pole můžete prohledávat 14 různých nástrojů. Výběrem nástroje se otevře stránka, kde nastavíte parametry pro váš výběr.

### 🗄️ History Dashboard (Historie)
Aplikace lokálně ukládá všechny vygenerované výběry do složky `results/`. Tato záložka tyto soubory načte a zobrazí je v přehledné tabulce.
* Můžete vyhledávat v minulých výsledcích.
* Kliknutím na **"View & Edit"** (Zobrazit a upravit) otevřete starší výsledek.
* *Poznámka:* Samotný výsledek (los) zde nelze změnit, ale můžete přidávat poznámky (např. "Alenka dnes chyběla") do tzv. Blockchain Ledgeru (Knihy poznámek).

### 🔍 Auditor Terminal (Auditorský terminál)
Ultimátní nástroj pro ověření pravdy. Pokud má někdo pochybnosti o férovosti výsledku, stačí zde nahrát `.json` soubor. Auditor přepočítá každý kryptografický hash, ověří digitální pečeť a zopakuje veškerou matematiku (modulo). Tím prokáže, že soubor je 100% autentický.

---

## 2. Kryptografické jádro (Jak to funguje)

Tento nástroj nepoužívá jednoduchou funkci `random.choice()`. Využívá architekturu **Provably Fair** (Prokazatelně spravedlivou), která je identická s přísně regulovanými transparentními systémy.

### A) Závazek předem (Server Seed)
Ještě než zadáte jména, server vygeneruje 256bitový `Server Seed`. Tento seed okamžitě zahashuje pomocí `SHA-256` a zobrazí vám ho na obrazovce. **To dokazuje, že systém po přečtení jmen studentů tajně nezměnil výchozí hodnotu (seed).**

### B) Generování (HMAC-SHA256)
Když kliknete na tlačítko "Generate", systém zkombinuje:
1. **Server Seed** (Uzamčený z předchozího kroku)
2. Váš **Client Seed** (Váš vlastní náhodný text)
3. **Externí Entropii** (Skutečný atmosférický šum z Random.org nebo hluboké systémové proměnné OS)
4. **Nonce** (Počítadlo, které se s každým krokem zvyšuje o 1)

Tyto hodnoty jsou spojeny pomocí funkce `HMAC-SHA256`. Výsledný hash je převeden na obrovské celé číslo a k výběru konkrétního jména se použije **Modulo matematika** (zbytek po dělení).

### C) Absolutní pečeť souboru a Podpis
Všechna data jsou uložena do formátu JSON. Systém vypočítá `SHA-256` hash celého tohoto dokumentu – to je **Globální pečeť souboru (Global File Seal)**. Pokud někdo otevře soubor v Poznámkovém bloku a změní "Bob" na "Alice", ověřovací hash už nebude sedět s pečetí a soubor je okamžitě označen za **Zmanipulovaný (Tampered)**.

Pokud učitel zadá heslo, vytvoří se navíc **HMAC Podpis**. Ten dokazuje, *kdo* přesně soubor vygeneroval.

---

## 3. Vysvětlení režimů výběru

1. **Sequential Order:** Zamíchá celou třídu pomocí deterministického Fisher-Yatesova algoritmu.
2. **Single Lottery:** Vybere přesně 1 výherce.
3. **Multi-Winner:** Zamíchá třídu a vybere prvních *N* lidí.
4. **Team Generator:** Zamíchá třídu a rozdělí je jako karty do *N* vyrovnaných týmů.
5. **Pairs Generator:** Vytvoří dvojice (1 na 1).
6. **Role Assignment:** Zadáte role (např. "Vedoucí, Mluvčí"). Systém náhodně přiřadí lidi k těmto konkrétním rolím.
7. **Secret Santa:** Vytvoří dokonalý matematický kruh (derangement), kde každý dává dárek dalšímu a poslední dává prvnímu. Nikdo si nevytáhne sám sebe.
8. **Captains / Pop Quiz:** Varianty jednoduché/vícenásobné loterie přizpůsobené školní terminologii (Zkoušení / Kapitáni).
9. **Weighted Raffle Draw:** Zadejte `Jan:5`, čímž získá Jan 5 lístků v osudí.
10. **Weighted Queue Shuffle:** Zadejte `Jan:100`. Tento režim využívá matematický algoritmus **A-Res ($U^{1/W}$)**. Jan dostane obrovskou váhu, což posune jeho desetinné skóre blíže k hodnotě `1.0`. Tím se efektivně odsouvá na konec fronty (je mnohem méně pravděpodobné, že půjde k tabuli první), ale kryptografická náhodnost zůstává zachována.
11. **Tournament Bracket:** Vygeneruje pavouka pro turnaje 1v1. Lichým číslům automaticky přidělí "BYE" (Volný postup).
12. **Seating Chart:** Definujete řady stolů, sloupce a počet míst u stolu. Systém vygeneruje vizuální mapu zasedacího pořádku (rozsazení třídy).

---

## 4. Jak funguje Blockchain kniha poznámek (Note Ledger)

Pokud vygenerujete výsledek a později potřebujete přidat kontext (např. "Bob byl na záchodě, takže jsme ho museli přeskočit"), můžete použít formulář **Append to Ledger** na spodní straně výsledku.

* Každá nová poznámka vytvoří nový "Blok".
* Každý blok obsahuje `SHA-256` hash *předchozího* bloku.
* To znamená, že staré poznámky nelze nikdy upravit nebo smazat, aniž by se rozbil celý řetězec.
* K přidání poznámky je nutné heslo učitele (podpis), aby se soubor mohl znovu bezpečně zapečetit.

> **Upozornění:**
> Tento projekt byl vytvořen stylem „vibe codingu“, proto jej používejte s opatrností. – Masterman331
