from main import *

def update_all(set_target):
    message = ""
    for update in check_all_updates(target_price_bool=set_target):  
        item, result = update[0], update[1]
        if result:
            for res in result:
                title, link, price = parse_single_entry(res)
                message += (f"\nNew {item} post matched!: \n\nTitle:{title}\nLink:{link}\nPrice:{price}")
                return message
    else:
        return "No match found for all items!"

def update_all_bytp(set_target=True):
    return update_all(set_target=set_target)

def update_all_nofilter(set_target=False):
    return update_all(set_target=set_target)

def update_oneitem(item_code, set_target=True):
    entries = check_one_update(item_code, set_target)
    message = ""
    if entries:

        for res in entries:
            title, link, price = parse_single_entry(res)
            message += (f"\nNew {item_code} post matched!: \n\nTitle:{title}\nLink:{link}\nPrice:{price}")
            return message
    else:
        return f"No new update for {item_code}"
if __name__ == "__main__":
    print(update_all_nofilter())
    #print (update_oneitem("pixel 6a"))