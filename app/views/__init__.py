import re
from datetime import datetime

from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_restplus import Resource, reqparse
from flask_restplus import fields

from app import api_v1
from app.models import Sale, Product, User, UserPermission, Stock, SaleStock, SoldStock
from utils.validator import Validate

api_v1.namespaces.clear()

ns = api_v1.namespace('api/v1',
                      description='End points regarding Sale operations')
ns1 = api_v1.namespace('api/v1/auth',
                       description='End points regarding User operations')
ns2 = api_v1.namespace('api/v1',
                       description='End points regarding Product operations')

ns3 = api_v1.namespace('api/v1/products',
                       description='End points regarding Product operations')

sale_fields = api_v1.model('Sale', {
    'buyer_name': fields.String
})


@ns.route('/sales')
class SaleResource(Resource):
    '''Get all sales resource'''

    @ns.doc(security='apiKey')
    @jwt_required
    def get(self):
        '''Get all sales ever created.Admin only'''
        user_logged_in = get_jwt_identity()
        if not User.isAdmin(user_id=user_logged_in):
            return {"error": 401, "message": "Not authorized.Admin only."}
        if "search" in request.args:
            sales_found = Sale.search_closed_sales(self, username=request.args['search'])
            if sales_found:
                return {"message": "Sales found", "data": sales_found}, 200
            return {"message": "No sales found"}, 404

        all_sales = Sale.get_all()

        return {"message": "Ok", "data": all_sales}, 200

    @api_v1.expect(sale_fields)
    @ns.doc(security='apiKey')
    @jwt_required
    def post(self):
        '''Create a sale'''
        parser = reqparse.RequestParser()
        parser.add_argument('buyer_name', help='The product field cannot be blank',
                            required=True, type=str)
        data = parser.parse_args()
        logged_in_user = User.get_by_id(get_jwt_identity())['username']
        sale = Sale(id=None, buyer_name=data['buyer_name'], status='open', created_by=logged_in_user,
                    date_created=str(datetime.now()), date_modified=str(datetime.now()))

        sale.save()
        posted_sale = dict(buyer_name=data['buyer_name'], status='open',
                           created_by=User.get_by_id(id=get_jwt_identity()), date_created=str(datetime.now()),
                           date_modified=str(datetime.now()))
        return {"message": "Sale created", "data": posted_sale}


@ns.route('/sales?search=<string:string>')
class SaleResource(Resource):
    '''Get all sales resource'''

    @ns.doc(security='apiKey')
    @jwt_required
    def get(self):
        '''Search all sales of a given user,admin only'''
        pass


@ns.route('/sales/closed')
class SaleResource(Resource):
    '''Get all products resource'''

    @ns.doc(security='apiKey')
    @jwt_required
    def get(self):
        '''Get all closed sales'''
        user_logged_in = get_jwt_identity()
        if not User.isAdmin(user_id=user_logged_in):
            return {"error": 401, "message": "Not authorized.Admin only."}
        all_sales = Sale.get_all_closed_sales()

        return {"message": "Ok", "data": all_sales}, 200


@ns.route('/sales/closed/usersales')
class SaleResource(Resource):
    '''Get all sales for the logged in user'''

    @ns.doc(security='apiKey')
    @jwt_required
    def get(self):
        '''Get all closed sales for a user'''
        if 'user' in request.args:
            try:
                user_to_search = User.get_by_id(request.args['user'])['username']
            except:
                return {"error": 404, "message": "No user found with that id"}, 404
            logged_user = User.get_by_id(id=get_jwt_identity())['username']
            if user_to_search == logged_user or User.isAdmin(user_id=get_jwt_identity()):
                user_sales = Sale.get_all_user_closed_sales(username=user_to_search)
                if user_sales:
                    return {"message": "Success", "data": user_sales}, 200
                return {"error": 404, "message": "The user has no closed sales yet"}
            return {"message": "Unauthorized.Only admin or sale owner can access"}, 401


