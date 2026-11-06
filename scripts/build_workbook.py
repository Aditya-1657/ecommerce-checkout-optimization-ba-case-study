"""Builds analysis/Checkout_Funnel_Analysis.xlsx (formula-driven) from the CSV."""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter

df = pd.read_csv("data/checkout_sessions.csv", keep_default_na=False)
N = len(df); LAST = N + 1

F = "Arial"
H = Font(name=F, bold=True, color="FFFFFF", size=10); HF = PatternFill("solid", fgColor="1F3A5F")
B = Font(name=F, size=10); BB = Font(name=F, size=10, bold=True)
T = Font(name=F, size=14, bold=True, color="1F3A5F"); SUB = Font(name=F, size=12, bold=True, color="1F3A5F")
INP = Font(name=F, size=10, color="0000FF", bold=True); INPF = PatternFill("solid", fgColor="FFFF00")
RED = PatternFill("solid", fgColor="F6D9D5"); GRY = PatternFill("solid", fgColor="EEF2F7")
thin = Side(style="thin", color="BBBBBB"); BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
RIGHT = Alignment(horizontal="right")

wb = Workbook()

def hdr(ws, row, labels, col=1):
    for i, l in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=l)
        c.font, c.fill, c.border = H, HF, BOX
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 34

def box(ws, rng, fmt=None, font=B, fill=None):
    for row in ws[rng]:
        for c in row:
            c.font = font; c.border = BOX
            if fmt: c.number_format = fmt
            if fill: c.fill = fill

def widths(ws, w):
    for i, x in enumerate(w, 1): ws.column_dimensions[get_column_letter(i)].width = x

# ================= Data =================
wd = wb.active; wd.title = "Data"
cols = list(df.columns)
wd.append(cols)
for t in df.itertuples(index=False):
    row = list(t)
    row[1] = pd.Timestamp(row[1]).date()
    wd.append(row)
hdr(wd, 1, cols)
for row in wd.iter_rows(min_row=2, max_row=LAST):
    for c in row: c.font = B
    row[1].number_format = "yyyy-mm-dd"
wd.freeze_panes = "A2"; wd.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{LAST}"
widths(wd, [11, 12, 11, 15, 12, 10, 12, 12, 13, 11, 22, 18, 26, 10, 10])

def R(col): return f"Data!${col}$2:${col}${LAST}"
DEV, CT, CART, SHIP, LOAD, STEP, TAG, CONV = R("C"), R("E"), R("G"), R("H"), R("I"), R("J"), R("M"), R("O")

# ================= Read Me =================
rm = wb.create_sheet("Read Me", 0)
rm["A1"] = "E-Commerce Checkout Funnel Analysis"; rm["A1"].font = T
notes = [
    ("Purpose", "Find which checkout step loses the most customers and how much cart value is at stake."),
    ("Data", "25,000 SIMULATED cart sessions (Jul-Sep 2026) from scripts/generate_dataset.py. This is not real company data."),
    ("Key field", "last_step_reached: 1 Cart, 2 Login/Account, 3 Shipping, 4 Delivery, 5 Payment, 6 Gateway authorisation, 7 Order confirmed."),
    ("Sheets", "Funnel = overall drop-off | Segments = device, customer type, load time, shipping | Exit Reasons = tags captured at exit | Impact Scenario = what-if model."),
    ("How it works", "Every figure on the analysis sheets is a live formula pointing at the Data sheet."),
    ("Colour code", "Blue text on yellow = assumption you can change (Impact Scenario sheet). Black = formula. Red-shaded rows = payment stage."),
    ("Caution", "Recovery rates on the Impact Scenario sheet are assumptions for discussion, not forecasts. Validate with an A/B test."),
]
for i, (a, b) in enumerate(notes, 3):
    rm.cell(i, 1, a).font = BB
    c = rm.cell(i, 2, b); c.font = B; c.alignment = Alignment(wrap_text=True, vertical="top")
    rm.row_dimensions[i].height = 30
widths(rm, [16, 110])

# ================= Funnel =================
fu = wb.create_sheet("Funnel", 1)
fu["A1"] = "AS-IS checkout funnel"; fu["A1"].font = T
fu["A2"] = "All figures calculated from the Data sheet."; fu["A2"].font = Font(name=F, size=9, italic=True)
hdr(fu, 4, ["Step", "Step name", "Sessions reached", "Sessions lost at this step", "Pass rate to next step",
            "Drop-off rate", "% of all lost sessions", "Cumulative conversion", "Lost cart value (USD)", "% of lost value"])
names = ["Cart", "Login / Create Account", "Shipping Address", "Delivery Options", "Payment Details",
         "Gateway Authorisation", "Order Confirmed"]
