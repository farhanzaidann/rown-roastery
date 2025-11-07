from datetime import datetime

class OrderModel:
    def __init__(self):
        # Static data for orders
        self.orders = []
        self.next_id = 1

    def create_order(self, user_name, phone, address, items, total_amount):
        """Create a new order"""
        order = {
            'id': self.next_id,
            'user_name': user_name,
            'phone': phone,
            'address': address,
            'items': items,  # List of item dictionaries
            'total_amount': total_amount,
            'status': 'pending',  # pending, confirmed, shipped, delivered, cancelled
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.orders.append(order)
        self.next_id += 1
        return order

    def get_all_orders(self):
        """Return all orders"""
        return self.orders

    def get_order_by_id(self, order_id):
        """Return a specific order by its ID"""
        for order in self.orders:
            if order['id'] == order_id:
                return order
        return None

    def update_order_status(self, order_id, new_status):
        """Update the status of an order"""
        for i, order in enumerate(self.orders):
            if order['id'] == order_id:
                self.orders[i]['status'] = new_status
                return self.orders[i]
        return None

    def get_orders_by_status(self, status):
        """Return all orders with a specific status"""
        return [order for order in self.orders if order['status'] == status]