from src.base.middleware import AuthMiddleware, RequestResponseMiddleware
from flask_http_middleware import MiddlewareManager
from src import app, api
from src.routes.admin import *
from src.routes.public import *

app.wsgi_app = MiddlewareManager(app)

app.wsgi_app.add_middleware(AuthMiddleware, app=app, settings=settings,
                            ignored_endpoints=["/register", "/login", "/options", "/features",
                                               "/apartments", "/available_apartments"])
app.wsgi_app.add_middleware(RequestResponseMiddleware, app=app, api=api, settings=settings)

# ==============================================admin routes

if __name__ == '__main__':
    app.run(debug=True, port=3000)
