# Protokoll 03.12.2022

- Tooling
  - Kuerze Erklaerung von Abdu, was er aufgesetzt hat

- Architektur
  - Code-Manager
    - Wrappt Ausfuehrung
    - Eingabe-Moeglichkeiten: Funktion, File, AST
    - CodeManager gibt AST weiter an Magie-Komponente, die IR/Transformation macht
    - Zweiter CodeManager wird fuer Transformierte Variante erzeugt
    - Output: Execute, Write, AST

  - Funktion:
    - Vergleich letzter Variable, maybe
    - Funktions-Parameter Typen Inference ist teilweise schwierig
    - [Inspect Module](https://docs.python.org/3/library/inspect.html) liefert Informationen zu Funktionen @ runtime
    -

  - Problem:
    - Wie vergleichen wir Code?
    - Funktionen und Ausgabewerte vergleichen macht es einfacher
    - Aber Inferieren von Typen ist schwierig
      - Woher wissen wir, dass 'df' eine DataFrame ist?!

    - Funktions-Ansatz ist gut zum Vergleichen und zum Korrektheits-Beweis
    - Am Anfang ist die Verarbeitung von Dateien/Strings einfacher
    - Moeglichkeit Angabe des Users wichtige Variable anzugeben.

- IR
  - Emani: Mega fette Baeume, Diggah
  - Kunft: Nicht besonders aussagekraeftig, high level -
  - weld.rs - Implementiert in rust, Empfehlung von Ilin --> Abdu
  - Snakes on a Plane --> Tobi
  - Putting Pandas in a Box - Grizzly --> Github Code anschauen, Alle 3 von uns
  - Ibis project --> Dave

- CST
  - Frage: Gibts es Libraries, die Relational Algebra implementieren?

- Next Steps
  - AST -> IR umbauen
  - Recherche IR
