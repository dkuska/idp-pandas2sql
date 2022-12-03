
# Protokoll 24.11

    - Acceptance Tests schreiben fuer minimale Examples -> I. zeigen, was wir umsetzen wollen
    - Input-Seite: pandas, modin, etc.
    - Output-Seite: PostgreSQL, T-SQL, andere Dialekte, etc.

    - CST ist guter Startpunkt fuer Source-Analyse

    - Limitierung: Cross-database joins cannot be pushed to the server side
    - Gedanke fuer spaeter: Do Aggregations/Joins in Pandas and Database produce the same results?!
    - top(order(R)) != order(top(R))

    - Ziel: Gemeinsame Vision entwickeln, Gemeinsame Ziele abstecken

    - Grundlegende Pipeline:
        src -> AST/CST -> IR -> AST/CST -> output

        Optimierung passiert innerhalb der IR

        Idee: Pandas2Pandas, maybe to optimize

    - 2 Ansaetze:
        - IR bildet komplette Kontrollstruktur ab
        src -> AST/CST -> IR -> optimized AST/CST -> output

        - IR bildet nur Relationale Komponenten ab
        src -> AST/CST -> IR + AST/CST -> optimized AST/CST -> output

    - Hausaufgabe: Unit-Tests/Acceptance-Tests/User Stories schreiben
        - Einfache und komplexe Beispiele
        - Was geht, was geht nicht
        - Zur Kommunikation mit I.; nicht formalisiert

    - Ziele kommende Besprechung mit Ilin:
        - Research Paper fuer Intermediate Representations (IR)
        - AST vs. CST (libCST)
        - Scope abstecken/ expectation management
