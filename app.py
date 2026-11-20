from app import create_app

app = create_app()

if __name__ == "__main__":
    # Debug mode is disabled; use a production WSGI server for deployment.
    app.run(debug=False)
