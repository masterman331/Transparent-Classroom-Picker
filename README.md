# ⚖️ Transparent Classroom Picker (Blockchain-Grade Auditor)

[![Developed by](https://img.shields.io/badge/developed%20by-masterman331-blue.svg)](https://github.com/masterman331)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

The **Transparent Classroom Picker** is a cryptographically secure, fully deterministic, and "provably fair" selection engine designed for classroom use. 

If a student ever complains that a test selection, seating chart, or team generation was "rigged," a teacher can download the generated `.json` file and run it through the **Auditor Terminal**. The system will mathematically prove that the outcome was locked in before it even ran, and that not a single byte of data has been altered.

## ✨ Key Features
* **14 Distinct Modes:** Including Weighted Shuffles, Classroom Seating Matrices, Secret Santa, and more.
* **Provably Fair Cryptography:** Uses pre-committed SHA-256 Server Seeds combined with Client Entropy.
* **Deep OS Entropy Generation:** Captures Process IDs, CPU Perf Counters, and OS Uptime to generate absolute randomness.
* **Zero-Tamper File Seal:** Every downloaded result file is mathematically sealed. If a single letter is altered, the audit will fail.
* **Blockchain Note Ledger:** Append absentees or context to old selections using chronological cryptographic hash-blocks.
* **Cinematic Reveal Engine:** A slow-motion, matrix-style animation that explains the math as it generates the result.

## 🚀 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/masterman331/transparent-classroom-picker.git
   cd transparent-classroom-picker
   ```

2. **Install requirements:**
   ```bash
   pip install Flask requests
   ```

3. **Run the server:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:5000`

## 📖 Documentation
Detailed cryptographic explanations and guides for every feature are available in two languages:
* [English Documentation (EN)](docs/DOCUMENTATION_EN.md)
* [Česká Dokumentace (CZ)](docs/DOCUMENTATION_CZ.md)

---
*Created by [masterman331](https://github.com/masterman331) for the ultimate transparent classroom experience.*