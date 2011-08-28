def csql(self,query,qkeys):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # build dict for template:
    fdicts = []
    for row in rows:
        i = 0
        cur_row = {}
        for key in qkeys:
            cur_row[key] = row[i]
            i = i+1
        fdicts.append(cur_row)
    return fdicts