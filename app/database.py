import os  # import os

import psycopg2



class Database:

    @classmethod
    def connect_to_db(cls):
        '''Function to create a database connection'''
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        conn.autocommit = True
        cursor = conn.cursor()

        return cursor

    @classmethod
    def create_database_tables(cls):
        cursor = Database.connect_to_db()
        # create products table
        sql_command = """CREATE TABLE IF NOT EXISTS "public"."products"  (
        id SERIAL ,
        name VARCHAR(255) NOT NULL,
        created_by VARCHAR(255) NOT NULL,
        buying_price VARCHAR(255) NOT NULL,
        date_created VARCHAR(80),
        date_modified VARCHAR(80),
        PRIMARY KEY (id)
            )
            """
        cursor.execute(sql_command)
        # create sales table
        sql_command = """CREATE TABLE IF NOT EXISTS "public"."sales"  (
        id SERIAL ,
        buyer_name VARCHAR(255) NOT NULL,
        status VARCHAR(255) NOT NULL,
        created_by VARCHAR(255) NOT NULL,
        date_created VARCHAR(80),
        date_modified VARCHAR(80),
        PRIMARY KEY (id)
            )
            """
        cursor.execute(sql_command)

        # create saleproducts table
        sql_command = """CREATE TABLE IF NOT EXISTS "public"."saleproducts"  (
        id SERIAL ,
        sale_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
            )
            """
        cursor.execute(sql_command)

        # create users table
        sql_command = """CREATE TABLE IF NOT EXISTS "public"."users"  (
        id SERIAL ,
        username VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        date_created VARCHAR(80),
        date_modified VARCHAR(80),
        PRIMARY KEY (id)
            )
            """
        cursor.execute(sql_command)

        # create permissions table
        sql_command = """CREATE TABLE IF NOT EXISTS "public"."permissions"  (
          id SERIAL ,
          name VARCHAR(255) NOT NULL,
          PRIMARY KEY (id)
              )
              """
        cursor.execute(sql_command)

        # create userpermissions table
        sql_command = """CREATE TABLE IF NOT EXISTS "public"."userpermissions" (
        id SERIAL ,
        user_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE
            )
            """
        cursor.execute(sql_command)

        # create availableproducts table
        sql_command = """CREATE TABLE IF NOT EXISTS "public"."availableproducts" (
           id SERIAL ,
           product_id INTEGER NOT NULL,
           available BOOLEAN DEFAULT True NOT NULL,
           quantity INTEGER NOT NULL,
           PRIMARY KEY (id),
           FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
               )
               """
        cursor.execute(sql_command)

    @classmethod
    def drop_database_tables(cls):
        cursor = Database.connect_to_db()
        # drop products table
        sql_command = """ DROP TABLE products CASCADE;
            """
        cursor.execute(sql_command)
        # drop saleproducts table
        sql_command = """ DROP TABLE saleproducts CASCADE;
                   """
        cursor.execute(sql_command)
        # drop availableproducts table
        sql_command = """ DROP TABLE availableproducts CASCADE;
                        """
        cursor.execute(sql_command)
        # drop sales table
        sql_command = """ DROP TABLE sales CASCADE;
                              """
        cursor.execute(sql_command)



