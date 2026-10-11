"""Gemini/Groq router. API keys are read from OS credential storage first, then environment."""
import os, time
from dotenv import load_dotenv
load_dotenv()
def get_saved_key(name):
 try:
  import keyring
  return (keyring.get_password("GeM Tender Assistant",name) or "").strip()
 except Exception:
  return ""
class AIRouter:
 def __init__(self):
  self.gemini_key=get_saved_key("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY","").strip()
  self.groq_key=get_saved_key("GROQ_API_KEY") or os.getenv("GROQ_API_KEY","").strip()
  self.gemini_model=os.getenv("GEMINI_MODEL","gemini-2.5-flash")
  self.groq_model=os.getenv("GROQ_MODEL","llama-3.3-70b-versatile")
  self.cooldown=int(os.getenv("PROVIDER_COOLDOWN_SECONDS","60"))
  self.blocked={}
 def configured(self): return {"Gemini":bool(self.gemini_key),"Groq":bool(self.groq_key)}
 def generate(self,prompt):
  errors=[]
  for name in ("Gemini","Groq"):
   if not self.configured()[name] or self.blocked.get(name,0)>time.time(): continue
   try:
    if name=="Gemini":
     from google import genai
     response=genai.Client(api_key=self.gemini_key).models.generate_content(model=self.gemini_model,contents=prompt)
     return response.text
    from groq import Groq
    response=Groq(api_key=self.groq_key).chat.completions.create(model=self.groq_model,messages=[{"role":"user","content":prompt}],temperature=0.2)
    return response.choices[0].message.content
   except Exception as exc:
    message=str(exc); errors.append(f"{name}: {message[:250]}")
    low=message.lower()
    self.blocked[name]=time.time()+(self.cooldown if any(k in low for k in ("429","rate limit","quota","resource_exhausted")) else 15)
  raise RuntimeError("No AI provider succeeded. "+" | ".join(errors or ["No API key configured."]))
