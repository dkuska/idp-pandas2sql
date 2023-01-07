# ToDos IDP-Project

- Intermediate Presentation - 2023_01_10
  - Progress so far:
    - IR
  - Problems encountered:
    - AST/CST
    - IR
    - Optimization
    - Code Generation
  - Class Diagram IR

- IR
  - Aggregations
  - Parameter der einzelnen Optionen
  - Erweiterbarkeit? Wie umsetzen?
    - Offenes Interface, um andere Pandas Operationen abzufangen?
    - Sollte equivalent zu Pandas sein, aber auch Plattformunabhaengig sein
  - Deletion mit Linting erkennen?

- Code Generation/ Output Generation
  - IR -> CST/Str

- Test Cases/ Automated Test Setup
  - Test-Cases definieren
  - Richtigkeit bestimmt durch der Korrektheit/Gleichheit der Ergebnisse
  - File/Funktion Angeben
  - Erstellung NodeSelector
  - Optimierungen/Magie
  - Ausgabe neuer Code in neue Datei

- Join
  - Joins on Keys
  - Wichtige Parameter: On, How, Join

- Aggregations
  - Welche Aggregationen gibt es ueberhaupt in Pandas?
    - Min, Max, Mean, Median,
  - Nicht df.aggregate! Die nimmt ein UDF!
  - Bedarf auf jeden Fall die Queries anzufassen und auseinanderzunehmen

Fragen an Ilin:

- Was sind aggregations fuer uns?
- Muessen wir die gesamte Pandas API uebernehmen?
- Erweiterbarkeit
  - Viel Arbeit
  - Payoff unsicher
  - War unsere Praemisse

Next Steps:
- Not be focussed on DataFrames
- DB Libraries
- Join: On, How, Sort
- Aggregations:
