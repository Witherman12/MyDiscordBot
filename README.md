# ⚙️ Glorious Counter — Administratum Servitor Bot

![CI Status](https://github.com/USERNAME/REPO/actions/workflows/bot_check.yml/badge.svg)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat&logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=flat&logo=discord&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat&logo=mongodb&logoColor=white)
![Gemini](https://img.shields.io/badge/AI-Gemini%203.5%20Flash%20Lite-8E75B2?style=flat&logo=googlegemini&logoColor=white)
![Render](https://img.shields.io/badge/Hosted%20on-Render-46E3B7?style=flat&logo=render&logoColor=black)

Ένα Discord bot με θεματολογία **Warhammer 40,000**, σχεδιασμένο για τη διαχείριση community server: καταγραφή αγώνων και στατιστικών στρατών, AI chatbot με προσωπικότητα Servitor, live καταμέτρηση factions, αυτόματη ενημέρωση νέων 40k, πρόγνωση καιρού και πλήρες σύστημα Audit Logs.

---

## ✨ Βασικές Λειτουργίες

* **🤖 AI Servitor Chatbot (`Gemini 3.5 Flash Lite`)**: Απαντάει όταν γίνεται mention, διατηρώντας κυνικό, γραφειοκρατικό 40k roleplay. Διαβάζει δυναμικά τους **ρόλους (Factions)** του χρήστη για να προσαρμόζει τη συμπεριφορά του, τηρεί αυστηρό language mirroring (Ελληνικά/Αγγλικά) και διαθέτει ειδικούς κανόνες για VIP χρήστες.
* **⚔️ Match Tracker & Στατιστικά (`MongoDB`)**: Καταγραφή νικών, ηττών και ισοπαλιών με Slash Commands και Autocomplete για όλους τους 40k στρατούς, leaderboard Top 5 και αυτόματο υπολογισμό Win Rate.
* **📊 Live Faction Census**: Αυτόματη ενημέρωση πίνακα καταμέτρησης στρατών (Imperium, Chaos, Xenos) σε πραγματικό χρόνο.
* **📡 40k News Scanner**: Αυτόματη σάρωση RSS feeds (*Tabletop Battles, Auspex Tactics, Wargamer, Official Warhammer*) με φιλτράρισμα keywords για Warhammer 40k.
* **🌦️ Weather Module**: Ενημέρωση καιρού μέσω εξωτερικού Weather API.
* **🛡️ Audit Logs**: Καταγραφή διαγραφών, επεξεργασιών (με `on_raw_message_edit` ώστε να πιάνει και παλιά μηνύματα μετά από restart), αποχωρήσεων, bans/unbans, timeouts, αλλαγών nickname, χειροκίνητων αλλαγών ρόλων και δραστηριότητας σε Voice Channels.
* **💾 Database Backup**: Εξαγωγή ολόκληρης της βάσης MongoDB σε αρχείο `.json` (εξαιρώντας το collection `news`).

---

## 📜 Εντολές

### Slash Commands
| Εντολή | Περιγραφή | Δικαιώματα |
| :--- | :--- | :--- |
| `/report` | Καταγραφή αποτελέσματος αγώνα 40k (νίκη ή ισοπαλία) με Autocomplete στρατών. | Όλοι |
| `/stats` | Προβολή Win Rate, Wins, Losses και Ties για συγκεκριμένο στρατό. | Όλοι |
| `/top` | Εμφάνιση του Top 5 των Factions με βάση τις νίκες. | Όλοι |
| `/undo_report` | Αναίρεση αγώνα που καταγράφηκε κατά λάθος. | `Manage Messages` |
| `/backup` | Κατέβασμα αντιγράφου ασφαλείας της MongoDB σε JSON (χωρίς τα news). | `Administrator` |

### Prefix Commands (High Command / Utilities)
| Εντολή | Περιγραφή |
| :--- | :--- |
| `!adminhelp` | Εμφανίζει το Inquisitorial Vault με όλες τις εντολές διαχείρισης. |
| `!setup_roles` | Δημιουργεί ή ενημερώνει το Live Panel καταμέτρησης των Factions. |
| `!setlevel [@user] [level]` | Ορίζει χειροκίνητα το Level ενός μέλους. |
| `!setbday [ΗΗ/ΜΜ] [@user]` | Ορίζει ή αλλάζει τα γενέθλια ενός μέλους. |
| `!weather [πόλη]` | Εμφανίζει τρέχουσες καιρικές συνθήκες (μέσω `WEATHER_API_KEY`). |
| `!on` / `!off` | Ενεργοποιεί ή βάζει σε Sleep Mode το AI chatbot. |
| `!reset` | Καθαρίζει τη μνήμη συζητήσεων του AI (Memory Wipe). |
| `!say [#κανάλι] [κείμενο]` | Στέλνει μήνυμα ως το bot σε συγκεκριμένο κανάλι. |
| `!reply [link] [κείμενο]` | Κάνει απευθείας reply ως το bot σε συγκεκριμένο μήνυμα. |
| `!void [@user]` | Στέλνει τον χρήστη στο Void. |

---

## 📂 Δομή Project

```text
.
├── .github/
│   └── workflows/
│       └── bot_check.yml      # GitHub Actions CI έλεγχοι πριν το deploy
├── cogs/
│   ├── stats.py               # /report, /stats, /top, /undo_report, /backup
│   ├── roles.py               # Διαχείριση ρόλων & Live Faction Census
│   ├── chat.py                # AI Servitor (Gemini), δυναμικοί ρόλοι & puppet commands
│   └── logs.py                # Audit Logs (messages, voice, roles, moderation)
├── tests/
│   └── check_emojis.py        # Έλεγχος εγκυρότητας Discord emojis
├── main.py                    # Κεντρικό αρχείο εκκίνησης του bot
├── requirements.txt           # Python dependencies
├── .env.example               # Πρότυπο environment variables
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🛠️ Ρύθμιση & Environment Variables

Το bot τρέχει σε **Python 3.14** και φιλοξενείται στο **Render** με βάση **MongoDB Atlas**.

### 1. Αντιγραφή του `.env.example` σε `.env`
```env
DISCORD_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
WEATHER_API_KEY=your_weather_api_key_here
PYTHONUNBUFFERED=1
```

### 2. Τοπική Εγκατάσταση & Εκκίνηση
```bash
pip install -r requirements.txt
python main.py
```

---

## 🧪 Testing & CI/CD Pipeline

Κάθε push στο `main` ενεργοποιεί αυτόματα το workflow **`Servitor Code Inspection`** στο GitHub Actions:
1. **`python -m compileall -q .`** — Έλεγχος για `SyntaxError` και `IndentationError`.
2. **`ruff check --select=F63,F7,F82 .`** — Έλεγχος για χαμένα imports και αδήλωτες μεταβλητές.
3. **`python tests/check_emojis.py`** — Έλεγχος για invalid Discord shortcodes (π.χ. `:japanese_ogre:`) ή κατεστραμμένα custom emoji IDs.

Το Render είναι ρυθμισμένο σε **Auto-Deploy: After CI Checks Pass**, ώστε να αποτρέπονται άσκοπα restarts και Cloudflare `429` rate limits σε περίπτωση σφάλματος.

### Τοπικός Έλεγχος πριν από Push
```bash
python -m compileall -q .
python tests/check_emojis.py
```

---

## 📄 License & Disclaimer

Αυτό το project διατίθεται υπό την άδεια **[GNU General Public License v3.0 (GPLv3)](LICENSE)**.

> *Disclaimer: Ανεπίσημο fan-made project. Το Warhammer 40,000 και όλα τα σχετικά ονόματα/factions αποτελούν πνευματική ιδιοκτησία της Games Workshop Ltd.*