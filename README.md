# ⚙️ Glorious Counter — Administratum Servitor Bot

![CI Status](https://github.com/Witherman12/MyDiscordBot/actions/workflows/bot_check.yml/badge.svg)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat&logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=flat&logo=discord&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat&logo=mongodb&logoColor=white)
![Gemini](https://img.shields.io/badge/AI-Gemini%203.5%20Flash%20Lite-8E75B2?style=flat&logo=googlegemini&logoColor=white)
![Render](https://img.shields.io/badge/Hosted%20on-Render-46E3B7?style=flat&logo=render&logoColor=black)

Ένα Discord bot με θεματολογία **Warhammer 40,000**, σχεδιασμένο για την ολοκληρωμένη διαχείριση και ψυχαγωγία community server: AI Servitor chatbot, σύστημα Levels/XP, καταγραφή μαχών & στατιστικών, εργαλεία 40k (Mathhammer, Trivia, Quotes), ημερήσιες ενημερώσεις & γενέθλια, live faction census, news scanner και πλήρη Audit Logs.

---

## ✨ Βασικές Λειτουργίες

* **🤖 AI Servitor Chatbot (`Gemini 3.5 Flash Lite`)**: Απαντάει όταν γίνεται mention με κυνικό, γραφειοκρατικό 40k roleplay. Διαβάζει δυναμικά τους **ρόλους (Factions)** του χρήστη, τηρεί αυστηρό language mirroring (Ελληνικά/Αγγλικά) και διαθέτει ειδικούς κανόνες για VIP χρήστες.
* **📊 Levels, XP & Προσευχές (`MongoDB`)**: Καταγραφή εμπειρίας μελών, leaderboard βετεράνων (`!toprank`) και ημερήσια προσευχή για bonus XP (`!pray`).
* **⚔️ Match Tracker & Στατιστικά (`MongoDB`)**: Καταγραφή νικών, ηττών και ισοπαλιών με Slash Commands και Autocomplete στρατών, Top 5 Factions και υπολογισμός Win Rate.
* **🎲 Warhammer 40k Εργαλεία**: Υπολογιστής πιθανοτήτων Mathhammer (`!math`), τυχαίες ατάκες από το lore (`!quote`) και 40k lore trivia (`!trivia`).
* **🎂 Ημερήσιες Ενημερώσεις, Καιρός & Γενέθλια**: Διαχείριση γενεθλίων μελών (`!setbday`, `!bday`, `!bdaylist`) και αυτοματοποιημένες ημερήσιες ειδοποιήσεις/καιρός μέσω `WEATHER_API_KEY`.
* **🤡 Fun & Community Utilities**: Εντολές ψυχαγωγίας, ζάρια, soundbites (`!glorious`), phrase counter (`!counter`) και 40k memes (`!overwatch`, `!sus`, `!excuse`).
* **📋 Live Faction Census**: Αυτόματη ενημέρωση πίνακα καταμέτρησης στρατών (Imperium, Chaos, Xenos) σε πραγματικό χρόνο.
* **📡 40k News Scanner**: Αυτόματη σάρωση RSS feeds (*Tabletop Battles, Auspex Tactics, Wargamer, Official Warhammer*) με φιλτράρισμα keywords για Warhammer 40k.
* **🛡️ Audit Logs & Database Backup**: Καταγραφή διαγραφών, επεξεργασιών (με `on_raw_message_edit` για παλιά/uncached μηνύματα), bans/unbans, timeouts, nicknames, ρόλων και voice activity, καθώς και εξαγωγή της MongoDB σε JSON (`/backup`).

---

## 📜 Αρχείο Εντολών (Χρήστες)

### 📊 Στατιστικά & Εμπειρία
| Εντολή | Περιγραφή |
| :--- | :--- |
| `!rank [@user]` | Εμφανίζει το Level & XP σου ή ενός άλλου παίκτη. |
| `!toprank` | Το Leaderboard με τους 9 καλύτερους βετεράνους. |
| `!pray` | Ημερήσια προσευχή για bonus XP. |

### ⚔️ Καταγραφή Μαχών & Factions
| Εντολή | Περιγραφή |
| :--- | :--- |
| `/report` | Καταγραφή νικητή/ηττημένου ή ισοπαλίας (Slash Command). |
| `/stats [Faction]` | Win Rate & ιστορικό αγώνων για συγκεκριμένο στρατό (Slash Command). |
| `/top` | Leaderboard με τα 5 καλύτερα Factions (Slash Command). |

### 🎲 Warhammer 40k Εργαλεία
| Εντολή | Περιγραφή |
| :--- | :--- |
| `!math [A] [BS] [S] [T]` | Υπολογίζει τις πιθανότητες στο Mathhammer. |
| `!quote` | Στέλνει μια τυχαία ατάκα από το lore του 40k. |
| `!trivia` | Ξεκινάει ένα γρήγορο παιχνίδι 40k lore trivia. |

### 🎂 Γενέθλια
| Εντολή | Περιγραφή |
| :--- | :--- |
| `!setbday [HH/MM]` | Δήλωσε τα γενέθλιά σου (π.χ. `!setbday 15/08`). |
| `!bday [@user]` | Δες πότε έχει γενέθλια κάποιος. |
| `!bdaylist` | Λίστα με όλα τα καταχωρημένα γενέθλια του server. |

### 🤡 Fun & Διάφορα
| Εντολή | Περιγραφή |
| :--- | :--- |
| `!glorious` | Στέλνει το Glorious MP3. |
| `!counter` | Δείχνει πόσες φορές έχει ειπωθεί Η Φράση. |
| `!roll [αριθμός]` | Ρίχνει ζάρια. Ιδανικό για να λύνετε διαφορές. |
| `!overwatch` | Όταν τα λόγια δεν αρκούν, το bot φέρνει Flamers. |
| `!excuse` | Το bot σου δίνει την τέλεια δικαιολογία. |
| `!sus [reply ή @user]` | Δικάζει δημόσια όποιον στέλνει περίεργο περιεχόμενο. |

---

## 🛑 Inquisitorial Vault (Admin Commands)

Εντολές αυστηρά περιορισμένες για το High Command του Server.

### ⚙️ Σύστημα & Δεδομένα
| Εντολή | Περιγραφή |
| :--- | :--- |
| `!setlevel [@user] [level]` | Ορίζει χειροκίνητα το Level κάποιου παίκτη. |
| `!setbday [HH/MM] [@user]` | Ορίζει ή αλλάζει τα γενέθλια κάποιου μέλους. |
| `/undo_report` | Διαγράφει έναν αγώνα που καταγράφηκε λάθος (Slash Command). |
| `/backup` | Κατεβάζει όλη τη βάση δεδομένων σε JSON αρχείο (Slash Command). |
| `!setup_roles` | Δημιουργεί/Ενημερώνει το Live Panel καταμέτρησης των Factions. |

### 🎭 Επικοινωνία, Roleplay & AI
| Εντολή | Περιγραφή |
| :--- | :--- |
| `!say [#κανάλι] [κείμενο]` | Το bot στέλνει το κείμενό σου στο κανάλι. |
| `!reply [LINK_ΜΗΝΥΜΑΤΟΣ] [κείμενο]` | Το bot κάνει απευθείας reply στο μήνυμα. |
| `!on` / `!off` | Ενεργοποιεί ή απενεργοποιεί (Sleep Mode) το AI chatbot. |
| `!reset` | Καθαρίζει τη μνήμη συζητήσεων του AI (Memory Wipe). |

### 🔨 Moderation & Ποινές
| Εντολή | Περιγραφή |
| :--- | :--- |
| `!void [@user]` | Στέλνει τον χρήστη στο Void. |

---

## 📂 Δομή Project

```text
.
├── .github/
│   └── workflows/
│       └── bot_check.yml      # GitHub Actions CI έλεγχοι πριν το deploy
├── cogs/
│   ├── chat.py                # AI Servitor (Gemini), δυναμικοί ρόλοι & puppet commands
│   ├── daily.py               # Ημερήσιες ενημερώσεις, καιρός & σύστημα γενεθλίων
│   ├── fun.py                 # 40k εργαλεία (!math, !quote, !trivia) & fun εντολές
│   ├── levels.py              # Σύστημα XP, !rank, !toprank, !pray & !setlevel
│   ├── logs.py                # Audit Logs (messages, voice, roles, moderation)
│   ├── news.py                # Αυτόματος 40k RSS News Scanner
│   ├── roles.py               # Διαχείριση ρόλων & Live Faction Census
│   └── stats.py               # /report, /stats, /top, /undo_report & /backup
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