import os
from app import create_app, db

app = create_app()

@app.cli.command()
def init_db():
    db.create_all()
    print("Database tables created!")

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')

