import os, re, datetime, requests, psycopg2

URL      = "https://www.interspar.at/shop/lebensmittel/" \
           "s-budget-basmati-reis/p/7979828"
PRICE_RE = r"(\d{1,3},\d{2})\s*€"
DB       = os.environ["DATABASE_URL"]

def fetch_price():
    html = requests.get(URL,headers={"User-Agent":"Mozilla/5.0"}).text
    m = re.search(PRICE_RE, html)
    if not m:
        raise RuntimeError("Preis nicht gefunden – Regex prüfen!")
    return float(m.group(1).replace(",", "."))

def store(p):
    with psycopg2.connect(DB,sslmode="require") as c:
        with c.cursor() as cur:
            cur.execute("""create table if not exists price_history(
                             ts date primary key, price numeric)""")
            cur.execute("""insert into price_history(ts,price)
                           values(%s,%s)
                           on conflict (ts) do update
                           set price = excluded.price""",
                        (datetime.date.today(), p))

if __name__ == "__main__":
    price = fetch_price()
    store(price)
    print("Gespeichert:", price, "€")
