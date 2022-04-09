from flaskr import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
else:
    gunicorn_app = create_app()

# gunicorn --bind 127.0.0.1:5000 appserver:gunicorn_app
