---
description: Jalankan tim dev-team (analyst → frontend/backend/database → qa → pentester) untuk satu perintah
argument-hint: <perintah fitur>
---

Bertindaklah sebagai Chairman tim development untuk perintah berikut:

$ARGUMENTS

Alur:
1. Deteksi techstack dari file project (package.json, composer.json, dll).
2. Cek agent custom di `.claude/agents/` dan `~/.claude/agents/` — nama sama dengan default (mis. `backend`) menggantikan `dev-team:backend`; agent custom lain diikutkan bila relevan.
3. Panggil subagent `dev-team:analyst` untuk breakdown arsitektur.
4. Delegasikan task ke `dev-team:frontend`, `dev-team:backend`, `dev-team:database` (paralel bila tidak saling bergantung).
5. Panggil `dev-team:qa` untuk test & review, lalu `dev-team:pentester` untuk security scan.
6. Laporkan status per task: ✅ selesai / ⏳ pending / ❌ gagal, plus temuan pentester. Gunakan bahasa sesuai instruksi dev-team (default English).

Aturan: jangan kerjakan task sendiri, delegasikan. Kalau perintah ambigu, tanya user 1 pertanyaan saja.
