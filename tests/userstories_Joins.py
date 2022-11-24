import unittest

from . import magic

class Testing(unittest.TestCase):
    def test_simple(self):
        ''' 
        Explanation: 
        By default Pandas joins on the index of the dataframe ~ Row number in SQL Table.
        This results in the simple looking pandas creating a rather complex and unintuitive SQL Query.
        In PostgreSQL row_number() is a windowing functions, which requires us to specify some order (e.g. over some key).
        This affects the ordering of the output.
        
        Additionally the default join method in pandas is `left`....
        
        Since df1 and df2 are used nowhere else, they can be entirely removed from the output.
        '''
        
        input = '''
                import pandas as pd
                con = ...
                df1 = pd.read_sql("SELECT * FROM table1", con)
                df2 = pd.read_sql("SELECT * FROM table2", con)
                df3 = df1.join(df2)
                '''
        
        expected_output = '''
                ...
                df3 = pd.read_sql(""" 
                                    SELECT * 
                                    FROM (SELECT *, row_number() over (order by pk)
                                          FROM table1)B
                                          LEFT join
                                          (SELECT *, row_number() over (order by pk)
                                          FROM table2)A
                                  """)
                '''
        
        self.assertEqual(magic(input), expected_output)

    def test_df_used_later(self):
        ''' 
        Explanation: 
        df1 is used later on in the script to create df4 and cannot be removed
        df2 is not referenced later on and can be removed
        
        -> We need to track if the DataFrames are referenced somewhere else later on in the script
        
        '''

        input = '''
                import pandas as pd
                con = ...
                df1 = pd.read_sql("SELECT * FROM table1", con)
                df2 = pd.read_sql("SELECT * FROM table2", con)
                df3 = df1.join(df2)
                
                df4 = something(df1)
                
                '''
    
        expected_output = '''
                ...
                df1 = pd.read_sql("SELECT * FROM table1", con)
                
                df3 = pd.read_sql(""" 
                                    SELECT * 
                                    FROM (SELECT *, row_number() over (order by pk)
                                          FROM table1)B
                                          LEFT join
                                          (SELECT *, row_number() over (order by pk)
                                          FROM table2)A
                                  """)
                ...
                
                '''
        
        self.assertEqual(magic(input), expected_output)

        
    def test_Different_Connections(self):
        ''' 
        Explanation: 
        Joins over different Databases cannot be done Server-side!
        As such we can't optimize anything here.
        
        --> We need to track through which connections the dataframes are created
        
        '''
        
        input = '''
                import pandas as pd
                con1 = ...
                con2 = ...
                df1 = pd.read_sql("SELECT * FROM table1", con1)
                df2 = pd.read_sql("SELECT * FROM table2", con2)
                df3 = df1.join(df2)
                '''
        
        expected_output = input
        
        self.assertEqual(magic(input), expected_output)
        
        
    def test_Join_Local_DF(self):
        ''' 
        Explanation: 
        Joins with locally created DataFrames cannot be done Server-side either!
        As such we can't optimize anything here.
        
        --> We need to track the source of each Dataframe
        
        '''
        
        input = '''
                import pandas as pd
                con1 = ...
                con2 = ...
                df1 = pd.read_sql("SELECT * FROM table1", con1)
                df2 = pd.DataFrame(...)
                df3 = df1.join(df2)
                '''
        
        expected_output = input
        
        self.assertEqual(magic(input), expected_output)
        
    