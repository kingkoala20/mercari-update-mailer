import sqlite3


class Entry:

    def __init__(self, alt, link, price):
        self._alt = alt
        self._link = link
        self._price = int(price)

class Item:
    
    def __init__(self, brand: str, item_code: str, neg=None):
        self._brand = brand
        self._item_code = item_code.lower()
        self._average_price_sold = 0
        self._last_updated = ''
        self.target_price = 0
        self._head_code = ''
        self._neg = None if neg == None else " ".join(neg)
        
        self._init_db()

    def __str__(self):
        return f'{self._brand +" "+ self._item_code}'

    def _init_db(self):
        conn = sqlite3.connect('market.db')
        cur = conn.cursor()
        data = (
            self._brand,
            self._item_code,
            self._neg
        )
        
        entry_clause = """
            INSERT INTO items(brand, item_code, neg) VALUES (?,?,?)
        """
        try:
            cur.execute(entry_clause, data)
        except sqlite3.IntegrityError:
            for entry in cur.execute(f"""
                SELECT *
                FROM items
                WHERE item_code = "{self._item_code}"
                """):
                self._brand = entry[1]
                self._average_price_sold = entry[3]
                self.target_price = entry[4]
                self._last_updated = entry[5]
                self._head_code = entry[6]
                self._neg = entry[7].split() if entry[7] != None else None
                
                
        conn.commit()

    def _update_db(self, **kwargs):
        conn = sqlite3.connect('market.db')
        cur = conn.cursor()
        data = ", ".join(f"{k}={v}" for k,v in kwargs.items())
        cur.execute(f"""
            UPDATE items SET
            {data}
        """)
        conn.commit()

    def set_target_price(self, new_target):
        self.target_price = new_target
        self._update_db(target_price = new_target)
    
if __name__ == "__main__":
    testitem = Item("Pioneer", "ddj-400")
    testitem.set_target_price(12)


        