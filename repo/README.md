# DigiChemJN

Interaktive Lehr-Notebooks als Open Educational Resources.
Fakultät für Chemie und Pharmazie, Universität Freiburg. CC BY-SA 4.0.

**Ohne Installation öffnen:** https://<konto>.github.io/digichemjn/
**Herunterladen:** die `.ipynb` in [`files/`](files/)

---

## Was dieses Repo ist

Zwei Dinge, die oft verwechselt werden:

1. **Die fertigen Notebooks** (`files/`) — je eine `.ipynb`-Datei, die in
   JupyterLab, JupyterLite, Colab und Binder läuft.
2. **Eine statische Website**, die aus denselben Dateien gebaut wird und sie im
   Browser ausführbar macht — JupyterLite mit Pyodide, also ein Python-Kernel
   in WebAssembly. Kein Server, kein Konto, keine Anmeldung.

Ein QR-Code auf einer Vorlesungsfolie zeigt auf die URL oben, mit dem Notebook
im Pfad. Der Student scannt, der Browser öffnet, das Notebook läuft.

**Was dabei nicht passiert:** es kommt nichts zurück. Die Arbeit des Studenten
liegt in seinem Browser-Speicher. Das ist die Grenze dieses Weges — und
gleichzeitig der Grund, warum er datenschutzrechtlich billig ist.

## Wie es gebaut wird

`.github/workflows/pages.yml` läuft bei jedem Push auf `main`:

```
files/*.ipynb  ──►  jupyter lite build  ──►  _site  ──►  GitHub Pages
                                              └─ files/ roh zum Herunterladen
```

Nichts daran ist handgemacht — wer eine neue Notebook-Version einlegt und
pusht, hat sie zwei Minuten später unter derselben URL.

### Einmal einrichten

1. Repo anlegen, diese Dateien hineinlegen, `main` pushen.
2. **Settings → Pages → Source: GitHub Actions.**
3. Fertig. Der erste Lauf baut die Seite.

## Die Quellen

Die Notebooks in `files/` sind **erzeugt**, nicht geschrieben. Jede entsteht
aus einem Bausystem: ein gemeinsames Toolkit plus eine Datei je Kapitel. Das
Bausystem liegt nicht hier, sondern im Projekt *DigiChem | Sase* als
`notebooks/quellen-buendel.txt` — 154 Dateien in einer Textdatei, aus der sich
jedes Notebook byteidentisch wiederherstellen lässt.

Wenn das Bausystem hierher soll, gehört es in einen eigenen Ordner `src/` mit
einem eigenen Workflow, der die Notebooks bei jedem Push neu baut und die
sieben Prüfsuiten laufen lässt. Das ist der nächste Schritt, nicht dieser.

## Was hier NICHT hingehört

**Fortschritts- oder Statistikdaten von Studierenden.** Drei Gründe, jeder für
sich hinreichend:

1. Ein Repo vergisst nichts. Versionsgeschichte ist bei Quellcode der Sinn und
   bei personenbezogenen Daten das Gegenteil davon — Löschen löscht nicht.
2. Ein Browser kann ohne Schreib-Token gar nicht in ein Repo schreiben, und ein
   Token in einer ausgelieferten Seite ist öffentlich.
3. Sobald Daten den Rechner des Studenten verlassen, ist es keine Speicherfrage
   mehr, sondern eine Rechtsfrage.

Siehe `notebooks/APPLIKATION-server-und-recht.md` im Projekt.

## Noch nicht gemessen

Ehrlich benannt, bevor jemand sich darauf verlässt:

- diese Notebooks auf einem **Pages-gehosteten** JupyterLite (gemessen ist
  bisher nur ein lokal gebautes)
- die Ladezeit über Hörsaal-WLAN — Pyodide plus vier Wheels sind zweistellige
  Megabyte, gleichzeitig von hundert Geräten
- **Telefone.** Unter 820 px blendet sich das Bedienpanel aus. Das Dokument
  bleibt lesbar, die Bedienung ist offen.
