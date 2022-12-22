# Agenda

    - Vorstellung IR Dave & Feedback
    - Vorstellung Erkenntnisse Abdu und Tobias
      - Weird, dass IR den ganzen Code abbildet
      - Nodes sollen parent haben, um Baum traversieren zu koennen
      - Nicht alle Nodes muessen eine CSTNode origin haben
      - Wenn Node Kinder nicht finden kann, muessen diese dynamisch erstellt werden
      - Optimierung steht ganz weit hinten
      - If-Else TODOS werden nicht unbedingt angefasst....
      - Nicht alle Parameter von Joins werden unbedingt unterstuetzt von uns
      - Moeglicherweise SortingNodes
      - Notiz, dass Nodes geloescht werden koennen, wenn sie nicht mehr benotigt wird
      - Linting ausfuehren zum Loeschen von Nodes? Toter Code mit PyClean 
    
    - Naechste Implementierungsschritte
      - Bessere NodeType-Selektion/Node-Erstellung - Abdu und Tobi
      - Entwicklung Node-Hierarchie - Abdu und Tobi
      - Parent Nodes anstatt Origin (origin bleibt drin, wird aber erstmal nicht unbedingt benutzt) - Abdu und Tobi
      - Use Custom-Types - Tatsaechliche Types statt dicts - Abdu
      - TODOS bei den Nodes - Abdu und Tobi
      - Visit Expression - Dave