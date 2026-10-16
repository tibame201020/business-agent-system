"""Durable agent loop: the model chooses tools; contracts enforce transitions and receipts.
No model response can skip source verification or cause an arbitrary network action.
"""
import hashlib,json,os,tempfile,datetime
from pathlib import Path

STAGES={
 "new":{"discover"},"discovered":{"inspect","discover"},
 "inspected":{"propose","inspect","discover"},
 "proposed":{"evaluate"},"evaluated":{"queue_build","discover"},
 "queued":{"audit_asset","discover"},"audited":{"discover","audit_asset"},
 "rejected":{"discover"}
}
class Blocked(Exception): pass

def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:20]
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def fresh():return {"schema":"business-agent.v1","goal":"Find, validate, build and operate small, self-service digital businesses; maximize verified net profit, not output count.","stage":"new","events":[],"discovered":{},"inspected":{},"offers":{},"pending":{},"current_offer":None,"last_result":None,"revenue":{"verified_twd":0,"source":None},"costs":{"verified_twd":0,"source":None}}

class Store:
 def __init__(self,path):self.path=Path(path);self.state=json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else fresh()
 def append(self,kind,payload,operation_key):
  s=self.state
  for event in s["events"]:
   if event["key"]==operation_key:return False
  event={"seq":len(s["events"])+1,"at":utc(),"kind":kind,"key":operation_key,"receipt":digest(payload),"summary":payload}
  s["events"].append(event)
  self.save();return True
 def save(self):
  self.path.parent.mkdir(parents=True,exist_ok=True)
  fd,name=tempfile.mkstemp(dir=str(self.path.parent),prefix=".state-",suffix=".tmp")
  try:
   with os.fdopen(fd,"w",encoding="utf-8") as f:json.dump(self.state,f,ensure_ascii=False,indent=2,sort_keys=True);f.flush();os.fsync(f.fileno())
   os.replace(name,self.path)
  finally:
   if os.path.exists(name):os.unlink(name)

class Controller:
 def __init__(self,store,planner,ports):self.store=store;self.planner=planner;self.ports=ports
 def tick(self):
  s=self.store.state
  stage=s["stage"];allowed=sorted(STAGES[stage]);request={"goal":s["goal"],"stage":stage,"allowed_tools":allowed,"last_result":s["last_result"],"recent_events":s["events"][-4:],"discovered":list(s["discovered"].values())[-8:],"inspected":list(s["inspected"].values())[-5:],"current_offer":s["offers"].get(s["current_offer"])}
  try:decision=self.planner.choose(request)
  except Exception as e:
   self.store.append("planner_blocked",{"reason":type(e).__name__,"detail":str(e)[:180]},"planner:"+digest({"stage":stage,"events":len(s["events"]),"reason":str(e)[:180]}));raise Blocked("planner unavailable") from e
  if set(decision)!={"tool","args","reason"} or decision["tool"] not in allowed or not isinstance(decision["args"],dict) or not isinstance(decision["reason"],str) or not decision["reason"].strip():
   raise Blocked("planner output violates tool contract")
  tool=decision["tool"];key=digest({"stage":stage,"tool":tool,"args":decision["args"],"offer":s["current_offer"]})
  if any(e["key"]==key for e in s["events"]):raise Blocked("repeat decision: choose a new action")
  if not hasattr(self.ports,tool):raise Blocked("tool unimplemented")
  try:result=getattr(self.ports,tool)(s,**decision["args"])
  except (TypeError,ValueError) as e:
   self.store.append("tool_rejected",{"tool":tool,"reason":str(e)[:170]},"reject:"+key);raise Blocked("tool contract failed") from e
  if not isinstance(result,dict) or "stage" not in result or "receipt" not in result:raise Blocked("tool missing structured receipt")
  if result["stage"] not in STAGES:raise Blocked("unknown stage")
  s["stage"]=result["stage"]
  s["last_result"]={"tool":tool,"stage":result["stage"],"receipt":result["receipt"],"observation":result.get("observation")}
  self.store.append("tool_result",{"tool":tool,"reason":decision["reason"][:260],"stage":result["stage"],"receipt":result["receipt"]},key)
  return s["last_result"]
