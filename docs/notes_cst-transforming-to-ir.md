# Notes cst-transforming-to-ir

- `aggregate` function on DFs cannot generally be translated by us, as this takes a UDF. This can only be done for a handful of functions that have a 'canonical' SQL equivalent: `np.sum`, `mean` etc.
- We might have to ask Ilin about this, as I think he had functions like `min`, `max`, `mean` in mind.

- `NotImplementedError` will never be thrown, as the CSTVisitor has all `visit_XY` methods implemented in some fashion. They are not `empty` per se but rather call the respective functions for the children/attributes of the nodes

- In the NodeSelector is `imported_pandas_aliases` doing what it is supposed to? This would contain the pandas functions that are imported and not exactly 'aliases'
- `visit_Assign` does not handle cases where one Call has multiple return values. Does this actually occur with our relevant Pandas functions?
- `SQLNode.sql` is a CSTNode and during execution it is passed a SimpleString on which you can easily call `.value` and be done. This does not work when you do something like `sql_string = '...'; df = pd.read_sql(sql_string, con)`. In these cases we need to give the Assign Nodes access to `NodeSelector.variables` to fill in the statically assigned variables.
- However for more complicated cases such as f-strings, this approach will blow up in our faces. Nothing to do for now but rather for the future. We need to talk about expectation management with Ilin. We are doing static code analysis, we cannot know the value of variables at runtime.
- For Aggregations we need to further analyze the SQL-String and cannot assume `SELECT * ...` anymore. Does this make sense for the Join case also?
