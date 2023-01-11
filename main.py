from scrape import *

DT_FORMAT = "%Y-%m-%d, %H:%M"
ROOT_URL ="jp.mercari.com/"

def add_item(brand, item_code, neg=None):
    item = Item(brand, item_code, neg=neg)
    update_average_price(item_code)
    update_head_code(item_code)
        

def db_init(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE if not exists items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            item_code TEXT NOT NULL,
            ave_price_sold INT,
            target_price INT,
            last_updated TEXT,
            head_code TEXT,
            neg TEXT,
            UNIQUE(item_code)
        )
    """)
    conn.commit()

def update_target_price(item_code, price, brand = 0):
    item = Item(brand, item_code.lower())
    item.set_target_price(price)

def update_average_price(item_code, brand = 0, brand_bool = False):
    item = Item(brand, item_code.lower())
    if brand_bool:
        timestamp, price = scrape_average_sold(str(item), neg=item._neg)[-2:]
    else:
        timestamp, price = scrape_average_sold(item_code, neg=item._neg)[-2:]
    
    conn = sqlite3.connect("market.db")
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE items SET
        ave_price_sold = {price},
        last_updated = "{timestamp}"
        WHERE item_code = "{item_code}"
    """)

    conn.commit()
    
    return item_code, timestamp, price

def update_all_average_price():
    conn = sqlite3.connect("market.db")
    cur = conn.cursor()
    items = cur.execute("""
        SELECT *
        FROM items
    """).fetchall()
    
    for item in items:
        update_average_price(item[2])
    
    print ("Updated average price sold for all items!")

def update_head_code(item_code):
    item = Item(0, item_code)
    code = parse_head(item_code, neg=item._neg)
    conn = sqlite3.connect("market.db")
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE items SET
        head_code = "{code}"
        WHERE item_code = "{item_code}"
    """)
    conn.commit()

def check_new_entries(item_code, set_target = 0):
    item = Item(0, item_code)
    code = parse_head(item_code, neg=item._neg)
    conn = sqlite3.connect("market.db")
    cur = conn.cursor()
    old_head = cur.execute(f"""
        SELECT head_code
        FROM items
        WHERE item_code = "{item_code}"
    """)
    old_code = old_head.fetchone()[0]
    
    if old_code == code:
        print("No new updates!")
        return 0
    
    else:
        offset = code.find(old_code[:3])
    
    new_entries = scrape_head(item_code, offset, neg=item._neg)
    cur.execute(f"""
        UPDATE items SET
        head_code = "{code}"
        WHERE item_code = "{item_code}"
    """)
    conn.commit()

    if set_target > 2:
        update_target_price(item_code, set_target)
        new_entries = filter_target_price(item_code, new_entries)

    elif set_target == 1:
        new_entries = filter_target_price(item_code, new_entries)

    return new_entries

def parse_link_from_entry(entry):
    item_link = entry._link
    link = "https://" + ROOT_URL + "item/" + item_link
    return link

def parse_alt_from_entry(entry):
    return entry._alt

def parse_price_from_entry(entry):
    return "¥" + entry._price

def parse_single_entry(entry):
    title = parse_alt_from_entry(entry)
    link = parse_link_from_entry(entry)
    price = parse_price_from_entry(entry)

    return title, link, price

def parse_all_entry(entries: tuple):
    result = []
    for e in entries:
        result.append(parse_single_entry(e))
    return result

def check_all_updates(target_price_bool = False):
    conn = sqlite3.connect("market.db")
    cur = conn.cursor()
    items = cur.execute("""
        SELECT *
        FROM items
    """).fetchall()
    results = []
    for item in items:
        if target_price_bool:
            new_entries = check_new_entries(item[2], target_price_bool)
        new_entries = check_new_entries(item[2])
    
    return results

def filter_target_price(item_code, entries):
    conn = sqlite3.connect("market.db")
    cur = conn.cursor()
    query = cur.execute(f"""
        SELECT *
        FROM items
        WHERE item_code = "{item_code}"
    """).fetchone()
    target_price = query[4]
    if target_price == None:
        print ('Target price is NULL..\nSetting Average price sold as target price.')
        cur.execute(f"""
            UPDATE items SET
            target_price = {query[3]}
            WHERE item_code = "{item_code}"
        """)
        target_price = query[3]
    
    conn.commit()
    filtered_entries = []
    for e in entries:
        if e._price <= target_price:
            filtered_entries.append(e)
    
    return filtered_entries

if __name__ == "__main__":
    db_init("market.db")
    #add_item("Pioneer","ddj 400",["箱"])
    #add_item("Apple","macbook air m1")
    #add_item("Google","pixel 6a", neg=["箱","フィルム","ケース"])

    #update_all_average_price()

    for update in check_all_updates(target_price_bool=True):
        item, result = update[0], update[1]
        if result:
            for res in result:
                title, link, price = parse_all_entry(res[1])
                print (f"New {item} post matched!: \n\nTitle:{title}\nLink:{link}\nPrice:{price}")
                break
    else:
        print ("No match found for all items!")