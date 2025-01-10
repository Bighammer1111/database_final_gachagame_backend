from app.__init__ import create_app


if __name__ == '__main__':
    app = create_app()
    for rule in app.url_map.iter_rules():
        print(rule.endpoint, rule.methods, rule.rule)
    print("Starting the Flask application")
    app.run(host="0.0.0.0", port=6000, debug=True)
