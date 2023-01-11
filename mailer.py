from main import *
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def update_all(set_target):
    payload = []
    for update in check_all_updates(target_price_bool=set_target):  
        item, result = update[0], update[1]
        if result:
            for res in result:
                title, link, price = parse_single_entry(res)
                payload.append ((item, f"<br><br>Title: {title}<br>Link: <a href='{link}'>Link</a><br>Price:{price}"))
            return payload
    else:
        payload.append((0, "No match found for all items!"))
        return payload

def quick_check(item_code, target_price, pages=3, neg=None):
    payload = []
    for res in fast_item_query(item_code, target_price=target_price, pages=pages, neg=neg):
        if res:
            title, link, price = res
            payload.append((item_code, f"<br><br>Title: {title}<br>Link: <a href='{link}'>Link</a><br>Price:{price}"))
        else:
            break
        return payload
    else:
        payload.append((0,"No match found for quick search!"))


def update_all_bytp(set_target=True):
    return update_all(set_target=set_target)

def update_all_nofilter(set_target=False):
    return update_all(set_target=set_target)

def update_oneitem(item_code, set_target=True):
    entries = check_one_update(item_code, set_target)
    payload = []
    if entries:

        for res in entries:
            title, link, price = parse_single_entry(res)
            payload.append((item_code, f"<br><br>Title: {title}<br>Link: <a href='{link}'>Link</a><br>Price: {price}"))
        return payload

    else:
        payload.append((0, f"No new update for {item_code}"))
        return payload

def parse_payload(payload):
    message = ""
    divider = "<br /><hr width=100%>"
    for item, entry in payload:
        message += f"New posts for {item}:<br>" + entry + divider
    return message
        


def send_mail(receiver, payload, subject, user = 'user', pw = 'password'):
    

    # Message, Generation
    message = MIMEMultipart()
    message["From"] = user
    message["To"] = receiver
    message["Subject"] = subject
    
    body = parse_payload(payload)
    mimetext = MIMEText(body, 'html')
    message.attach(mimetext)

    # Server Initialization
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(user, pw)
    message_text = message.as_string()
    s.sendmail(user, receiver, message_text)
    s.close()

def check_payload(payload):
    if payload[0][0]:
        send_mail('juncobots@mail.com', payload, 'MERCARI new POSTS!', user='uchiyamajunrei@gmail.com', pw='haiuvqjmkolyyioe')
    else:
        print(payload[0][1])
    


if __name__ == "__main__":
    payload = update_all_nofilter()
    check_payload(payload)
    