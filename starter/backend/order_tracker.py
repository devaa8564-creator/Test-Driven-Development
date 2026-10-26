# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    VALID_STATUSES = {"pending", "processing", "shipped", "delivered", "cancelled"}

    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def _validate_status(self, status: str) -> str:
        if status is None or not str(status).strip():
            raise ValueError("Status cannot be empty.")

        normalized_status = str(status).strip().lower()
        if normalized_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: '{status}'.")
        return normalized_status

    def add_order(self, order_id: str, item_name: str, quantity: int = 1, customer_id: str = "", status: str = "pending"):
        """
        Add a new order to the system.

        Supports both the API-style call ordering and the simplified unit-test call style.
        """
        if order_id is None or not str(order_id).strip():
            raise ValueError("Order ID cannot be empty.")
        if item_name is None or not str(item_name).strip():
            raise ValueError("Item name cannot be empty.")

        if customer_id == "" and isinstance(quantity, str):
            customer_id = quantity
            quantity = 1

        if customer_id is None or not str(customer_id).strip():
            raise ValueError("Customer ID cannot be empty.")

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be a valid integer.")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        normalized_status = self._validate_status(status)
        order = {
            "order_id": str(order_id).strip(),
            "item_name": str(item_name).strip(),
            "quantity": quantity,
            "customer_id": str(customer_id).strip(),
            "status": normalized_status,
        }

        if self.storage.get_order(order["order_id"]) is not None:
            raise ValueError(f"Order with ID '{order['order_id']}' already exists.")

        self.storage.save_order(order["order_id"], order)
        return order

    def get_order_by_id(self, order_id: str):
        if order_id is None or not str(order_id).strip():
            raise ValueError("Order ID cannot be empty.")

        order = self.storage.get_order(str(order_id).strip())
        return order.copy() if order else None

    def update_order_status(self, order_id: str, new_status: str):
        if order_id is None or not str(order_id).strip():
            raise ValueError("Order ID cannot be empty.")

        normalized_status = self._validate_status(new_status)

        order = self.storage.get_order(str(order_id).strip())
        if order is None:
            raise ValueError(f"Order with ID '{order_id}' does not exist.")

        order["status"] = normalized_status
        self.storage.save_order(order["order_id"], order)
        return order

    def list_all_orders(self):
        orders = self.storage.get_all_orders() or {}
        return [order.copy() for order in orders.values()]

    def list_orders_by_status(self, status: str):
        if status is None or not str(status).strip():
            raise ValueError("Status cannot be empty.")

        normalized_status = self._validate_status(status)
        orders = self.storage.get_all_orders() or {}
        return [order.copy() for order in orders.values() if order.get("status") == normalized_status]
    
   