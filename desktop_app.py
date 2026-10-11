"""GeM tender desktop workspace. CAPTCHA and final bid submission stay manual."""
import sys, json
from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import (QApplication,QCheckBox,QComboBox,QFrame,QHBoxLayout,QLabel,
 QLineEdit,QMainWindow,QMessageBox,QPushButton,QScrollArea,QSplitter,QVBoxLayout,QWidget)
from PySide6.QtWebEngineWidgets import QWebEngineView

PORTAL="https://gem.gov.in/"
DOCS=[
 "Udyam / MSME certificate (if applicable)","Product catalogue / technical datasheet",
 "Price list / quotation / cost breakdown","PAN card","Aadhaar / authorised signatory ID (if requested)",
 "GST registration certificate","Turnover certificate / audited financials","ITR / CA certificate (if tender asks)",
 "Experience / past performance certificates","OEM authorisation / MAF (if applicable)",
 "Bank details / cancelled cheque (if requested)","Digital Signature Certificate (DSC) ready"
]
STYLE="""
QMainWindow,QWidget{background:#f5f7fb;color:#172033;font-family:Arial;font-size:12px}
QFrame#top{background:#111827;border-radius:12px} QLabel#brand{color:white;font-size:19px;font-weight:bold}
QLabel#sub{color:#cbd5e1} QFrame#card{background:white;border:1px solid #e3e8f1;border-radius:12px}
QLabel#section{font-size:14px;font-weight:bold;color:#111827} QLabel#muted{color:#64748b}
QLineEdit,QComboBox{background:white;border:1px solid #cbd5e1;border-radius:7px;padding:8px}
QPushButton{background:#4f46e5;color:white;border:0;border-radius:8px;padding:9px;font-weight:bold}
QPushButton#secondary{background:#eef2ff;color:#3730a3;border:1px solid #c7d2fe}
QCheckBox{spacing:8px;padding:3px}
"""
class Window(QMainWindow):
 def __init__(self):
  super().__init__(); self.setWindowTitle("GeM Tender Assistant"); self.resize(1600,950); self.setMinimumSize(1100,720)
  root=QWidget(); self.setCentralWidget(root); outer=QVBoxLayout(root); outer.setContentsMargins(14,12,14,12); outer.setSpacing(10)
  top=QFrame(); top.setObjectName("top"); row=QHBoxLayout(top); row.setContentsMargins(16,12,16,12)
  labels=QVBoxLayout(); brand=QLabel("GeM Tender Assistant"); brand.setObjectName("brand"); sub=QLabel("Tender preparation workspace · human-reviewed"); sub.setObjectName("sub")
  labels.addWidget(brand); labels.addWidget(sub); row.addLayout(labels); row.addStretch()
  home=QPushButton("Open GeM home"); home.setObjectName("secondary"); home.clicked.connect(lambda:self.browser.setUrl(QUrl(PORTAL))); row.addWidget(home); outer.addWidget(top)
  split=QSplitter(Qt.Orientation.Horizontal); split.setChildrenCollapsible(False); split.addWidget(self.browser_panel()); split.addWidget(self.controls_panel()); split.setStretchFactor(0,7); split.setStretchFactor(1,3); split.setSizes([1120,480]); outer.addWidget(split,1)
  self.status=QLabel("Ready. Credentials are held in memory only."); self.status.setObjectName("muted"); outer.addWidget(self.status)
 def card(self,title):
  f=QFrame(); f.setObjectName("card"); l=QVBoxLayout(f); l.setContentsMargins(13,12,13,12); l.setSpacing(7)
  h=QLabel(title); h.setObjectName("section"); l.addWidget(h); return f
 def fieldlabel(self,t):
  x=QLabel(t); x.setObjectName("muted"); return x
 def browser_panel(self):
  f=self.card("GeM portal · embedded Chromium"); l=f.layout(); nav=QHBoxLayout()
  for text,fn in [("←",lambda:self.browser.back()),("→",lambda:self.browser.forward()),("Reload",lambda:self.browser.reload())]:
   b=QPushButton(text); b.setObjectName("secondary"); b.clicked.connect(fn); nav.addWidget(b)
  self.url=QLineEdit(PORTAL); self.url.returnPressed.connect(self.navigate); nav.addWidget(self.url,1)
  go=QPushButton("Go"); go.clicked.connect(self.navigate); nav.addWidget(go); l.addLayout(nav)
  self.browser=QWebEngineView(); self.browser.setUrl(QUrl(PORTAL)); self.browser.urlChanged.connect(lambda u:self.url.setText(u.toString()))
  self.browser.loadFinished.connect(lambda ok:self.status.setText("Page loaded. Review before using assistant actions." if ok else "Page failed to load; check connection."))
  l.addWidget(self.browser,1); note=QLabel("Solve the CAPTCHA yourself in this browser. Login filling is best-effort and may not match every page."); note.setWordWrap(True); note.setObjectName("muted"); l.addWidget(note)
  return f
 def navigate(self):
  u=self.url.text().strip()
  if u and not u.startswith(("https://","http://")): u="https://"+u
  self.browser.setUrl(QUrl(u or PORTAL))
 def controls_panel(self):
  w=QWidget(); w.setMinimumWidth(350); scroll=QScrollArea(); scroll.setWidgetResizable(True); box=QVBoxLayout(w); box.setContentsMargins(0,0,0,0); box.addWidget(scroll)
  body=QWidget(); scroll.setWidget(body); c=QVBoxLayout(body); c.setContentsMargins(0,0,0,0); c.setSpacing(9)
  login=self.card("1 · Portal sign-in"); a=login.layout()
  a.addWidget(self.fieldlabel("User ID / email / mobile")); self.uid=QLineEdit(); self.uid.setPlaceholderText("GeM login ID"); a.addWidget(self.uid)
  a.addWidget(self.fieldlabel("Password")); self.pwd=QLineEdit(); self.pwd.setEchoMode(QLineEdit.EchoMode.Password); self.pwd.setPlaceholderText("Not saved"); a.addWidget(self.pwd)
  a.addWidget(self.fieldlabel("Current CAPTCHA shown in browser")); self.cap=QLineEdit(); self.cap.setPlaceholderText("Type CAPTCHA yourself"); a.addWidget(self.cap)
  show=QCheckBox("Show password while typing"); show.toggled.connect(lambda v:self.pwd.setEchoMode(QLineEdit.EchoMode.Normal if v else QLineEdit.EchoMode.Password)); a.addWidget(show)
  fill=QPushButton("Fill login fields in browser"); fill.clicked.connect(self.fill_login); a.addWidget(fill)
  msg=QLabel("Review the page and click Login yourself. If detection fails, enter details directly in the browser."); msg.setWordWrap(True); msg.setObjectName("muted"); a.addWidget(msg); c.addWidget(login)
  filt=self.card("2 · Tender preferences"); b=filt.layout()
  b.addWidget(self.fieldlabel("Location / delivery area")); self.loc=QLineEdit(); self.loc.setPlaceholderText("Mumbai, Maharashtra / All India"); b.addWidget(self.loc)
  b.addWidget(self.fieldlabel("Buyer department / organisation")); self.dept=QLineEdit(); self.dept.setPlaceholderText("School, hospital, ministry…"); b.addWidget(self.dept)
  b.addWidget(self.fieldlabel("Supply category")); self.cat=QComboBox(); self.cat.addItems(["Any category","Stationery","Office supplies","Housekeeping / cleaning","Computers & IT","Printers & consumables","Furniture","Electrical items","Safety / PPE","Other"]); b.addWidget(self.cat)
  b.addWidget(self.fieldlabel("EMD preference")); self.emd=QComboBox(); self.emd.addItems(["Any EMD status","Prefer EMD-exempt / EMD-free","EMD required is acceptable","Only tenders requiring EMD"]); b.addWidget(self.emd)
  b.addWidget(self.fieldlabel("Keywords")); self.kw=QLineEdit(); self.kw.setPlaceholderText("Product / brand / bid keywords"); b.addWidget(self.kw)
  prep=QPushButton("Prepare search terms"); prep.setObjectName("secondary"); prep.clicked.connect(self.prepare); b.addWidget(prep)
  self.preview=QLabel("Prepared criteria appear here."); self.preview.setWordWrap(True); self.preview.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse); b.addWidget(self.preview); c.addWidget(filt)
  docs=self.card("3 · Documents to prepare"); d=docs.layout(); tip=QLabel("Requirements differ by bid. Mark ready only when valid and available."); tip.setWordWrap(True); tip.setObjectName("muted"); d.addWidget(tip)
  self.checks=[]
  for name in DOCS:
   cb=QCheckBox(name); self.checks.append(cb); d.addWidget(cb)
  c.addWidget(d)
  act=self.card("4 · Review"); e=act.layout()
  missing=QPushButton("Show missing documents"); missing.setObjectName("secondary"); missing.clicked.connect(self.missing); e.addWidget(missing)
  copy=QPushButton("Copy tender plan"); copy.clicked.connect(self.copy_plan); e.addWidget(copy)
  safety=QLabel("No CAPTCHA bypass or automatic bid submission. Verify eligibility, EMD exemption, deadlines and attachments yourself."); safety.setWordWrap(True); safety.setStyleSheet("background:#fff7ed;color:#9a3412;border:1px solid #fed7aa;border-radius:8px;padding:8px"); e.addWidget(safety); c.addWidget(act); c.addStretch(); return w
 def fill_login(self):
  user,pwd,cap=self.uid.text(),self.pwd.text(),self.cap.text()
  if not user or not pwd or not cap:
   QMessageBox.warning(self,"Missing fields","Enter user ID, password, and the CAPTCHA you read in the browser."); return
  js=f"""(()=>{{const v={{u:{json.dumps(user)},p:{json.dumps(pwd)},c:{json.dumps(cap)}}};const a=[...document.querySelectorAll('input:not([type=hidden])')];const score=(e,ws)=>ws.reduce((n,w)=>n+(([e.id,e.name,e.placeholder,e.getAttribute('aria-label'),e.autocomplete].join(' ').toLowerCase().includes(w))?1:0),0);const pick=ws=>a.map(e=>({{e,s:score(e,ws)}})).filter(x=>x.s).sort((x,y)=>y.s-x.s)[0]?.e;const pw=a.find(e=>e.type==='password')||pick(['password','passwd']);const uid=pick(['username','user id','userid','email','mobile','login']);const cap=pick(['captcha','capcha','verification code','security code']);const set=(e,x)=>{{if(!e)return false;const d=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value');d.set.call(e,x);e.dispatchEvent(new Event('input',{{bubbles:true}}));e.dispatchEvent(new Event('change',{{bubbles:true}}));return true}};return {{user:set(uid,v.u),password:set(pw,v.p),captcha:set(cap,v.c)}}}})()"""
  self.browser.page().runJavaScript(js,self.filled)
 def filled(self,res):
  self.uid.clear(); self.pwd.clear(); self.cap.clear()
  self.status.setText("Attempted to fill detected login fields. Check the browser; click Login manually. Result: "+str(res))
 def prepare(self):
  values=[f"Location: {self.loc.text().strip() or 'Any'}",f"Department: {self.dept.text().strip() or 'Any'}",f"Category: {self.cat.currentText()}",f"EMD: {self.emd.currentText()}",f"Keywords: {self.kw.text().strip() or 'None'}"]
  self.preview.setText("\n".join(values)+"\n\nApply these criteria in the visible portal and confirm the actual bid document.")
  self.status.setText("Search terms prepared; use them in GeM and verify live tender requirements.")
 def missing(self):
  m=[x.text() for x in self.checks if not x.isChecked()]
  QMessageBox.information(self,"Document checklist","Not marked ready:\n\n"+("\n".join("• "+x for x in m) if m else "All checklist items marked ready. Confirm bid-specific requirements."))
 def copy_plan(self):
  ready=[x.text() for x in self.checks if x.isChecked()]; missing=[x.text() for x in self.checks if not x.isChecked()]
  text="GeM Tender Preparation Plan\n"+f"Location: {self.loc.text() or 'Any'}\nDepartment: {self.dept.text() or 'Any'}\nCategory: {self.cat.currentText()}\nEMD: {self.emd.currentText()}\nKeywords: {self.kw.text() or 'None'}\n\nReady:\n"+"\n".join("- "+x for x in ready)+"\n\nNot marked ready:\n"+"\n".join("- "+x for x in missing)
  QApplication.clipboard().setText(text); self.status.setText("Plan copied. Credentials and CAPTCHA are not included.")
def main():
 app=QApplication(sys.argv); app.setStyle("Fusion"); app.setStyleSheet(STYLE); w=Window(); w.show(); sys.exit(app.exec())
if __name__=="__main__": main()
