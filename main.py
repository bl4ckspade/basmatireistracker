import os, json, psycopg2
from fastapi import FastAPI, Response

DB = os.environ["DATABASE_URL"]

HTML = """<!doctype html><meta charset=utf-8>
<title>S-Budget Basmati Tracker</title>
<script src=https://cdn.jsdelivr.net/npm/chart.js></script>
<canvas id=c></canvas>
<script>
fetch('/data').then(r=>r.json()).then(d=>{
 new Chart(c,{type:'line',
   data:{labels:d.map(x=>x.date),
         datasets:[{label:'Preis €',data:d.map(x=>x.price),tension:.3}]},
   options:{scales:{y:{beginAtZero:false}}}});
});
</script>"""

app = FastAPI()

def q(sql,*p):
    with psycopg2.connect(DB,sslmode="require") as c:
        with c.cursor() as cur:
            cur.execute(sql,p)
            if cur.description: return cur.fetchall()

@app.get("/")
def root():  return Response(HTML,media_type="text/html")

@app.get("/data")
def data():
    rows = q("select ts,price from price_history order by ts")
    return [{"date":r[0].isoformat(),"price":float(r[1])} for r in rows]
