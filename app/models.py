from datetime import datetime

from passlib.handlers.pbkdf2 import pbkdf2_sha256

from app.database import Database

cursor = Database.connect_to_db()
Database.create_database_tables()


class Product:
    def __init__(self, id, name, buying_price, created_by, date_created, date_modified):
        self.id = id
        self.name = name
        self.buying_price = buying_price
        self.created_by = created_by
        self.date_created = date_created
        self.date_modified = date_modified

    @classmethod
    def get_all(cls):
        '''Factory method'''
        cursor.execute(
            f"SELECT * FROM public.products;")
        rows = cursor.fetchall()

        product_objects = []
        for item in rows:
            product = Product(id=item[0], name=item[1], created_by=item[2], buying_price=item[3],
                              date_created=item[4], date_modified=item[5])
            product_json = product.json_dump()
            product_objects.append(product_json)

        return product_objects

    @classmethod
    def get_by_id(cls, id):
        cursor.execute(
            f"SELECT * FROM public.products where id = {id};")
        item = cursor.fetchone()
        if item is None:
            return None

        product = Product(id=item[0], name=item[1], created_by=item[2], buying_price=item[3],
                          date_created=item[4], date_modified=item[5])

        return product

    @classmethod
    def get_by_name(cls, name):
        '''method to find a user by username'''
        try:
            cursor.execute("select * from products where name = %s", (name,))
            product = cursor.fetchone()
            return list(product)
        except Exception:
            return False

    def search_products(self, name):
        cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{name}%'")
        rows = cursor.fetchall()
        product_objects = []
        for item in rows:
            product = Product(id=item[0], name=item[1], created_by=item[2], buying_price=item[3],
                              date_created=item[4], date_modified=item[5])
            product_json = product.json_dump()
            product_objects.append(product_json)
        return product_objects

    def save(self):
        cursor.execute(
            f"INSERT INTO public.products(name,buying_price,created_by,date_created,date_modified) VALUES('{self.name}', '{self.buying_price}','{self.created_by}','{self.date_created}','{self.date_modified}');")

    def json_dump(self):
        return {
            "id": self.id,
            "name": self.name,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
            "created_by": User.get_by_id(self.created_by),
        }

    def get_available_stocks(self):
        return Stock.get_all_available_stock_products(self.id)

    def get_all_available_quantity(self):
        count = 0
        for item in Stock.get_all_available_stock_products(self.id):
            count += item.available_quantity()
        return count


class Stock:
    def __init__(self, id, product_id, available, quantity):
        self.id = id
        self.product_id = product_id
        self.available = available
        self.quantity = quantity

    def save(self):
        cursor.execute(
            f"INSERT INTO public.stock(product_id, available, quantity) VALUES({self.product_id}, {self.available}, {self.quantity});")

    def available_quantity(self):
        total_quantity = self.quantity
        sale_stocks = SaleStock.get_by_stock(self.id)

        for sale_stock in sale_stocks:
            total_quantity -= sale_stock.quantity

        return total_quantity

    @classmethod
    def get_all_available(cls):
        '''Factory method'''
        cursor.execute(
            f"SELECT * FROM public.stock WHERE available=True;")
        rows = cursor.fetchall()

        product_objects = []
        for item in rows:
            product_retieved = Stock(id=item[0], product_id=item[1], quantity=item[2], available=item[3])
            product_json = product_retieved.json_dump()
            product_json['products'] = Product.get_by_id(item[1]).json_dump()
            product_objects.append(product_json)
        return product_objects

    @classmethod
    def get_all_available_stock_products(cls, product_id):
        '''Factory method'''
        cursor.execute(
            f"SELECT * FROM public.stock WHERE available=True AND product_id={product_id};")
        rows = cursor.fetchall()

        product_objects = []
        for item in rows:
            stock = Stock(id=item[0], product_id=item[1], available=item[2], quantity=item[3])
            if stock.available_quantity() > 0:
                product_objects.append(stock)
        return product_objects

    @classmethod
    def get_by_id(cls, stock_id):
        cursor.execute(
            f"SELECT * FROM public.stock WHERE id = {stock_id};")
        item = cursor.fetchone()
        if item is None:
            return None
        stock = Stock(id=item[0], product_id=item[1], available=item[2], quantity=item[3])
        return stock.json_dump()

    @classmethod
    def get_by_product(cls, product_id):
        cursor.execute(
            f"SELECT * FROM public.stock WHERE product_id = {product_id};")
        items = cursor.fetchall()
        if items is None:
            return None
        stocks_json = []
        for item in items:
            stock = Stock(id=item[0], product_id=item[1], available=item[2], quantity=item[3])
            stocks_json.append(stock.json_dump())
        return stocks_json

    def makeOutofStock(self):
        cursor.execute(
            f"UPDATE public.stock SET available =False WHERE id = {self.id};")

    def json_dump(self):
        return {
            "id": self.id,
            "quantity": self.quantity,
            "available": self.available,
            "availableQuantity": self.available_quantity()
        }


