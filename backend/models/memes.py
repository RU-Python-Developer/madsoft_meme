import sqlalchemy

metadata = sqlalchemy.MetaData()

memes_table = sqlalchemy.Table(
    "memes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(32)),
    sqlalchemy.Column("bucket_name", sqlalchemy.String(32)),
    sqlalchemy.Column("description", sqlalchemy.String(128)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime()),
)