for i, n in enumerate(names):
    r = 5 + i
    fu.cell(r, 1, i + 1); fu.cell(r, 2, n)
    fu.cell(r, 3, f'=COUNTIF({STEP},">="&A{r})')
    fu.cell(r, 8, f"=C{r}/$C$5")
    if i < 6:
        fu.cell(r, 4, f"=C{r}-C{r+1}")
        fu.cell(r, 5, f"=C{r+1}/C{r}")
        fu.cell(r, 6, f"=1-E{r}")
        fu.cell(r, 7, f"=D{r}/$D$12")
        fu.cell(r, 9, f"=SUMIFS({CART},{STEP},A{r},{CONV},0)")
        fu.cell(r, 10, f"=I{r}/$I$12")
    else:
        for c in (4, 5, 6, 7, 9, 10): fu.cell(r, c, "-")
fu["B12"] = "Total lost (not converted)"
fu["D12"] = "=SUM(D5:D10)"; fu["G12"] = "=SUM(G5:G10)"; fu["I12"] = "=SUM(I5:I10)"; fu["J12"] = "=SUM(J5:J10)"
box(fu, "A5:J12")
for r in (9, 10):
    for c in range(1, 11): fu.cell(r, c).fill = RED
for c in range(1, 11): fu.cell(12, c).font = BB; fu.cell(12, c).fill = GRY
for r in range(5, 13):
    for c in (3, 4): fu.cell(r, c).number_format = "#,##0"
    for c in (5, 6, 7, 8, 10): fu.cell(r, c).number_format = "0.0%"
    fu.cell(r, 9).number_format = "$#,##0"
    for c in range(3, 11): fu.cell(r, c).alignment = RIGHT

fu["A14"] = "Payment stage summary (steps 5 and 6 together)"; fu["A14"].font = SUB
summary = [
    ("Sessions that reached Payment Details", "=C9", "#,##0"),
    ("Sessions lost between Payment Details and Order Confirmed", "=D9+D10", "#,##0"),
    ("Payment-stage abandonment rate", "=E16/E15", "0.0%"),
    ("Cart value lost in payment stage (USD)", "=I9+I10", "$#,##0"),
    ("Payment stage share of all lost sessions", "=G9+G10", "0.0%"),
    ("Overall cart-to-order conversion", "=H11", "0.0%"),
    ("Overall cart abandonment", "=1-H11", "0.0%"),
]
for i, (lab, f, fmt) in enumerate(summary, 15):
    fu.merge_cells(start_row=i, start_column=1, end_row=i, end_column=4)
    fu.cell(i, 1, lab).font = B
    c = fu.cell(i, 5, f); c.font = BB; c.number_format = fmt; c.alignment = RIGHT
    for cc in range(1, 6): fu.cell(i, cc).border = BOX
widths(fu, [8, 26, 14, 15, 14, 12, 14, 14, 16, 12])

ch = BarChart(); ch.type = "col"; ch.title = "Sessions reaching each step"; ch.style = 10
ch.add_data(Reference(fu, min_col=3, min_row=4, max_row=11), titles_from_data=True)
ch.set_categories(Reference(fu, min_col=2, min_row=5, max_row=11))
ch.legend = None; ch.height = 8.5; ch.width = 18
fu.add_chart(ch, "G14")

# ================= Segments =================
sg = wb.create_sheet("Segments", 2)
sg["A1"] = "Segment analysis"; sg["A1"].font = T

# A. device
sg["A3"] = "A. By device"; sg["A3"].font = SUB
hdr(sg, 4, ["Device", "Sessions", "Orders", "Cart-to-order %", "Reached Payment", "Payment pass % (5 to 6)",
            "Reached Gateway", "Gateway pass % (6 to 7)"])
for i, d in enumerate(["Desktop", "Tablet", "Mobile"]):
    r = 5 + i
    sg.cell(r, 1, d)
    sg.cell(r, 2, f'=COUNTIF({DEV},A{r})')
    sg.cell(r, 3, f'=COUNTIFS({DEV},A{r},{STEP},7)')
    sg.cell(r, 4, f"=C{r}/B{r}")
    sg.cell(r, 5, f'=COUNTIFS({DEV},A{r},{STEP},">=5")')
    sg.cell(r, 7, f'=COUNTIFS({DEV},A{r},{STEP},">=6")')
    sg.cell(r, 6, f"=G{r}/E{r}")
    sg.cell(r, 8, f"=C{r}/G{r}")
box(sg, "A5:H7")
for r in range(5, 8):
    for c in (2, 3, 5, 7): sg.cell(r, c).number_format = "#,##0"
    for c in (4, 6, 8): sg.cell(r, c).number_format = "0.0%"
for c in range(1, 9): sg.cell(7, c).fill = RED

