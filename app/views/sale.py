from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restplus import reqparse, Resource

from app.models import Product, SaleStock, Sale, SoldStock, User
from app.views import ns


@ns.route('/salses/<int:sale_id>')
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

        # sale = Sale.get_by_id(sale_id)
        #
        # if sale is None:
        #     return {"error": 404, "message": "sale not found"}
        # logged_user = User.get_by_id(id=get_jwt_identity())['username']
        # if logged_user == sale.created_by or User.isAdmin(user_id=get_jwt_identity()):
        #     sale = Sale.get_by_id(sale_id)
        #     sale_json = sale.json_dump()
        #     sale_json["products"] = SaleProduct.get_sale_products(sale_id=sale.id)
        #     if not sale_json["products"]:
        #         return {"Error": 400, "message": "You can't close a sale with no products"}, 400
        #     if sale.status == "submitted":
        #         return {"Error": 400, "message": "The sale is already closed"}, 400
        #     sale.submit()
        #     sale = Sale.get_by_id(sale_id)
        #     sale_json = sale.json_dump()
        #     sale_json["products"] = SaleProduct.get_sale_products(sale_id=sale.id)
        #     return {"message": "successfuly closed the sale", "data": sale_json}, 200
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
        # sale_json["products"] = SaleStock.get_sale_stocks(sale_id=sale.id)
        # stock = Stock.get_by_id(stock_id=data['stock'])
        # if stock is None:
        #     return {"error": 404, "message": "stock not available"}, 404

        # sale_products = SaleStock.get_sale_stocks(sale_id=sale_id)
        # for item in sale_products:
        #     if item['id'] == data['stock']:
        #         return {"error": 409, "message": "product already exists"}, 409
        sale_product = SaleStock(id=None, sale_id=sale_id, stock_id=stocks[0].id, quantity=data["quantity"])
        sale_product.save()
        sale = Sale.get_by_id(sale_id)
        sale_json = sale.json_dump()
        sale_json["products"] = SoldStock.get_sale_products(sale_id=sale.id)
        return {"message": "success", "data": sale_json}, 201