class SaleStock:
    def __init__(self, id, sale_id, stock_id, quantity):
        self.id = id
        self.sale_id = sale_id
        self.stock_id = stock_id
        self.quantity = quantity

    def save(self):
        cursor.execute(
            f"INSERT INTO public.salestock(sale_id, stock_id, quantity) VALUES({self.sale_id}, {self.stock_id}, {self.quantity});")

    def json_dump(self):
        return {
            "id": self.id,
            "sale_id": self.sale_id,
            "stock_id": self.stock_id,
            "quantity": self.quantity
        }

    @classmethod
    def get_sale_stocks(cls, sale_id):
        '''Factory method'''
        cursor.execute(
            f"SELECT * FROM public.salestock where sale_id = {sale_id};")
        rows = cursor.fetchall()

        sale_objects = []
        for item in rows:
            sale = SaleStock(id=item[0], stock_id=item[1], sale_id=item[2], quantity=item[3])
            sale_objects.append(sale.json_dump())
        return sale_objects

    @classmethod
    def get_by_stock(cls, stock_id):
        '''Factory method'''
        cursor.execute(
            f"SELECT * FROM public.salestock WHERE  stock_id = {stock_id};")
        rows = cursor.fetchall()

        sale_objects = []
        for item in rows:
            sale = SaleStock(id=item[0], sale_id=item[1], stock_id=item[2], quantity=item[3])

            sale_objects.append(sale)

        return sale_objects


class SoldStock:
    def __init__(self, id, name, quantity, sale_id, product_id, stock_id):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.sale_id = sale_id
        self.product_id = product_id
        self.stock_id = stock_id

    @classmethod
    def get_sale_products(cls, sale_id):
        '''Factory method'''
        cursor.execute(f"""
                SELECT ss.id, ss.quantity, ss.sale_id, p."name", p.id as product_id, s.id as stock_id FROM salestock ss,
                stock s, products p where ss.stock_id = s.id and s.product_id = p.id and ss.sale_id = {sale_id};
                """)
        rows = cursor.fetchall()

        sale_objects = []
        for item in rows:
            sale = SoldStock(id=item[0], quantity=item[1], sale_id=item[2], name=item[3], product_id=item[4],
                             stock_id=item[5])

            sale_objects.append(sale.json_dump())

        return sale_objects

    def json_dump(self):
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "sale_id": self.sale_id,
            "product_id": self.product_id,
            "stock_id": self.stock_id,

        }


class Sale:
    def __init__(self, id, buyer_name, status, created_by, date_created, date_modified):
        self.id = id
        self.buyer_name = buyer_name
        self.status = status
        self.created_by = created_by
        self.date_created = date_created
        self.date_modified = date_modified

    def submit(self):
        cursor.execute(
            f"UPDATE public.sales SET status = 'submitted' WHERE id = {self.id};")

    def cancel(self):
        cursor.execute(
            f"UPDATE public.sales SET status = 'deleted' WHERE id = {self.id};")

    def save(self):
        cursor.execute(
            f"INSERT INTO public.sales(buyer_name, status, created_by,date_created,date_modified) VALUES('{self.buyer_name}', '{self.status}', '{self.created_by}','{self.date_created}','{self.date_modified}');")

    @classmethod
    def get_all(cls):
        '''Factory method'''
        cursor.execute(
            f"SELECT * FROM public.sales;")
        rows = cursor.fetchall()

        sale_objects = []
        for item in rows:
            sale = Sale(id=item[0], buyer_name=item[1], status=item[2], created_by=item[3], date_created=item[4],
                        date_modified=item[5])
            sale_json = sale.json_dump()
            sale_json["products"] = SaleStock.get_sale_stocks(sale_id=sale.id)

            sale_objects.append(sale_json)

        return sale_objects

    @classmethod
    def get_all_closed_sales(cls):
        '''Factory method'''
        cursor.execute(
            f"SELECT * FROM public.sales WHERE status='submitted';")
        rows = cursor.fetchall()

        sale_objects = []
        for item in rows:
            sale = Sale(id=item[0], buyer_name=item[1], status=item[2], created_by=item[3], date_created=item[4],
                        date_modified=item[5])
            sale_json = sale.json_dump()
            sale_json["products"] = SaleStock.get_sale_stocks(sale_id=sale.id)

            sale_objects.append(sale_json)

        return sale_objects

    @classmethod
    def get_all_user_closed_sales(cls, username):
        '''Factory method'''
        cursor.execute(
            f"SELECT * FROM public.sales where status='submitted' AND created_by='{username}';")
        rows = cursor.fetchall()

        sale_objects = []
        for item in rows:
            sale = Sale(id=item[0], buyer_name=item[1], status=item[2], created_by=item[3], date_created=item[4],
                        date_modified=item[5])
            sale_json = sale.json_dump()
            sale_json["products"] = SaleStock.get_sale_stocks(sale_id=sale.id)

            sale_objects.append(sale_json)

        return sale_objects

    def search_closed_sales(self, username):
        cursor.execute(f"SELECT * FROM sales WHERE status='deleted' AND created_by LIKE '%{username}%'")
        rows = cursor.fetchall()
        sale_objects = []
        for item in rows:
            sale = Sale(id=item[0], buyer_name=item[1], status=item[2], created_by=item[3], date_created=item[4],
                        date_modified=item[5])
            sale_json = sale.json_dump()
            sale_json["products"] = SaleProduct.get_sale_products(sale_id=sale.id)

            sale_objects.append(sale_json)
        return sale_objects

    def json_dump(self):
        return {
            "id": self.id,
            "buyer_name": self.buyer_name,
            "status": self.status,
            "created_by": self.created_by,
            "date_created": self.date_created,
            "date_modified": self.date_modified
        }

    @classmethod
    def get_by_id(cls, sale_id):
        cursor.execute(
            f"SELECT * FROM public.sales where id = {sale_id};")
        item = cursor.fetchone()

        if item is None:
            return None

        sale = Sale(id=item[0], buyer_name=item[1], status=item[2], created_by=item[3], date_created=item[4],
                    date_modified=item[5])
        return sale


