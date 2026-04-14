"""PharmIQ — Invoice PDF Generator"""
from datetime import datetime
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas

def generate_invoice(cart,total,invoice_number):
    filename=f"invoice_{invoice_number}.pdf"
    c=canvas.Canvas(filename,pagesize=A5); W,H=A5
    c.setFillColorRGB(0.137,0.122,0.180); c.rect(0,H-100,W,100,fill=True,stroke=False)
    c.setFillColorRGB(0.537,0.706,0.980); c.setFont("Helvetica-Bold",20); c.drawCentredString(W/2,H-42,"PharmIQ")
    c.setFont("Helvetica",11); c.setFillColorRGB(0.804,0.839,0.957); c.drawCentredString(W/2,H-62,"Smart Pharmacy Management System")
    c.setFillColorRGB(0.18,0.18,0.28); c.rect(0,H-140,W,40,fill=True,stroke=False)
    c.setFillColorRGB(0.804,0.839,0.957); c.setFont("Helvetica-Bold",10)
    c.drawString(20,H-118,f"Invoice #: {invoice_number}"); c.drawRightString(W-20,H-118,f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y=H-165
    c.setFillColorRGB(0.537,0.706,0.980); c.rect(15,y-5,W-30,22,fill=True,stroke=False)
    c.setFillColorRGB(0.118,0.114,0.176); c.setFont("Helvetica-Bold",10)
    c.drawString(25,y+5,"Drug Name"); c.drawCentredString(W/2,y+5,"Qty"); c.drawString(W-100,y+5,"Unit Price"); c.drawRightString(W-15,y+5,"Total")
    y-=15; c.setFont("Helvetica",10)
    for i,item in enumerate(cart):
        sub=item["qty"]*item["price"]
        if i%2==0: c.setFillColorRGB(0.118,0.114,0.176)
        else: c.setFillColorRGB(0.137,0.122,0.180)
        c.rect(15,y-8,W-30,20,fill=True,stroke=False)
        c.setFillColorRGB(0.804,0.839,0.957)
        c.drawString(25,y+3,item["name"][:24]); c.drawCentredString(W/2,y+3,str(item["qty"]))
        c.drawString(W-100,y+3,f"{item['price']:,.0f}"); c.drawRightString(W-15,y+3,f"{sub:,.0f}"); y-=22
    y-=10; c.setFillColorRGB(0.267,0.247,0.380); c.rect(15,y-8,W-30,28,fill=True,stroke=False)
    c.setFillColorRGB(0.537,0.706,0.980); c.setFont("Helvetica-Bold",13)
    c.drawString(25,y+8,"Total Amount:"); c.drawRightString(W-15,y+8,f"{total:,.0f} IQD")
    c.setFillColorRGB(0.18,0.18,0.28); c.rect(0,0,W,40,fill=True,stroke=False)
    c.setFillColorRGB(0.804,0.839,0.957); c.setFont("Helvetica",9)
    c.drawCentredString(W/2,25,"Thank you for your purchase!"); c.drawCentredString(W/2,12,"PharmIQ © 2026")
    c.save(); return filename
