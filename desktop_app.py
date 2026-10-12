"""GeM tender desktop workspace with embedded Chromium and local API-key settings."""
import sys, json
from PySide6.QtCore import QUrl, Qt, QSettings
from PySide6.QtWidgets import (QApplication,QCheckBox,QComboBox,QFrame,QHBoxLayout,QLabel,
 QLineEdit,QMainWindow,QMessageBox,QPushButton,QScrollArea,QSplitter,QVBoxLayout,QWidget)
from PySide6.QtWebEngineWidgets import QWebEngineView
import keyring
from gem_bid_search import BidSearchPanel

PORTAL="https://gem.gov.in/"
KEYRING_SERVICE="GeM Tender Assistant"
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
  super().__init__(); self.setWindowTitle("GeM Tender Assistant"); self.resize(1600,950); self.setMinimumSize(1000,680)
  root=QWidget(); self.setCentralWidget(root); outer=QVBoxLayout(root); outer.setContentsMargins(12,10,12,10); outer.setSpacing(8)
  top=QFrame(); top.setObjectName("top"); row=QHBoxLayout(top); row.setContentsMargins(16,10,16,10)
  labels=QVBoxLayout(); brand=QLabel("GeM Tender Assistant"); brand.setObjectName("brand"); sub=QLabel("Tender preparation workspace · human-reviewed"); sub.setObjectName("sub")
  labels.addWidget(brand); labels.addWidget(sub); row.addLayout(labels); row.addStretch()
  login=QPushButton("Open GeM login"); login.clicked.connect(lambda:self.browser.setUrl(QUrl("https://sso.gem.gov.in/ARXSSO/oauth/doLogin"))); row.addWidget(login)
  home=QPushButton("Open GeM home"); home.setObjectName("secondary"); home.clicked.connect(lambda:self.browser.setUrl(QUrl(PORTAL))); row.addWidget(home); outer.addWidget(top)
  split=QSplitter(Qt.Orientation.Horizontal); split.setChildrenCollapsible(False); split.addWidget(self.browser_panel()); split.addWidget(self.controls_panel())
  split.setStretchFactor(0,7); split.setStretchFactor(1,3); split.setSizes([1120,480]); outer.addWidget(split,1)
  self.status=QLabel("Ready. API keys are stored in your operating system's credential store."); self.status.setObjectName("muted"); outer.addWidget(self.status)
  QSettings("GeM","TenderAssistant").setValue("last_version","1")
 def card(self,title):
  f=QFrame(); f.setObjectName("card"); l=QVBoxLayout(f); l.setContentsMargins(12,10,12,10); l.setSpacing(6)
  h=QLabel(title); h.setObjectName("section"); l.addWidget(h); return f
 def fieldlabel(self,t):
  x=QLabel(t); x.setObjectName("muted"); return x
 def browser_panel(self):
  f=self.card("GeM portal · embedded Chromium"); l=f.layout(); nav=QHBoxLayout()
  for text,fn in [("←",lambda:self.browser.back()),("→",lambda:self.browser.forward()),("Reload",lambda:self.browser.reload())]:
   b=QPushButton(text); b.setObjectName("secondary"); b.setMaximumWidth(68); b.clicked.connect(fn); nav.addWidget(b)
  self.url=QLineEdit(PORTAL); self.url.returnPressed.connect(self.navigate); nav.addWidget(self.url,1)
  go=QPushButton("Go"); go.setMaximumWidth(55); go.clicked.connect(self.navigate); nav.addWidget(go); l.addLayout(nav)
  self.browser=QWebEngineView(); self.browser.setUrl(QUrl(PORTAL)); self.browser.urlChanged.connect(lambda u:self.url.setText(u.toString()))
  self.browser.loadFinished.connect(self.page_loaded); l.addWidget(self.browser,1)
  note=QLabel("Use Open GeM login to reach the official sign-in page. Solve CAPTCHA yourself; if fields are not detected, type directly into the portal."); note.setWordWrap(True); note.setObjectName("muted"); l.addWidget(note)
  return f
 def page_loaded(self,ok):
  self.status.setText("GeM page loaded. Review before proceeding." if ok else "The page did not load. Check internet or press Reload.")
 def navigate(self):
  u=self.url.text().strip()
  if u and not u.startswith(("https://","http://")): u="https://"+u
  self.browser.setUrl(QUrl(u or PORTAL))
 def controls_panel(self):
  w=QWidget(); w.setMinimumWidth(300); scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
  box=QVBoxLayout(w); box.setContentsMargins(0,0,0,0); box.addWidget(scroll)
  body=QWidget(); scroll.setWidget(body); c=QVBoxLayout(body); c.setContentsMargins(0,0,0,0); c.setSpacing(8)
  search=self.card("3 · Live bid discovery & recommendations"); search.layout().addWidget(BidSearchPanel(self.browser, self.status))
  c.addWidget(search)
  login=self.card("1 · Portal sign-in"); a=login.layout()
  a.addWidget(self.fieldlabel("User ID / email / mobile")); self.uid=QLineEdit(); self.uid.setPlaceholderText("GeM login ID"); a.addWidget(self.uid)
  a.addWidget(self.fieldlabel("Password")); self.pwd=QLineEdit(); self.pwd.setEchoMode(QLineEdit.EchoMode.Password); self.pwd.setPlaceholderText("Password (not saved)"); a.addWidget(self.pwd)
  a.addWidget(self.fieldlabel("CAPTCHA shown in browser")); self.cap=QLineEdit(); self.cap.setPlaceholderText("Type CAPTCHA yourself"); a.addWidget(self.cap)
  fill=QPushButton("Fill login fields"); fill.clicked.connect(self.fill_login); a.addWidget(fill)
  msg=QLabel("Credentials are cleared after filling. Inspect the browser and click Login yourself."); msg.setWordWrap(True); msg.setObjectName("muted"); a.addWidget(msg); c.addWidget(login)
  settings=self.card("2 · AI API keys (optional)"); s=settings.layout()
  s.addWidget(self.fieldlabel("Gemini API key")); self.gemini_key=QLineEdit(); self.gemini_key.setEchoMode(QLineEdit.EchoMode.Password); self.gemini_key.setPlaceholderText("Paste Gemini key"); s.addWidget(self.gemini_key)
  s.addWidget(self.fieldlabel("Groq API key")); self.groq_key=QLineEdit(); self.groq_key.setEchoMode(QLineEdit.EchoMode.Password); self.groq_key.setPlaceholderText("Paste Groq key"); s.addWidget(self.groq_key)
  saved=QLabel(self.key_status()); saved.setObjectName("muted"); self.key_status_label=saved; s.addWidget(saved)
  save=QPushButton("Save API keys securely"); save.setObjectName("secondary"); save.clicked.connect(self.save_keys); s.addWidget(save)
  links=QLabel('<a href="https://aistudio.google.com/apikey">Get Gemini key</a> · <a href="https://console.groq.com/keys">Get Groq key</a>'); links.setOpenExternalLinks(True); s.addWidget(links)
  note=QLabel("Keys are stored locally using the OS credential store, not in this repository. AI calls send text to the selected provider."); note.setWordWrap(True); note.setObjectName("muted"); s.addWidget(note); c.addWidget(settings)
  filt=self.card("3 · Tender preferences"); b=filt.layout()
  b.addWidget(self.fieldlabel("Location / delivery area")); self.loc=QLineEdit(); self.loc.setPlaceholderText("Mumbai, Maharashtra / All India"); b.addWidget(self.loc)
  b.addWidget(self.fieldlabel("Buyer department / organisation")); self.dept=QLineEdit(); self.dept.setPlaceholderText("School, hospital, ministry…"); b.addWidget(self.dept)
  b.addWidget(self.fieldlabel("Supply category")); self.cat=QComboBox(); self.cat.addItems(["Any category","Stationery","Office supplies","Housekeeping / cleaning","Computers & IT","Printers & consumables","Furniture","Electrical items","Safety / PPE","Other"]); b.addWidget(self.cat)
  b.addWidget(self.fieldlabel("EMD preference")); self.emd=QComboBox(); self.emd.addItems(["Any EMD status","Prefer EMD-exempt / EMD-free","EMD required is acceptable","Only tenders requiring EMD"]); b.addWidget(self.emd)
  b.addWidget(self.fieldlabel("Keywords")); self.kw=QLineEdit(); self.kw.setPlaceholderText("Product / brand / bid keywords"); b.addWidget(self.kw)
  prep=QPushButton("Prepare search terms"); prep.setObjectName("secondary"); prep.clicked.connect(self.prepare); b.addWidget(prep)
  self.preview=QLabel("Prepared criteria appear here."); self.preview.setWordWrap(True); self.preview.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse); b.addWidget(self.preview); c.addWidget(filt)
  docs=self.card("4 · Documents to prepare"); d=docs.layout(); tip=QLabel("Mark ready only when valid. Check the actual bid for required documents."); tip.setWordWrap(True); tip.setObjectName("muted"); d.addWidget(tip)
  self.checks=[]
  for name in DOCS:
   cb=QCheckBox(name); self.checks.append(cb); d.addWidget(cb)
  c.addLayout(d)
  act=self.card("5 · Review"); e=act.layout()
  missing=QPushButton("Show missing documents"); missing.setObjectName("secondary"); missing.clicked.connect(self.missing); e.addWidget(missing)
  copy=QPushButton("Copy tender plan"); copy.clicked.connect(self.copy_plan); e.addWidget(copy)
  safety=QLabel("No CAPTCHA bypass or automatic bid submission. Verify eligibility, EMD, deadlines and attachments."); safety.setWordWrap(True); safety.setStyleSheet("background:#fff7ed;color:#9a3412;border:1px solid #fed7aa;border-radius:8px;padding:8px"); e.addWidget(safety); c.addWidget(act); c.addStretch(); return w
 def key_status(self):
  try:
   g=bool(keyring.get_password(KEYRING_SERVICE,"GEMINI_API_KEY")); r=bool(keyring.get_password(KEYRING_SERVICE,"GROQ_API_KEY"))
   return "Saved locally: Gemini "+("✓" if g else "—")+" · Groq "+("✓" if r else "—")
  except Exception: return "OS credential store unavailable. Check keyring support on this computer."
 def save_keys(self):
  try:
   for field,name in ((self.gemini_key,"GEMINI_API_KEY"),(self.groq_key,"GROQ_API_KEY")):
    value=field.text().strip()
    if value: keyring.set_password(KEYRING_SERVICE,name,value)
   self.gemini_key.clear(); self.groq_key.clear(); self.key_status_label.setText(self.key_status())
   self.status.setText("API keys saved to the OS credential store. Restarting is not required.")
   QMessageBox.information(self,"Saved","Your API keys are stored in the operating system credential store. Empty fields leave previously saved keys unchanged.")
  except Exception as exc:
   QMessageBox.critical(self,"Could not save keys",f"Credential storage failed: {exc}\nPlease update keyring / OS permissions. Keys were not saved by this app.")
 def fill_login(self):
  user,pwd,cap=self.uid.text(),self.pwd.text(),self.cap.text()
  if not user or not pwd or not cap:
   QMessageBox.warning(self,"Missing details","Enter your user ID, password and the CAPTCHA you read in the browser."); return
  js=f"""(()=>{{const v={{u:{json.dumps(user)},p:{json.dumps(pwd)},c:{json.dumps(cap)}}};const a=[...document.querySelectorAll('input:not([type=hidden])')];const score=(e,ws)=>ws.reduce((n,w)=>n+(([e.id,e.name,e.placeholder,e.getAttribute('aria-label'),e.autocomplete].join(' ').toLowerCase().includes(w))?1:0),0);const pick=ws=>a.map(e=>({{e,s:score(e,ws)}})).filter(x=>x.s).sort((x,y)=>y.s-x.s)[0]?.e;const pw=a.find(e=>e.type==='password')||pick(['password','passwd']);const uid=pick(['username','user id','userid','email','mobile','login']);const cap=pick(['captcha','capcha','verification code','security code']);const set=(e,x)=>{{if(!e)return false;const d=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value');d.set.call(e,x);e.dispatchEvent(new Event('input',{{bubbles:true}}));e.dispatchEvent(new Event('change',{{bubbles:true}}));return true}};return {{user:set(uid,v.u),password:set(pw,v.p),captcha:set(cap,v.c)}}}})()"""
  self.browser.page().runJavaScript(js,self.filled)
 def filled(self,res):
  self.uid.clear(); self.pwd.clear(); self.cap.clear()
  self.status.setText("Login fill attempted. Inspect the browser and click Login yourself. "+str(res))
 def prepare(self):
  values=[f"Location: {self.loc.text().strip() or 'Any'}",f"Department: {self.dept.text().strip() or 'Any'}",f"Category: {self.cat.currentText()}",f"EMD: {self.emd.currentText()}",f"Keywords: {self.kw.text().strip() or 'None'}"]
  self.preview.setText("\n".join(values)+"\n\nApply these criteria in GeM and confirm the bid document.")
  self.status.setText("Search terms prepared; verify the live tender requirements.")
 def missing(self):
  m=[x.text() for x in self.checks if not x.isChecked()]
  QMessageBox.information(self,"Document checklist","Not marked ready:\n\n"+("\n".join("• "+x for x in m) if m else "All items marked ready. Confirm bid-specific requirements."))
 def copy_plan(self):
  ready=[x.text() for x in self.checks if x.isChecked()]; missing=[x.text() for x in self.checks if not x.isChecked()]
  plan="GeM Tender Preparation Plan\n"+f"Location: {self.loc.text() or 'Any'}\nDepartment: {self.dept.text() or 'Any'}\nCategory: {self.cat.currentText()}\nEMD: {self.emd.currentText()}\nKeywords: {self.kw.text() or 'None'}\n\nReady:\n"+"\n".join("- "+x for x in ready)+"\n\nNot marked ready:\n"+"\n".join("- "+x for x in missing)
  QApplication.clipboard().setText(plan); self.status.setText("Tender plan copied. Credentials and API keys are excluded.")
def main():
 app=QApplication(sys.argv); app.setStyle("Fusion"); app.setStyleSheet(STYLE); w=Window(); w.show(); sys.exit(app.exec())
if __name__=="__main__": main()
