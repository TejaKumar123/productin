from product import app,db

if __name__=="__main__":
    with app.app_context():
        db.create_all()
        app.run(port=3000,debug=True)