# B. customer type
sg["A10"] = "B. Forced account creation: Login / Create Account step (2 to 3)"; sg["A10"].font = SUB
hdr(sg, 11, ["Customer type", "Reached login step", "Moved to shipping", "Step pass %"])
for i, d in enumerate(["New", "Returning"]):
    r = 12 + i
    sg.cell(r, 1, d)
    sg.cell(r, 2, f'=COUNTIFS({CT},A{r},{STEP},">=2")')
    sg.cell(r, 3, f'=COUNTIFS({CT},A{r},{STEP},">=3")')
    sg.cell(r, 4, f"=C{r}/B{r}")
box(sg, "A12:D13")
for r in (12, 13):
    for c in (2, 3): sg.cell(r, c).number_format = "#,##0"
    sg.cell(r, 4).number_format = "0.0%"

# C. load time
sg["A16"] = "C. Payment page load time: Payment Details step (5 to 6)"; sg["A16"].font = SUB
hdr(sg, 17, ["Load time bucket", "Lower (sec)", "Upper (sec)", "Reached Payment", "Submitted payment", "Step pass %"])
buckets = [("Under 3 sec", 0, 3), ("3 to 4.5 sec", 3, 4.5), ("Over 4.5 sec", 4.5, 999)]
for i, (n, lo, hi) in enumerate(buckets):
    r = 18 + i
    sg.cell(r, 1, n); sg.cell(r, 2, lo); sg.cell(r, 3, hi)
    sg.cell(r, 4, f'=COUNTIFS({LOAD},">="&B{r},{LOAD},"<"&C{r},{STEP},">=5")')
    sg.cell(r, 5, f'=COUNTIFS({LOAD},">="&B{r},{LOAD},"<"&C{r},{STEP},">=6")')
    sg.cell(r, 6, f"=E{r}/D{r}")
box(sg, "A18:F20")
for r in range(18, 21):
    for c in (4, 5): sg.cell(r, c).number_format = "#,##0"
    sg.cell(r, 6).number_format = "0.0%"

# D. shipping
sg["A23"] = "D. Shipping cost reveal: Delivery Options step (4 to 5)"; sg["A23"].font = SUB
hdr(sg, 24, ["Shipping type", "Reached Delivery", "Moved to Payment", "Step pass %"])
sg.cell(25, 1, "Free shipping"); sg.cell(26, 1, "Paid shipping")
sg["B25"] = f'=COUNTIFS({SHIP},0,{STEP},">=4")'; sg["C25"] = f'=COUNTIFS({SHIP},0,{STEP},">=5")'
sg["B26"] = f'=COUNTIFS({SHIP},">0",{STEP},">=4")'; sg["C26"] = f'=COUNTIFS({SHIP},">0",{STEP},">=5")'
sg["D25"] = "=C25/B25"; sg["D26"] = "=C26/B26"
box(sg, "A25:D26")
for r in (25, 26):
    for c in (2, 3): sg.cell(r, c).number_format = "#,##0"
    sg.cell(r, 4).number_format = "0.0%"
widths(sg, [28, 17, 17, 16, 16, 18, 16, 18])

# ================= Exit Reasons =================
ex = wb.create_sheet("Exit Reasons", 3)
ex["A1"] = "Exit tags captured by the app (simulated)"; ex["A1"].font = T
hdr(ex, 3, ["Step lost at", "Step name", "Exit tag", "Sessions", "% of that step's exits", "Lost cart value (USD)"])
tags = [
    (4, "Delivery Options", ["Shipping cost too high", "Delivery time too long", "No preferred carrier"]),
    (5, "Payment Details", ["Payment form abandoned", "Page load too slow", "Wanted wallet option"]),
    (6, "Gateway Authorisation", ["3-D Secure timeout/fail", "Card declined", "Redirect abandoned",
                                  "Gateway error/timeout", "Session expired"]),
]
r = 4
for step, nm, lst in tags:
    first = r
    for t in lst:
        ex.cell(r, 1, step); ex.cell(r, 2, nm); ex.cell(r, 3, t)
        ex.cell(r, 4, f'=COUNTIFS({STEP},A{r},{TAG},C{r})')
        r += 1
    last = r - 1
    for k in range(first, last + 1):
        ex.cell(k, 5, f"=D{k}/SUM($D${first}:$D${last})")
        ex.cell(k, 6, f'=SUMIFS({CART},{STEP},A{k},{TAG},C{k})')
        if step == 6:
            for c in range(1, 7): ex.cell(k, c).fill = RED
box(ex, f"A4:F{r-1}")
for k in range(4, r):
    ex.cell(k, 4).number_format = "#,##0"; ex.cell(k, 5).number_format = "0.0%"; ex.cell(k, 6).number_format = "$#,##0"
for k in range(4, r):
    if ex.cell(k, 1).value == 6: 
        for c in range(1, 7): ex.cell(k, c).fill = RED
widths(ex, [12, 24, 28, 12, 20, 20])

