def pipeline_with_join():
    import sqlite3

    import pandas as pd

    # Example data from https://www.sqlitetutorial.net/sqlite-sample-database/
    con = sqlite3.connect("data/chinook.db")

    media_types = pd.read_sql_query("SELECT * from media_types", con)
    tracks = pd.read_sql_query("SELECT * from tracks", con)
    con.close()

    print(tracks.merge(media_types, on="MediaTypeId", how="inner"))


def pipeline_with_filter():
    import sqlite3

    import pandas as pd

    # Example data from https://www.sqlitetutorial.net/sqlite-sample-database/
    con = sqlite3.connect("data/chinook.db")

    invoice_items = pd.read_sql_query("SELECT * from invoice_items", con)
    con.close()

    print(invoice_items[invoice_items["UnitPrice"] == 1.99])
