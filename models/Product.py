from models.db import get_db_connection

class ProductModel:
    def __init__(self):
        pass

    def setProduct(self, new_data):
        """Add a new product to the inventory"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO products (nama, origin, roast, harga, stok) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (
                    new_data['nama'],
                    new_data['origin'],
                    new_data['roast'],
                    int(new_data['harga']),
                    int(new_data['stok'])
                ))
            connection.commit()
            return True
        finally:
            connection.close()
    
    def getAllProduct(self):
        """Return all products in the inventory"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM products"
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        finally:
            connection.close()
    
    def getProductById(self, product_id):
        """Return a specific product by its ID"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM products WHERE id = %s"
                cursor.execute(sql, (product_id,))
                result = cursor.fetchone()
                return result
        finally:
            connection.close()
    
    def updateProduct(self, product_id, updated_data):
        """Update an existing product by its ID"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    UPDATE products 
                    SET nama=%s, origin=%s, roast=%s, harga=%s, stok=%s 
                    WHERE id=%s
                """
                cursor.execute(sql, (
                    updated_data['nama'],
                    updated_data['origin'],
                    updated_data['roast'],
                    int(updated_data['harga']),
                    int(updated_data['stok']),
                    product_id
                ))
            connection.commit()
            return True
        finally:
            connection.close()

    def deleteProduct(self, product_id):
        """Delete a product by its ID"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM products WHERE id = %s"
                cursor.execute(sql, (product_id,))
            connection.commit()
            return True
        finally:
            connection.close()