@ns.route('/sales/<int:sale_id>')
class SaleResource(Resource):
    '''Get all products resource'''

    @ns.doc(security='apiKey')
    @jwt_required
    def get(self, sale_id):
        '''Get a sale by id'''
        sale = Sale.get_by_id(sale_id)
        if sale is None:
            return {"error": 404, "message": "sale not found"}, 404
        logged_user = User.get_by_id(id=get_jwt_identity())['username']
        if logged_user == sale.created_by or User.isAdmin(user_id=get_jwt_identity()):
            sale_json = sale.json_dump()
            sale_json["products"] = SaleStock.get_sale_stocks(sale_id=sale_id)
            return {"message": "Ok", "data": sale_json}, 200
        return {"message": "You are not authorised.Only admin or sale owner can get the sale"}, 401

    @ns.doc(security='apiKey')
    @jwt_required
    def put(self, sale_id):
        '''Close a sale)'''

        sale = Sale.get_by_id(sale_id)

        if sale is None:
            return {"error": 404, "message": "sale not found"}
        logged_user = User.get_by_id(id=get_jwt_identity())['username']
        if logged_user == sale.created_by or User.isAdmin(user_id=get_jwt_identity()):
            sale = Sale.get_by_id(sale_id)
            sale_json = sale.json_dump()
            sale_json["products"] = SaleProduct.get_sale_products(sale_id=sale.id)
            if not sale_json["products"]:
                return {"Error": 400, "message": "You can't close a sale with no products"}, 400
            if sale.status == "submitted":
                return {"Error": 400, "message": "The sale is already closed"}, 400
            sale.submit()
            sale = Sale.get_by_id(sale_id)
            sale_json = sale.json_dump()
            sale_json["products"] = SaleProduct.get_sale_products(sale_id=sale.id)
            return {"message": "successfuly closed the sale", "data": sale_json}, 200
        return {"message": "Unauthorized,only an admin or sale owner can add products to a sale"}, 401

    @ns.doc(security='apiKey')
    @jwt_required
    def delete(self, sale_id):
        '''Delete a sale record'''
        sale = Sale.get_by_id(sale_id)
        if sale is None:
            return {"error": 404, "message": "sale not found"}, 404

        logged_user = User.get_by_id(id=get_jwt_identity())['username']
        if logged_user == sale.created_by or User.isAdmin(user_id=get_jwt_identity()):
            if sale.status == "deleted":
                return {"error": 400, "message": "The sale record has already been deleted"}, 400
            sale.cancel()
            return {"response": 204, "message": "successfully deleted"}, 204
        return {"message": "You are not authorised.Only admin or sale owner can delete a sale"}, 401

    @ns.doc(security='apiKey')
    @jwt_required
    def post(self, sale_id):
        '''Add products to a sale'''
        parser = reqparse.RequestParser()
        parser.add_argument('product', help='The product field cannot be blank',
                            required=True, type=int)
        parser.add_argument('quantity', help='The quantity field cannot be blank',
                            required=True, type=int)
        data = parser.parse_args()
        sale = Sale.get_by_id(sale_id)
        if sale is None:
            return {"error": 404, "message": "sale not found"}, 404
        if sale.status == "submitted":
            return {"message": "Forbidden.Sale is already submitted"}, 403
        sale_json = sale.json_dump()

        product = Product.get_by_id(id=data["product"])
        if product is None:
            return {"error": 404, "message": "product not found"}, 404


        stocks = product.get_available_stocks()

        if len(stocks) == 0:
            return {"error": 404, "message": "product out of stock"}, 404


        selected_stock = stocks[0]
        sale_quantity = data["quantity"]
        total_available = product.get_all_available_quantity()

        if sale_quantity > total_available:
            return {"error": 404, "message": "product out of stock"}, 404

        index = 0
        while sale_quantity > 0:
            if sale_quantity >= stocks[index].quantity:
                temp_ss = SaleStock(id=None, sale_id=sale_id, stock_id=stocks[index].id, quantity=stocks[index].quantity)
                temp_ss.save()
                sale_quantity -= stocks[index].quantity
            else:
                temp_ss = SaleStock(id=None, sale_id=sale_id, stock_id=stocks[index].id, quantity=sale_quantity)
                temp_ss.save()
                sale_quantity -= sale_quantity
            index +=1

        sale_product = SaleStock(id=None, sale_id=sale_id, stock_id=stocks[index].id, quantity=data["quantity"])
        sale_product.save()
        sale = Sale.get_by_id(sale_id)
        sale_json = sale.json_dump()
        sale_json["products"] = SoldStock.get_sale_products(sale_id=sale.id)
        return {"message": "success", "data": sale_json}, 201