# ================= Impact Scenario =================
im = wb.create_sheet("Impact Scenario", 4)
im["A1"] = "What-if: orders and revenue recovered by the proposed changes"; im["A1"].font = T
im["A2"] = ("Yellow cells are ASSUMPTIONS. Recovered sessions are assumed to finish the rest of the funnel at TODAY'S "
            "downstream rate, which is deliberately conservative.")
im["A2"].font = Font(name=F, size=9, italic=True)
hdr(im, 4, ["Initiative", "Targets exit at step", "Sessions lost there", "Assumed recovery %",
            "Sessions recovered", "Downstream completion rate", "Extra orders"])
init = [
    ("Guest checkout (no forced account)", 2, 0.20),
    ("Upfront shipping estimate in cart", 4, 0.15),
    ("Apple Pay / Google Pay + shorter payment form", 5, 0.20),
    ("3-D Secure 2, in-page auth, decline retry", 6, 0.25),
]
for i, (n, s, p) in enumerate(init):
    r = 5 + i
    im.cell(r, 1, n); im.cell(r, 2, s)
    im.cell(r, 3, f"=INDEX(Funnel!$D$5:$D$10,B{r})")
    c = im.cell(r, 4, p); c.font = INP; c.fill = INPF; c.number_format = "0%"
    im.cell(r, 5, f"=C{r}*D{r}")
    im.cell(r, 6, f"=Funnel!$C$11/INDEX(Funnel!$C$5:$C$11,B{r}+1)")
    im.cell(r, 7, f"=E{r}*F{r}")
box(im, "A5:G8")
for r in range(5, 9):
    im.cell(r, 4).font = INP; im.cell(r, 4).fill = INPF
    im.cell(r, 3).number_format = "#,##0"; im.cell(r, 5).number_format = "#,##0"
    im.cell(r, 6).number_format = "0.0%"; im.cell(r, 7).number_format = "#,##0"

im["A10"] = "Overlap haircut (initiatives rescue some of the same people)"; im["D10"] = 0.15
im["D10"].font = INP; im["D10"].fill = INPF; im["D10"].number_format = "0%"
im["A11"] = "Average order value, completed orders (USD)"; im["D11"] = f"=AVERAGEIFS({CART},{CONV},1)"
im["D11"].number_format = "$#,##0.00"
im["A12"] = "Baseline orders (3 months)"; im["D12"] = "=Funnel!C11"; im["D12"].number_format = "#,##0"
im["A13"] = "Extra orders after overlap haircut"; im["D13"] = "=SUM(G5:G8)*(1-D10)"; im["D13"].number_format = "#,##0"
im["A14"] = "Extra revenue, 3 months (USD)"; im["D14"] = "=D13*D11"; im["D14"].number_format = "$#,##0"
im["A15"] = "Baseline cart-to-order conversion"; im["D15"] = "=D12/Funnel!C5"; im["D15"].number_format = "0.0%"
im["A16"] = "Projected cart-to-order conversion"; im["D16"] = "=(D12+D13)/Funnel!C5"; im["D16"].number_format = "0.0%"
im["A17"] = "Relative uplift in orders"; im["D17"] = "=D13/D12"; im["D17"].number_format = "0.0%"
for r in range(10, 18):
    im.cell(r, 1).font = B
    if r != 10: im.cell(r, 4).font = BB
    for c in range(1, 5): im.cell(r, c).border = BOX
    im.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
    im.cell(r, 4).alignment = RIGHT

im["A20"] = "Sensitivity: scale every recovery % up or down"; im["A20"].font = SUB
hdr(im, 21, ["Case", "Multiplier on recovery %", "Extra orders", "Extra revenue (USD)", "Projected conversion"])
for i, (n, m) in enumerate([("Pessimistic", 0.5), ("Base", 1.0), ("Optimistic", 1.5)]):
    r = 22 + i
    im.cell(r, 1, n)
    c = im.cell(r, 2, m); c.font = INP; c.fill = INPF; c.number_format = "0.0x"
    im.cell(r, 3, f"=SUM(G5:G8)*B{r}*(1-$D$10)")
    im.cell(r, 4, f"=C{r}*$D$11")
    im.cell(r, 5, f"=($D$12+C{r})/Funnel!$C$5")
box(im, "A22:E24")
for r in range(22, 25):
    im.cell(r, 2).font = INP; im.cell(r, 2).fill = INPF
    im.cell(r, 3).number_format = "#,##0"; im.cell(r, 4).number_format = "$#,##0"; im.cell(r, 5).number_format = "0.0%"
widths(im, [48, 18, 18, 22, 18, 22, 14])

wb.move_sheet("Read Me", offset=-wb.index(wb["Read Me"]))
wb.save("analysis/Checkout_Funnel_Analysis.xlsx")
print("saved")
