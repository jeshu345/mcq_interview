from app import create_app
from app.models import db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully (if they didn't exist).")
    app.run(debug=True)
    
    
