from main import *

def update_mail(set_target = 0):
    message = ""
    for update in check_all_updates(target_price_bool=set_target):
        item, result = update[0], update[1]
        if result:
            for res in result:
                title, link, price = parse_all_entry(res[1])
                message += (f"\nNew {item} post matched!: \n\nTitle:{title}\nLink:{link}\nPrice:{price}")
                return message
    else:
        return "No match found for all items!"

if __name__ == "__main__":
    print (update_mail())