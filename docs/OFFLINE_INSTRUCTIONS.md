Istruzioni per lavorare offline con il repository RD2229

1) Copia/Clona il repository sul tuo computer (se non l'hai già fatto):

   git clone https://github.com/dancarloni/RD2229.git

2) Creare e attivare un virtualenv Python:

   python3 -m venv .venv
   source .venv/bin/activate

3) Installare dipendenze:

   pip install --upgrade pip
   pip install -r requirements.txt

4) (Opzionale) Lavorare completamente offline:

   - Rimuovi il remote `origin` per evitare accidentalmente fetch/push:

       git remote remove origin

   - Da questo punto la tua copia è locale e non richiede accesso a GitHub.

5) Eseguire test e aprire il progetto:

   pytest -q
   code .

   NOTE:
   - Se preferisci conservare una copia remota ma non connetterti, non rimuovere l'origin.
   - Se vuoi usare Docker/Dev Container senza Codespaces, usa la tua installazione Docker locale
      e la estensione "Dev Containers" di VS Code: "Reopen in Container".

   ---

   Windows (passaggi rapidi)

   - Installa Git for Windows: https://git-scm.com/download/win
   - Installa Python 3 e assicurati di aggiungerlo al PATH.
   - Apri PowerShell e esegui lo script fornito `run-local.ps1` dalla cartella dove hai scaricato i file:

      pwsh ./run-local.ps1

   Questo script:

   - clona il repository in `RD2229-local` (o nella cartella specificata)
   - crea e usa una virtualenv in `.venv` e installa le dipendenze
   - crea un branch locale `local-work` e rimuove l'upstream in modo che non sia collegato al remoto

   Per mantenere la copia remota ma evitare connessioni accidentali:

   - Lavorare su un branch locale senza upstream (`local-work`) evita push/pull involontari.
   - Disabilita il fetch automatico in VS Code: Impostazioni > Cerca `git.autofetch` -> deseleziona.
   - Evita di eseguire comandi `git fetch`, `git pull` o `git push` finché non vuoi riconnetterti.

   Se in futuro vuoi ripubblicare le modifiche sul remoto, puoi impostare di nuovo l'upstream:

      git checkout local-work
      git branch --set-upstream-to origin/main

