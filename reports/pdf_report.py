"""PharmIQ — PDF Reports with Arabic Support"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from database.crud import get_all_drugs, get_all_sales, get_today_revenue, get_today_sales
from logic.rtl_helper import ar

def _load_font():
    for path, name in [("C:/Windows/Fonts/arial.ttf","Arial"),("C:/Windows/Fonts/tahoma.ttf","Tahoma"),("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","DejaVu")]:
        if os.path.exists(path):
            try: pdfmetrics.registerFont(TTFont(name,path)); return name
            except: pass
    return "Helvetica"

FONT = _load_font()

def _header(c,w,h,sub):
    c.setFillColorRGB(0.118,0.114,0.180); c.rect(0,h-75,w,75,fill=True,stroke=False)
    c.setFillColorRGB(0.537,0.706,0.980); c.setFont(FONT,22); c.drawCentredString(w/2,h-38,"PharmIQ")
    c.setFont(FONT,11); c.setFillColorRGB(0.804,0.839,0.957); c.drawCentredString(w/2,h-58,ar(sub))
    c.setFont(FONT,9); c.drawString(30,h-70,f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    return h-95

def _th(c,y,cols,fill=(0.182,0.416,0.631)):
    c.setFillColorRGB(*fill); c.rect(30,y-6,535,22,fill=True,stroke=False)
    c.setFillColorRGB(1,1,1); c.setFont(FONT,10)
    for lbl,x in cols: c.drawString(x,y+5,lbl)
    return y-28

def generate_drugs_pdf(session,filename="drugs_report.pdf"):
    drugs=get_all_drugs(session); c=canvas.Canvas(filename,pagesize=A4); W,H=A4
    y=_header(c,W,H,"تقرير الأدوية والمخزون — Drugs & Inventory Report")
    hcols=[("ID",35),("Trade Name",80),("Category",210),("Qty",315),("Min",355),("Price",395),("Expiry",450),("Status",510)]
    y=_th(c,y,hcols); c.setFont(FONT,9)
    low=exp=expired=0
    for i,d in enumerate(drugs):
        if y<55:
            c.showPage(); y=_header(c,W,H,"تقرير الأدوية — (تابع)"); y=_th(c,y,hcols); c.setFont(FONT,9)
        if d.is_expired: c.setFillColorRGB(0.28,0.06,0.12); expired+=1
        elif d.is_low_stock: c.setFillColorRGB(0.22,0.10,0.06); low+=1
        elif d.is_expiring_soon: c.setFillColorRGB(0.22,0.17,0.05); exp+=1
        elif i%2==0: c.setFillColorRGB(0.09,0.08,0.13)
        else: c.setFillColorRGB(0.11,0.10,0.16)
        c.rect(30,y-6,535,18,fill=True,stroke=False); c.setFillColorRGB(0.80,0.84,0.96)
        c.drawString(35,y,str(d.id)); c.drawString(80,y,d.trade_name[:22]); c.drawString(210,y,(d.category or "")[:16])
        c.drawString(315,y,str(d.quantity)); c.drawString(355,y,str(d.min_quantity))
        c.drawString(395,y,f"{d.price:,.0f}"); c.drawString(450,y,str(d.expiry_date) if d.expiry_date else "—")
        if d.is_expired: c.setFillColorRGB(1,0.4,0.4); c.drawString(510,y,"EXPIRED")
        elif d.is_low_stock: c.setFillColorRGB(1,0.7,0.3); c.drawString(510,y,"LOW")
        elif d.is_expiring_soon: c.setFillColorRGB(1,0.9,0.3); c.drawString(510,y,"EXPIRING")
        c.setFillColorRGB(0.80,0.84,0.96); y-=20
    y-=15; c.setFillColorRGB(0.118,0.114,0.180); c.rect(30,y-10,535,40,fill=True,stroke=False)
    c.setFillColorRGB(0.537,0.706,0.980); c.setFont(FONT,11)
    c.drawString(40,y+15,f"Total: {len(drugs)}  |  Expired: {expired}  |  Low: {low}  |  Expiring: {exp}")
    c.save(); return filename

def generate_sales_pdf(session,filename="sales_report.pdf"):
    sales=get_all_sales(session); ts=get_today_sales(session); tr=get_today_revenue(session)
    c=canvas.Canvas(filename,pagesize=A4); W,H=A4
    y=_header(c,W,H,"تقرير المبيعات — Sales Report")
    c.setFillColorRGB(0.05,0.25,0.10); c.rect(30,y-10,535,35,fill=True,stroke=False)
    c.setFillColorRGB(0.65,0.90,0.65); c.setFont(FONT,11)
    c.drawString(40,y+10,ar(f"مبيعات اليوم: {len(ts)} عملية"))
    c.drawRightString(560,y+10,ar(f"إيرادات اليوم: {tr:,.0f} IQD")); y-=50
    hcols=[("ID",35),("Drug Name",75),("Qty",260),("Total (IQD)",310),("Date",430)]
    y=_th(c,y,hcols,fill=(0.05,0.25,0.10)); c.setFont(FONT,9); total=0
    for i,s in enumerate(sales):
        if y<55:
            c.showPage(); y=_header(c,W,H,"تقرير المبيعات — (تابع)"); y=_th(c,y,hcols,fill=(0.05,0.25,0.10)); c.setFont(FONT,9)
        if i%2==0: c.setFillColorRGB(0.09,0.08,0.13)
        else: c.setFillColorRGB(0.11,0.10,0.16)
        c.rect(30,y-6,535,18,fill=True,stroke=False); c.setFillColorRGB(0.80,0.84,0.96)
        dn=s.drug.trade_name if s.drug else "N/A"; sd=s.sale_date.strftime("%Y-%m-%d %H:%M") if s.sale_date else "—"
        c.drawString(35,y,str(s.id)); c.drawString(75,y,dn[:25]); c.drawString(260,y,str(s.quantity_sold))
        c.drawString(310,y,f"{s.total_price:,.0f}"); c.drawString(430,y,sd); total+=s.total_price; y-=20
    y-=15; c.setFillColorRGB(0.05,0.25,0.10); c.rect(30,y-10,535,30,fill=True,stroke=False)
    c.setFillColorRGB(0.65,0.90,0.65); c.setFont(FONT,13); c.drawString(40,y+5,ar(f"الإجمالي الكلي: {total:,.0f} دينار عراقي"))
    c.save(); return filename