product_fields = api_v1.model('Product', {
    'name': fields.String,
    'amount': fields.Integer,
    'quantity': fields.Integer

})


@ns2.route('/products')
class ProductsResource(Resource):
    '''Products resource'''

    @api_v1.expect(product_fields)
    @ns2.doc(security='apiKey')
    @jwt_required
    def post(self):
        """ Add a product.Admin only """

        parser = reqparse.RequestParser()
        parser.add_argument('name', help='The product field cannot be blank',
                            required=True, type=str)
        parser.add_argument('buying_price', help='The buying price field cannot be blank',
                            required=True, type=int)
        data = parser.parse_args()

        logged_in_user = get_jwt_identity()
        if not User.isAdmin(logged_in_user):
            return {"error": 401, "message": "You are not authorized.admin only"}, 401
        if Product.get_by_name(name=data['name']):
            return {"error": 409, "message": "product already exists"}, 409
        new_product = Product(id=None, name=data['name'], buying_price=data['buying_price'],
                              created_by=str(get_jwt_identity()), date_created=str(datetime.now()),
                              date_modified=str(datetime.now()))
        new_product.save()
        posted_product = dict(name=data['name'], buying_price=data['buying_price'],
                              created_by=User.get_by_id(get_jwt_identity()), date_created=str(datetime.now()),
                              date_modified=str(datetime.now()))
        print("this is creator", User.get_by_id(get_jwt_identity()))
        return {"message": "product added", "data": posted_product}

    @ns2.doc('list_products')
    @ns2.doc(security='apiKey')
    @jwt_required
    def get(self):
        '''Get all products'''
        if "search" in request.args:
            products_found = Product.search_products(self, name=request.args['search'])
            if products_found:
                return {"message": "Search results", "data": products_found}, 200
            return {"message": "No product found with that name"}, 404
        all_products = Product.get_all()

        return {"message": "Ok", "data": all_products}, 200


@ns2.route('/products/<int:product_id>')
class ProductResource(Resource):
    '''Product resource'''

    @ns2.doc('list_products')
    @ns2.doc(security='apiKey')
    @jwt_required
    def get(self,product_id):
        '''Get a product with its stock'''
        found_product = Product.get_by_id(id=product_id)

        product_json = found_product.json_dump()
        product_json['stock'] = Stock.get_by_product(product_id=product_id)
        return {"message":"ok","data":product_json},200


@ns2.route('/stocks')
class ProductResource(Resource):
    '''AvailableProduct resource'''

    @ns2.doc('list_available_products')
    @ns2.doc(security='apiKey')
    @jwt_required
    def get(self):
        '''Get all stocks'''
        all_products = Stock.get_all_available()
        return {"message": "Ok", "data": all_products}, 200

    @ns3.doc(security='apiKey')
    @jwt_required
    def post(self):
        '''Add available product.Admin only'''

        parser = reqparse.RequestParser()
        parser.add_argument('product_id', help='The product_id field cannot be blank',
                            required=True, type=int)
        parser.add_argument('quantity', help='The quantity field cannot be blank',
                            required=True, type=int)
        data = parser.parse_args()
        new_stock = Stock(id=None,product_id=data['product_id'],quantity=data['quantity'],available=True)
        new_stock.save()
        return {"message": "stock added"},201


@ns2.route('/products?search=<string:string>')
class SaleResource(Resource):
    '''Product resource'''

    @ns.doc(security='apiKey')
    @jwt_required
    def get(self):
        '''Search for a product'''
        pass


n_user = api_v1.model('Login', {
    'username': fields.String,
    'password': fields.String
})


@ns1.route('/login')
class LoginResource(Resource):
    '''Class for login resource'''

    @api_v1.expect(n_user)
    def post(self):
        ''' Login with registered details'''
        parser = reqparse.RequestParser()
        parser.add_argument('password', help='This3 field cannot be blank',
                            required=True)
        parser.add_argument('username', help='This field cannot be blank',
                            required=True)
        data = parser.parse_args()
        current_user = User.get_by_username(data['username'])
        if not current_user:
            return {'message': 'User {} doesnt exist'.format(
                data['username'])}, 404

        if User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(current_user.id)
            user = User.get_by_username(data['username'])
            user_json = user.json_dumps()
            return dict(message='Logged in as {}'.format(current_user.username), user=user_json,
                        permissions=UserPermission.get_user_permissions(current_user.id),
                        access_token=access_token), 200
        return {'message': 'Wrong credentials'}, 403


