from sqlalchemy import create_engine

def database_engine(db_name):
    engine = create_engine('sqlite:///' + db_name, encoding='utf-8')
    return engine
