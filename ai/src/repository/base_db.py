from peewee import Model, PostgresqlDatabase


def get_db():
    return PostgresqlDatabase(
        "line-ai-demo",
        user="root",
        password="password",
        host="database",
        port=5432,
    )


class BaseDBModel(Model):
    class Meta:
        database = get_db()
