import sqlite3
class Database:
    def __init__(self):
        self.connection = sqlite3.connect('delivery.db')
        self.connection.row_factory = sqlite3.Row
        self.cur = self.connection.cursor()
        self.cur.execute('''
                    create table if not exists "users" (
                    "id" integer not null primary key AUTOINCREMENT,
                    "chat_id" integer not null,
                    "tg_firstname" text not null,
                    "tg_username" text ,
                    "lang" integer,
                    "phone_number" text,
                    "fullname" text,
                    "joined_date" text not null
                    )
                ''')

        self.cur.execute('''
                    create table if not exists "location" (
                    "id" integer not null primary key AUTOINCREMENT,
                    "user_id" integer not null,
                    "lat" text not null,
                    "lon" text not null,
                    "name" text not null
                    )
                ''')

        self.cur.execute('''
                    create table if not exists "category" (
                    "id" integer not null primary key AUTOINCREMENT,
                    "name" text not null,
                    "photo" text 
                    )
                ''')

        self.cur.execute('''
                    create table if not exists "product" (
                    "id" integer not null primary key AUTOINCREMENT,
                    "name" text not null,
                    "photo" text,
                    "price" integer not null,
                    "is_available" integer not null,
                    "description" text,
                    "category_id" integer not null
                    )
                ''')

        self.cur.execute('''
                    create table if not exists "bucket" (
                    "id" integer not null primary key AUTOINCREMENT,
                    "user_id" integer not null
                    )
                ''')

        self.cur.execute('''
                    create table if not exists "bucketItem" (
                    "id" integer not null primary key AUTOINCREMENT,
                    "bucket_id" integer not null,
                    "product_id" integer not null,
                    "count" integer not null
                    )
                ''')

        self.cur.execute('''
                   create table if not exists "order" (
                   "id" integer not null primary key AUTOINCREMENT,
                   "user_id" integer not null,
                   "location_id" integer not null,
                   "price" integer not null
                   )
               ''')

        self.cur.execute('''
                   create table if not exists "orderItem" (
                   "id" integer not null primary key AUTOINCREMENT,
                   "order_id" integer not null,
                   "product_id" integer not null,
                   "count" integer not null
                   )
               ''')
        self.cur.execute('''
                   create table if not exists "userlog" (
                   "id" integer not null primary key AUTOINCREMENT,
                   "chat_id" integer not null,
                   "log" text
                   )
               ''')
    def get_user(self,chat_id):
        user_data = self.cur.execute(f'''
            select * from users
            where chat_id = {chat_id}
        ''').fetchone()
        if user_data:
            return user_data
        else:
            return None
    def add_user(self,**kwargs):
        if kwargs.get("chat_id") and kwargs.get("tg_firstname"):
            self.cur.execute(f'''
                insert into users (chat_id, tg_firstname, tg_username, joined_date)
                values ({kwargs.get('chat_id')},"{kwargs.get('tg_firstname')}","{kwargs.get('tg_username')}","{kwargs.get('joined_date')}")
            ''')
            self.connection.commit()
        if kwargs.get('lang') and kwargs.get('chat_id'):
            self.cur.execute(f'''
                        update users set lang = ?
                        where  chat_id = ?
                    ''', (kwargs.get('lang'), kwargs.get('chat_id')))
            self.connection.commit()
        if kwargs.get('chat_id') and kwargs.get('fullname'):
            self.cur.execute(f'''
                        update users set fullname = ?
                        where  chat_id = ?
                    ''', (kwargs.get('fullname'), kwargs.get('chat_id')))
            self.connection.commit()
        if kwargs.get('chat_id') and kwargs.get('phone_number'):
            self.cur.execute(f'''
                        update users set phone_number = ?
                        where  chat_id = ?
                    ''', (kwargs.get('phone_number'), kwargs.get('chat_id')))
            self.connection.commit()
    def add_log(self,**kwargs):
        log = self.cur.execute(f'''
            select * from userlog
            where chat_id = {kwargs['chat_id']}
        ''').fetchone()
        if log:
            self.cur.execute(f'''
                update userlog set log = {kwargs["log"]}
                where chat_id = {kwargs['chat_id']}
            ''')
            self.connection.commit()
        else:
            self.cur.execute(f'''
                insert into userlog (chat_id, log)
                values ({kwargs['chat_id']}, {kwargs['log']})
            ''')
            self.connection.commit()
    def get_log(self,chat_id):
        log = self.cur.execute(f'''
            select * from userlog 
            where chat_id = {chat_id}
        ''').fetchone()
        return log
    def get_category(self):
        categories = self.cur.execute('''
            select * from category
        ''').fetchall()
        return categories
    def get_products(self,category_id):
        products = self.cur.execute(f'''
            SELECT product.id as id,product.name as product_name, category.name as category_name, category.photo as category_photo
            from product
            inner join category on product.category_id = category.id
            where product.is_available = 1 and product.category_id = {category_id}
        ''').fetchall()

        return products
    def get_product(self,product_id):
        product = self.cur.execute(f'''
            select * from product
            where id = {product_id}
        ''').fetchone()
        return product
    def add_bucket(self, chat_id):
        user_bucket = self.cur.execute(f'''
            select * from bucket
            where user_id = {chat_id}
        ''').fetchone()
        if not user_bucket:
            self.cur.execute(f'''
                insert into bucket (user_id)
                values ({chat_id})
            ''')
            self.connection.commit()
    def get_bucket(self,chat_id):
        user_bucket = self.cur.execute(f'''
            select * from bucket
            where user_id = {chat_id}
        ''').fetchone()
        return user_bucket
    def add_bucket_item(self,bucket_id,product_id,count):
        self.cur.execute(f'''
            insert into bucketItem (bucket_id, product_id, count)
            values ({bucket_id},{product_id},{count})
        ''')
        self.connection.commit()
    def get_bucket_item(self,bucket_id):
        items = self.cur.execute(f'''
            select bucketItem.*, bucket.user_id, product.name as product_name, product.price
            from bucketItem 
            inner join bucket on bucketItem.bucket_id = bucket.id
            inner join product on bucketItem.product_id = product.id
            where bucketItem.bucket_id = {bucket_id}
        ''').fetchall()
        return items
    def clear_bucket(self,bucket_id):
        self.cur.execute(f'''
            delete from bucketItem
            where bucket_id = {bucket_id}
        ''')
        self.connection.commit()
    def add_order(self,id, price, date):
        self.cur.execute(f"""
            insert into user_order (user_id, price, order_date)
            values ({id}, {price}, "{date}")
        """)
        self.connection.commit()
        order_id = self.cur.execute(f"""
            select id from user_order
            where user_id = {id} and order_date = "{date}"
        """).fetchone()
        return order_id
    def add_order_item(self,order_id,product_id,count):
        self.cur.execute(f"""
            insert into orderItem (order_id,product_id,count)
            values({order_id},{product_id},{count})
        """)
        self.connection.commit()
    def update_item(self,item_id,count):
        self.cur.execute(f"""
            update bucketItem set count = {count}
            where id = {item_id}
        """)
        self.connection.commit()
    def clear_item(self,item_id):
        self.cur.execute(f"""
            delete from bucketItem
            where id = {item_id}
        """)
        self.connection.commit()
    def get_orders(self,user_id):
        orders = self.cur.execute(f"""
            select * 
            from user_order
            where user_order.user_id = {user_id}.
        """).fetchall()
        return orders
    def get_order_item(self,order_id):
        order_items = self.cur.execute(f"""
            select orderItem.* , product.name as product_name, product.price as price
            from orderItem 
            inner join product on orderItem.product_id = product.id
            where order_id = {order_id}
        """).fetchall()
        return order_items

