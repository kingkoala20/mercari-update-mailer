from scrape import *

DT_FORMAT = "%Y-%m-%d, %H:%M"
ROOT_URL ="jp.mercari.com/"

def add_item(brand, item_code, neg=None, brand_dependent=False):
    if brand_dependent:
        item = Item(brand, brand + " " + item_code, neg=neg)
    else:
        item = Item(brand, item_code, neg=neg)
    update_average_price(item._item_code)
    update_head_code(item._item_code)

        

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

def update_target_price(item_code, price=0, brand = 0):
    item = Item(brand, item_code.lower())
    if price:
        item.set_target_price(price)
    else:
        item.set_target_price(item._average_price_sold)
    return item.target_price

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

def check_initial_entries (item_code, filterbytp = True, target_price = 0, pages=3):
    item = Item(0, item_code)
    item.target_price = update_target_price(item_code, target_price)
    entries = scrape_entries(item._item_code, "sale", pages=pages, neg=item._neg)[2]
    filtered = []
    if filterbytp:
        for e in entries:
            if e._price <= item.target_price:
                filtered.append(e)
        return filtered
    else:
        return entries

def fast_item_query(item_code, target_price=0, pages=3, neg=None):
    entries = scrape_entries(item_code, "sale", pages=pages, neg=neg)[2]
    result = []
    if target_price:
        for e in entries:
            if e._price <= target_price:
                result.append(e)
    return parse_all_entry(result)

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
        return 0
    
    else:
        offset = code.find(old_code[:3])
    
    new_entries = scrape_head(item_code, offset, neg=item._neg)
    
    

    if set_target > 2:
        update_target_price(item_code, set_target)
        new_entries = filter_target_price(item_code, new_entries)

    elif set_target == 1:
        new_entries = filter_target_price(item_code, new_entries)


    cur.execute(f"""
        UPDATE items SET
        head_code = "{code}"
        WHERE item_code = "{item_code}"
    """)
    conn.commit()
    return new_entries

def parse_link_from_entry(entry):
    item_link = entry._link
    link = "https://" + ROOT_URL + "item/" + item_link
    return link

def parse_alt_from_entry(entry):
    return entry._alt

def parse_price_from_entry(entry):
    return "¥" + str(entry._price)

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

def check_all_updates(target_price_bool):
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
        results.append((item[2],new_entries))
    
    return results

def check_one_update(item_code, target_price_bool):
    item = Item(0, item_code)
    if target_price_bool:
        new_entries = check_new_entries(item_code, target_price_bool)
    else:
        new_entries = check_new_entries(item_code)
    return new_entries

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

    #update_target_price("macbook air m1")
    #update_target_price("pixel 6a")
    #add_item("Gucci","リュック", brand_dependent=True)
    #print(check_initial_entries("gucci リュック"))
    print(fast_item_query("gucci リュック", 10000, pages=5))