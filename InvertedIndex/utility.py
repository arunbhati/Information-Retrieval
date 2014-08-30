
def normalize_line(query):
    query = query.replace("\n", "")
    query = query.replace("\t", "")
    query = query.replace("\r", "")
    return query


