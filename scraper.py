from bs4 import BeautifulSoup
import requests
import time
import random
import datetime
import smtplib
import json


def email(title, text):
    from email.mime.text import MIMEText

    with open('config.json') as data_file:
        data = json.load(data_file)
    msg = MIMEText(text.encode('utf8'), 'plain', 'utf-8')
    msg['Subject'] = title
    msg['From'] = data["me"]
    msg['To'] = data["you"]
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(data["userLogin"], data["userPassword"])
    server.sendmail(data["me"], [data["you"]], msg.as_string())
    server.quit()


def scrape(link):
    content = requests.get(link)
    soup = BeautifulSoup(content.text)
    htmls = soup.find_all("tbody", class_="item")
    return [Item(html) for html in htmls]


class Item:
    def __init__(self, html):
        self.name = html.a.text.strip()
        self.mods = []
        self.price = str(html.get('data-buyout'))
        for mod in html.descendants:
            if mod.name == "li":
                classes = mod['class']
                if 'sortable' in classes:
                    mod_text = mod.text
                    self.mods.append(mod_text)
            if mod.name == "span":
                classes = mod['class']
                if 'requirements' in classes:
                    mod_text = mod.text
                    mod_text = mod_text[mod_text.index("Verify")+7:]
                    try:
                        self.seller = mod_text[:mod.text.index("PM")]
                    except:
                        1

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.mods == other.mods

        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class URL:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.current_list = []

    def update(self):
        new_list = scrape(self.url)
        difference = []
        for item in new_list:
            if item not in self.current_list:
                difference.append(item)
                self.current_list.append(item)
        if len(difference) != 0:
            return difference
        return []

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


urls = {}


def update_urls():
    with open("searches") as f:
        content = f.readlines()
        for line in content:
            title = line.split("@")[0]
            url = line.split("@")[1].strip()
            if urls.get(title) is None:
                print("Now also searching: " + title)
                urls[title] = URL(title, url)

counter = 0

while 1:
    update_urls()
    for url in urls.values():
        new_items = url.update()
        len_items = len(new_items)
        if len_items != 0:
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')
            title = str(timestamp) + " [" + str(len_items) + "] " + url.name + " - " + url.url
            log = title + "\n\n"
            print("\n" + log[:-2])
            for item in new_items:
                log += item.name + "\n"
                for mod in item.mods:
                    log += mod + "\n"
                try:
                    log += item.seller + "\t" + item.price + "\n\n"
                except:
                    1
                print(item.name)
            email(title, log)
        if counter >= len(urls):
            time.sleep(random.random() * 250)
        counter += 1

