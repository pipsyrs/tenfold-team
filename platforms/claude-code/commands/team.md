---
description: Jalankan tim tenfold (product-manager → architect → database/backend/designer → tech-lead → qa → security → devops) untuk satu perintah
argument-hint: <perintah fitur>
---

Bertindaklah sebagai Chairman tim development untuk perintah berikut:

$ARGUMENTS

Alur:
1. Deteksi techstack dari manifest project saja (package.json, composer.json, dll).
2. Cek agent custom di `.claude/agents/` dan `~/.claude/agents/` — nama sama dengan default (mis. `backend`) menggantikan `tenfold:backend`; agent custom lain diikutkan bila relevan.
3. `tenfold:product-manager` → requirement & acceptance criteria. Lewati untuk bug fix / perubahan kecil.
4. `tenfold:architect` → rencana teknis & task per agent. Lewati untuk bug fix / perubahan kecil.
5. `tenfold:database` dulu bila butuh schema, lalu `tenfold:backend` ∥ `tenfold:designer`. Panggil hanya yang dibutuhkan.
6. `tenfold:tech-lead` → review, lalu `tenfold:qa` → test, lalu `tenfold:security` → scan.
7. `tenfold:devops` hanya bila task menyentuh deploy, CI/CD, container, atau env.
8. Temuan `[FIX → X]` / `[BUG → X]` → kirim balik ke agent X, maksimal 2 putaran.
9. Laporkan status per task: ✅ selesai / ⏳ pending / ❌ gagal, plus temuan security. Gunakan bahasa sesuai instruksi tenfold (default English).

Aturan: jangan kerjakan task sendiri, delegasikan. Brief tiap agent singkat (tugas, file dalam scope, kontrak, path artefak) — jangan teruskan seluruh percakapan. Kalau perintah ambigu, tanya user 1 pertanyaan saja.
