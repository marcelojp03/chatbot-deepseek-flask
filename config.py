class Config:
    debug=True

    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/dbinf342'
    # SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://openpg:openpgpwd@localhost:5432/BDCENTRAL'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:admin123*@localhost:5432/TOPICOSDB'
    #SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:admin123*@db:5432/BDCENTRAL'
    #SQLALCHEMY_DATABASE_URI= 'postgresql+psycopg2://postgres:admin123*@host.docker.internal:5432/BDCENTRAL'
    #SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SQLALCHEMY_ECHO = True
    #SQLALCHEMY_RECORD_QUERIES = True
    JWT_SECRET_KEY='ficct'
