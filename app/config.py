import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_db_url():
        url = os.environ.get('DATABASE_URL', 'sqlite:///medi_share_dev.db')
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif url.startswith('postgresql://'):
            url = url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        return url

    SQLALCHEMY_DATABASE_URI = get_db_url.__func__()
