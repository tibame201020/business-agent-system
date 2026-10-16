"""Replaceable model, strict JSON response; no silent heuristic pretending to be an agent."""
import json,os,re,urllib.request,urllib.error
class LivePlanner:
 def __init__(self,url=None,token=None,model=None):
  self.url=url or os.getenv("BUSINESS_MODEL_URL","https://models.github.ai/inference/chat/completions")
  self.token=token or os.getenv("BUSINESS_MODEL_TOKEN") or os.getenv("GITHUB_TOKEN")
  self.model=model or os.getenv("BUSINESS_MODEL_NAME","openai/gpt-4o-mini")
 def choose(self,context):
  if not self.token:raise RuntimeError("no model credentials; no live autonomy")
  rule=("You manage an owner's legitimate, low-overhead digital business. Choose EXACTLY one action "
        "from allowed_tools, return ONLY JSON with exactly keys tool,args,reason. No Markdown. "
        "Use evidence and source IDs from observations. Do not invent buyers, orders, sales, accounts or verified revenue. "
        "Advance the business stage; don't loop on trivial research. Don't request secrets. "
        "discover args: {query:string}, max 3 keywords with 'in:title,body is:issue is:open'; "
        "inspect args: {ref:string} from discovered issue ref; "
        "propose args: {title,buyer,pain,deliverable,price_twd,source_refs:[ref],validation_metric}, "
        "evaluate args: {offer_id:string}, queue_build args: {offer_id:string}, "
        "audit_asset args: {url:string} limited to owner's product URLs.")
  data=json.dumps({"model":self.model,"messages":[{"role":"system","content":rule},{"role":"user","content":json.dumps(context,ensure_ascii=False)}],"temperature":0.2,"max_tokens":900}).encode()
  req=urllib.request.Request(self.url,data=data,headers={"Authorization":"Bearer "+self.token,"Content-Type":"application/json","Accept":"application/json"})
  try:
   with urllib.request.urlopen(req,timeout=25) as r:raw=r.read(60000);ctype=r.headers.get("Content-Type","")
  except urllib.error.HTTPError as e:raise RuntimeError("model_http_"+str(e.code)) from None
  if "json" not in ctype:raise RuntimeError("model_non_json_response")
  answer=json.loads(raw)["choices"][0]["message"]["content"].strip()
  return json.loads(answer)

class ExternalDecisionPlanner:
 """Use the calling ChatGPT or another MCP host as the planner."""
 def __init__(self,decision):self.decision=decision
 def choose(self,context):return self.decision

class FixturePlanner:
 def __init__(self,decisions):self.decisions=iter(decisions)
 def choose(self,context):return next(self.decisions)
