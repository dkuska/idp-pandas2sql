# Notes - Final Presentation - 07.02.2023

## Structure taken from Ilins Slides

- Introduction
  - Topic
    - DataFrame Systems are very popular in Data Processing Pipelines and Data Science systems (Pandas, Spark, R)
    - Provide abstraction from tabular data with lots of functionalities ranging from relational algebra to statistics and linear algebra
    - Pandas is de facto standard in the Python ecosystem -> All other DataFrame libraries follow their lead and aim to mimic their API
  - Explain Problem & Motivation
    - Data Scientists/Engineers might connect to DBMS for initial data loading but do processing on the client, which could be done inside the DBMS
    - Especially Data Scientists with a non-CS background might not be familiar with all the capabilities of DBMS
    - Idea: Ship parts of the computations to the DBMS and show developers which parts of their ETL pipeline may be realized with relational algebra
    - Possible Advantages:
      - Lower Memory Footprint
      - Lower computational load on client system
      - Less Network Traffic
  - Introductory Example

- Main Phase
  - Algorithms/Implementation
    - CLI
      - Input: Source File to be optimized (has to be syntactically correct)
      - Output: Separate file with optimized code
      - Additionally information in terminal about occurring errors
    - CST-Parsing
      - Static Code Analysis
      - CST > AST, since this preserves comments/whitespaces -> Optimized code should look as similar to the original code as possible
    - IR
      - SQL-based DataFrames and operations on them create graphs in which optimization takes place
      - All necessary information to create optimized code is contained inside IR-Nodes
    - General Architecture - (Might be too many details?)
      - Orchestrator - *Main class*
      - NodeSelector
        - Responsible for traversing CST
        - Gathers information on imports, variable assignments
        - If code is detected, that fits into a interface of InputModules, delegates creation of IR-Nodes to it
      - InputModules
        - Responsible for creating IR-Nodes and mapping arguments from different semantics
      - NodeReplacer
        - Responsible for replacing old code with new code create inside IR-Nodes
      - OutputModules
        - TODO
  - Differences to current state of the art
    - 2 Types of SotA Solutions:
      1. Drop-in Replacements for Pandas
           - Modin, Dask DF
           - These offer no clarity to developers what is happening in the background
      2. DataFrame-Systems not entirely compatible with pandas with their own reimplementations  
           - Grizzly, Ibis
           - Requires developers to get used to the quirks of these APIs
    - Instead we allow users to stay inside their accustomed environment -> No need to keep relearning new frameworks
  - Evaluations

- Conclusion
  - Summary
  - Take-home message
  - Possible follow-up/ Future Extensions
    - Analysis of whole projects consisting of multiple files
    - Extension to include more operations based on relational algebra
    - More freely translate between frameworks/DataFrame semantics