new_user = api_v1.model('Register', {
    'username': fields.String,
    'email': fields.String,
    'password': fields.String
})


@ns1.route('/signup')
class RegisterResource(Resource):
    '''Users registration resource'''

    @api_v1.expect(new_user)
    @ns.doc(security='apiKey')
    @jwt_required
    def post(self):
        '''Register a user.Admin only'''
        parser = reqparse.RequestParser()
        parser.add_argument('username',
                            help='The username field cannot be blank',
                            required=True, type=str)
        parser.add_argument('email', help='The email field cannot be blank',
                            required=True, type=str)
        parser.add_argument('password',
                            help='The password field cannot be blank',
                            required=True, type=str)
        data = parser.parse_args()
        if Validate.validate_username_format(data['username']):
            return {'message': 'Invalid username username should be of form "username"'}, 400
        if not Validate.validate_length_username(data['username']):
            return {'message': 'The length of username should be atleast 4 characters'}, 400
        if not Validate.validate_password_length(data['password']):
            return {'message': 'the length of the password should be atleast 6 characters'}, 400
        if re.match(r"^[1-9]\d*(\.\d+)?$", data['password']):
            return {'message': 'the username and password should be of type string'}, 400
        if not Validate.validate_email_format(data['email']):
            return {'message': 'Invalid email.The email should be of type "example@mail.com"'}, 400
        if User.get_by_username(data['username']):
            return {'message': 'This username is already taken,kindly try another username'}, 409
        if User.get_by_email(data['email']):
            return {'message': 'This email is already taken'}, 409

        logged_in_user = get_jwt_identity()
        if User.isAdmin(logged_in_user):
            User.save(self, username=data['username'],
                      email=data['email'],
                      password=User.generate_hash(data['password']))

            user = User.get_by_username(data['username'])
            user_json = user.json_dumps()
            access_token = create_access_token(user_json['id'])
            UserPermission.makeUser(self, user_id=user_json['id'])
            user = User.get_by_username(data['username'])
            user_json = user.json_dumps()
            return {"message": "The user signed up successfully", "user": user_json,
                    "permissions": UserPermission.get_user_permissions(user_json['id']),
                    "access_token": access_token}, 201
        return {"error": 401, "message": "Not authorized,only accessible by admin"}, 401


role_fields = api_v1.model('Role', {
    'name': fields.String,
})


@ns1.route('/users/<int:user_id>')
class UserResource(Resource):
    '''Give admin permission'''

    @api_v1.expect(role_fields)
    @ns.doc(security='apiKey')
    @jwt_required
    def put(self, user_id):
        '''Give admin and moderator rights,accessed by admin only'''
        parser = reqparse.RequestParser()
        parser.add_argument('name',
                            help='The name field cannot be blank',
                            required=True, type=str)
        data = parser.parse_args()
        user_to_make_admin = User.get_by_id(id=user_id)
        if not User.isAdmin(user_id=get_jwt_identity()):
            return {"error": 401, "message": "Not authorised,admin only"}, 401
        if user_to_make_admin is None:
            return {"error": 404, "message": "No user with that id"}, 404
        if data['name'] == "admin":
            if User.isAdmin(user_id=user_id):
                return {"message": "User is already an admin"}
            UserPermission.makeAdmin(self, user_id=user_id, permission_id=1)
            user = User.get_by_id(id=user_id)
            return {"user": user, "message": "Made admin"}, 201
        elif data['name'] == "moderator":
            user = User.get_by_id(id=user_id)
            if User.isModerator(user_id=user_id):
                return {"message": "user is already a moderator"}, 400
            UserPermission.makeModerator(self, user_id=user_id, permission_id=2)
            user = User.get_by_id(id=user_id)
            return {"user": user, "message": "User given moderator rights"}, 201
        return {"error code": 400, "message": "Role not allowed"}, 400
