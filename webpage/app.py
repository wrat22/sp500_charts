from flask import Flask

from routes import main_routes
from api import api_routes
from extensions import cache


app = Flask(__name__)

cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})

main_routes.cache = cache

app.register_blueprint(main_routes)
app.register_blueprint(api_routes)


if __name__ == "__main__":
    app.run(debug=True)
