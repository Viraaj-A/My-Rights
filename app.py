from __init__ import init_app

app = init_app()

Development = True

if Development == False:
    if __name__ == "__main__":
        from waitress import serve
        serve(app, host="0.0.0.0", port=8080)

else:
    if __name__ == "__main__":
        app.run(debug=True)
