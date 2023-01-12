# Notes on Intermediate Representations

## Literature Research

### Grizzly - Klaebe & Hagedorn

- [Link to repo](https://github.com/dbis-ilm/grizzly)
- Custom 'dataframe' type which mimics Pandas Dataframe behavior
- 'Whole' project seems to be contained in a single file xD
- Lazy Evaluation
- For SQL Integration uses query templates, which are not publically available as it seems

- Attributes:
  - index - Optional parameter, no default assigned
  - columns
  - computedColumns
  - parents - other DataFrame objects, this one is based on. Not sure where and how this is used

- Join Behavior
  - Join Columns need to be specified (different from pandas, where default behavior is joining on index column)

- Aggregations
  -

- SQL Interaction
  - RelationalExecutor object which manages DB connection
  - SQLGenerator manages query preconditions and actually builds the query strings
  - One big, nested function for query generation

### IBIS Project

- Very complicated implementation
- Internal data structure not necessarily similar to pandas DataFrames

### Weld

- It has the same vision we have
- Its intermediate representation is an imperative language that uses builders, mergers, etc.
- It doesn't understand SQL, only library functions
- No code available

## Considerations for our IR

- Grizzly seems like a good starting point
- In addition keeping the source AST/CST Node would be nice to do 'inplace' replacements, however this could increase the memory consumption significantly
-
