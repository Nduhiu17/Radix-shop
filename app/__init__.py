from flask import Flask, jsonify, Blueprint  # importing flask
from flask_cors import CORS
from flask_restplus import Api
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig
from werkzeug.contrib.fixers import ProxyFix

authorization = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'Header',
        'name': 'Authorization'
    }
}

app = Flask(__name__)
jwt = JWTManager(app)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
CORS(app)


app.config.from_object(DevelopmentConfig)
blueprint = Blueprint('api', __name__)
blueprint_2 = Blueprint('home', __name__)
blueprint_3 = Blueprint('auth', __name__)

api_v1 = Api(blueprint, title='Radix Shop manager', version='1',
             description='Radix Shop manager is a web application that helps shop owners manage sales and product inventory records. This application is meant for use in a single store.Provide token to the secured endpoints.e.g Bearer yourtoken',
             authorizations=authorization, )
api_home = Api(blueprint_2,
               title='Radix Shop manager',
               version='1',
               description='Radix Shop manager is a web application that helps shop owners manage sales and product inventory records. This application is meant for use in a single store. e.g `Bearer yourtoken`<br>Click on models to view samples of data input',
               authorizations=authorization,
               doc='/docv/',
               base_url="/"
               )

app.register_blueprint(blueprint)

jwt._set_error_handler_callbacks(api_v1)





@app.errorhandler(404)
def error_404(e):
    '''This method handles error 404'''
    return jsonify({"message": "Sorry!!!The page you were looking for was not found.Kindly countercheck the url"}), 404

@app.errorhandler(405)
def error_404(e):
    '''This method handles error 404'''
    return jsonify({"message": "Operation not allowed to that url"}), 405


from app import views

