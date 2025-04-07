from agents.base_agent import BaseAgent
import json
import os
import re


class OrderTrackingAgent(BaseAgent):
    def __init__(self, order_data_path="agents/data/orders.json"):
        self.orders = self.load_orders(order_data_path)

    def load_orders(self, path: str) -> list[dict]:
        if not os.path.exists(path):
            return []
        with open(path, "r") as file:
            return json.load(file)

    def find_orders(self, username: str) -> list[dict]:
        for user_entry in self.orders:
            if user_entry["username"].lower() == username.lower():
                return user_entry.get("orders", [])
        return []

    def build_prompt(self, message: str, context: str) -> str:
        username = self.extract_username(message)

        # If not found in message, then fallback to context
        if not username:
            username = self.extract_username(context)

        if not username:
            return "Please provide your email address so I can check your order status."

        orders = self.find_orders(username)
        if not orders:
            return f"No orders found for user '{username}'."

        order_info = "\n".join([
            f"- **{order['part_number']}** is *{order['status']}*, expected by **{order['expected_delivery']}** via **{order['carrier']}**.\n  Tracking: {order['tracking_url']}"
            for order in orders
        ])

        return (
            f"Here are your current orders, **{username}**:\n\n{order_info}\n\n"
            "Let me know if you want to track a specific one or need help changing an address."
        )


    def extract_username(self, text: str) -> str | None:
 
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        match = re.search(email_pattern, text)
        if match:
            return match.group()
        return None


