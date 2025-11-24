from datetime import datetime
from models.db import get_db_connection

class OrderModel:
    def __init__(self):
        pass

    def create_order(self, user_name, phone, address, items, total_amount):
        """Create a new order"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 1. Insert into orders table
                sql_order = """
                    INSERT INTO orders (user_name, phone, address, total_amount, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(sql_order, (
                    user_name,
                    phone,
                    address,
                    total_amount,
                    'pending',
                    created_at
                ))
                order_id = cursor.lastrowid

                # 2. Insert into order_items table
                sql_item = """
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """
                for item in items:
                    cursor.execute(sql_item, (
                        order_id,
                        item['id'],
                        item['quantity'],
                        item['price']
                    ))
            
            connection.commit()
            
            # Construct the order object to return
            order = {
                'id': order_id,
                'user_name': user_name,
                'phone': phone,
                'address': address,
                'items': items,
                'total_amount': total_amount,
                'status': 'pending',
                'created_at': created_at
            }
            return order
            
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()

    def get_all_orders(self):
        """mengambil seluruh data pesanan"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM orders ORDER BY created_at DESC"
                cursor.execute(sql)
                orders = cursor.fetchall()
                return orders
        finally:
            connection.close()

    def get_order_by_id(self, order_id):
        """mengambil data berdasasrkan id"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Get order details
                sql_order = "SELECT * FROM orders WHERE id = %s"
                cursor.execute(sql_order, (order_id,))
                order = cursor.fetchone()
                
                if order:
                    # Get order items
                    sql_items = """
                        SELECT oi.*, p.nama as product_name 
                        FROM order_items oi
                        JOIN products p ON oi.product_id = p.id
                        WHERE oi.order_id = %s
                    """
                    cursor.execute(sql_items, (order_id,))
                    items = cursor.fetchall()
                    order['items'] = items
                
                return order
        finally:
            connection.close()

    def update_order_status(self, order_id, new_status):
        """update status ordernya"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE orders SET status = %s WHERE id = %s"
                cursor.execute(sql, (new_status, order_id))
                
                if cursor.rowcount > 0:
                    # Return updated order (simplified)
                    return {'id': order_id, 'status': new_status}
                return None
            connection.commit()
        finally:
            connection.close()

    def get_orders_by_status(self, status):
        """mengambil data berdasarkan status"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM orders WHERE status = %s ORDER BY created_at DESC"
                cursor.execute(sql, (status,))
                orders = cursor.fetchall()
                return orders
        finally:
            connection.close()