class User:
    def __init__(self, id, username, email, password, date_created):
        self.id = id
        self.username = username
        self.email = email
        self.date_created = date_created
        self.password = password

    def save(self, username, email, password):
        '''method to save a user'''
        format_str = f"""
                 INSERT INTO public.users (username,email,password,date_created,date_modified)
                 VALUES ('{username}','{email}','{password}','{(datetime.now())}','{(datetime.now())}');
                 """
        cursor.execute(format_str)
        return {
            "username": username,
            "email": email
        }

    @classmethod
    def get_by_id(cls, id):
        '''method to find a user by id'''
        try:
            cursor.execute("select * from users where id = %s", (id,))
            retrieved_user = list(cursor.fetchone())
            user = User(id=retrieved_user[0], username=retrieved_user[1], email=retrieved_user[2],
                        password=retrieved_user[3], date_created=retrieved_user[4])

            return user.json_dumps()
        except Exception:
            return False

    @classmethod
    def get_by_username(cls, username):
        '''method to find a user by username'''
        try:
            cursor.execute("select * from users where username = %s", (username,))
            user = cursor.fetchone()
            user = User(id=user[0], username=user[1], email=user[2], password=user[3], date_created=user[4])
            return user
        except Exception:
            return False

    @classmethod
    def get_by_email(cls, email):
        '''This method gets a user using email'''
        try:
            cursor.execute("select * from users where email = %s", (email,))
            user = cursor.fetchone()
            return list(user)
        except Exception:
            return False

    def json_dumps(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }

    @staticmethod
    def generate_hash(password):
        '''method that returns a hash'''
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        '''method to verify password with the hash'''
        return pbkdf2_sha256.verify(password, hash)

    @classmethod
    def isAdmin(cls, user_id):
        user_permissions = UserPermission.get_user_permissions(user_id=user_id)
        if user_permissions:
            list_permissions = []
            for index in range(len(user_permissions)):
                for key in user_permissions[index]:
                    list_permissions.append((user_permissions[index][key]))
            if "admin" in list_permissions:
                return True
            return False
        return False

    @classmethod
    def isModerator(cls, user_id):
        user_permissions = UserPermission.get_user_permissions(user_id=user_id)
        if user_permissions:
            list_permissions = []
            for index in range(len(user_permissions)):
                for key in user_permissions[index]:
                    list_permissions.append((user_permissions[index][key]))
            if "moderator" in list_permissions:
                return True
            return False
        return False


class Permission:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def json_dump(self):
        return {
            "id": self.id,
            "name": self.name
        }

    @classmethod
    def get_by_id(cls, id):
        cursor.execute(
            f"SELECT * FROM public.permissions where id = {id};")
        item = cursor.fetchone()
        if item is None:
            return None
        permission = Permission(id=item[0], name=item[1])
        return permission.json_dump()


class UserPermission:
    def __init__(self, user_id, permission_id):
        self.id = id
        self.user_id = user_id
        self.permission_id = permission_id

    def json_dump(self):
        return {
            "id": self.id,
            "user": User.get_by_id(self.user_id),
            "permissions": Permission.get_by_id(id=self.permission_id)
        }

    @classmethod
    def get_user_permissions(cls, user_id):
        '''Factory method'''
        cursor.execute(
            f"SELECT * FROM public.userpermissions where user_id = {user_id};")
        rows = cursor.fetchall()
        permission_objects = []
        for item in rows:
            permission_item = Permission.get_by_id(item[2])
            permission_objects.append(permission_item)
        return permission_objects

    def makeAdmin(self, user_id, permission_id):
        cursor.execute(
            f"INSERT INTO public.userpermissions(user_id, permission_id) VALUES('{user_id}', '{permission_id}');")

    def makeModerator(self, user_id, permission_id):
        cursor.execute(
            f"INSERT INTO public.userpermissions(user_id, permission_id) VALUES('{user_id}', '{permission_id}');")

    def makeUser(self, user_id):
        cursor.execute(
            f"INSERT INTO public.userpermissions(user_id, permission_id) VALUES('{user_id}', '3');")
