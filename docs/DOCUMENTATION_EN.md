# 📘 Complete Documentation & Cryptographic Breakdown

Welcome to the deep-dive documentation for the **Transparent Classroom Picker** by [masterman331](https://github.com/masterman331).

## 1. Application Tabs Overview

### 📋 Select Mode (Home)
This is the main entry point. Here you can search through 14 different tools using the live-search bar. Selecting a tool opens the input page where you configure your selection.

### 🗄️ History Dashboard
The application locally stores all generated selections in the `results/` folder. The History Dashboard reads these files and presents them in a clean table. 
* You can search past results.
* You can click **"View & Edit"** to see an old result.
* *Note:* You cannot change the result here, but you can append notes (e.g., "Alice was absent today") to the Blockchain Ledger.

### 🔍 Auditor Terminal
The ultimate truth engine. If anyone doubts the fairness of a result, they can upload the `.json` file here. The Auditor will recalculate every single cryptographic hash, verify the digital seal, and reproduce the modulo math. It proves the file is 100% authentic.

---

## 2. The Cryptographic Engine (How it works)

This tool does not use simple `random.choice()`. It uses **Provably Fair** architecture, identical to highly regulated transparent cryptographic systems.

### A) The Pre-Commitment (Server Seed)
Before you even enter the names, the server generates a 256-bit `Server Seed`. It immediately hashes this seed (`SHA-256`) and shows it to you on the screen. **This proves the system did not secretly change the seed after looking at the student names.**

### B) The Generation (HMAC-SHA256)
When you click generate, the system combines:
1. The **Server Seed** (Locked)
2. Your **Client Seed** (Your manual input)
3. The **External Entropy** (True atmospheric noise from Random.org, or Deep OS variables)
4. A **Nonce** (A counter that goes up by 1 for every step)

These are combined using an `HMAC-SHA256` function. The resulting Hash string is converted into a massive integer, and we use **Modulo Arithmetic** to select an index.

### C) The Absolute File Seal & Signature
Every piece of data is placed into a JSON dictionary. The system calculates a `SHA-256` hash of this entire dictionary—this is the **Global File Seal**. If someone opens the file in Notepad and changes "Bob" to "Alice", the verification hash will no longer match the seal, and the file is instantly flagged as **Tampered**.

If the Teacher provides a password, an **HMAC Signature** is also created. This proves *who* generated the file.

---

## 3. Selection Modes Explained

1. **Sequential Order:** Shuffles the whole class using the deterministic Fisher-Yates algorithm.
2. **Single Lottery:** Selects exactly 1 winner.
3. **Multi-Winner:** Shuffles the class and picks the top *N* people.
4. **Team Generator:** Shuffles the class and deals them like cards into *N* equal teams.
5. **Pairs Generator:** Matches everyone up 1-on-1.
6. **Role Assignment:** You provide roles (e.g., "Leader, Speaker"). It randomly assigns people to those specific roles.
7. **Secret Santa:** Creates a perfect mathematical derangement circle where everyone gives to the next person, and the last gives to the first. No one gets themselves.
8. **Captains / Pop Quiz:** Variants of Single/Multi lotteries tailored for classroom terminology.
9. **Weighted Raffle Draw:** Input `John:5` to give John 5 tickets in the pool.
10. **Weighted Queue Shuffle:** Input `John:100`. This uses the **A-Res Algorithm ($U^{1/W}$)**. John gets a massive weight, which pulls his fractional score closer to `1.0`, effectively pushing him toward the back of the queue (or making him less likely to be called first), while retaining cryptographic randomness.
11. **Tournament Bracket:** Generates 1v1 match-ups. Automatically gives "BYE" (Free Passes) to odd numbers.
12. **Seating Chart:** You define rows, columns, and seats per table. It generates a visual map of the classroom.

---

## 4. Understanding the Blockchain Note Ledger

If you generate a result and later need to add context (e.g., "We had to skip Bob because he went to the bathroom"), you can use the **Append to Ledger** form at the bottom of a result page.

* Every note creates a new "Block".
* Each block contains the `SHA-256` hash of the *previous* block.
* This means historical notes can never be edited or deleted without destroying the chain. 
* Appending a note requires the Teacher's Signature Password to re-seal the file.