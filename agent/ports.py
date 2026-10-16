import os,re,json,urllib.parse,urllib.request,urllib.error,datetime,hashlib,shutil,subprocess,sys,zipfile,io
from pathlib import Path
from .core import digest

def get_json(url,token=None):
 h={"Accept":"application/vnd.github+json","User-Agent":"BusinessAgent/0.1","X-GitHub-Api-Version":"2022-11-28"}
 if token:h["Authorization"]="Bearer "+token
 req=urllib.request.Request(url,headers=h)
 try:
  with urllib.request.urlopen(req,timeout=16) as r:return json.loads(r.read(250000))
 except urllib.error.HTTPError as e:raise ValueError("github_http_"+str(e.code)) from None

class BusinessPorts:
 def __init__(self,owner_repo="tibame201020/business-agent-system",token=None,transport=None):
  self.repo=owner_repo;self.token=token or os.getenv("GITHUB_TOKEN");self.fetch=transport or get_json
 def gh(self,path):return self.fetch("https://api.github.com/"+path.lstrip("/"),self.token)
 def discover(self,s,query):
  if not isinstance(query,str) or not re.fullmatch(r"[\w\u4e00-\u9fff +.:-]{3,90}",query):raise ValueError("invalid bounded public query")
  q=query+" in:title comments:>=2 is:issue is:open archived:false"
  data=self.gh("search/issues?"+urllib.parse.urlencode({"q":q,"per_page":8,"sort":"comments","order":"desc"}));items=[]
  for x in data.get("items",[]):
   u=x.get("html_url","")
   if "pull_request" in x or not u.startswith("https://github.com/"):continue
   parts=u.split("/")
   if len(parts)<7:continue
   ref="issue:"+digest({"url":u})
   record={"ref":ref,"url":u,"api_url":x["url"],"title":x.get("title","")[:180],"excerpt":(x.get("body") or "")[:450],"comments":x.get("comments",0),"repo":parts[3]+"/"+parts[4],"source":"PUBLIC_ISSUE_NOT_PURCHASE_EVIDENCE"}
   s["discovered"][ref]=record;items.append({k:v for k,v in record.items() if k!="api_url"})
  return {"stage":"discovered","receipt":"search:"+digest({"query":q,"items":items}),"observation":{"query":q,"results":items,"total":data.get("total_count",0)}}
 def inspect(self,s,ref):
  if ref not in s["discovered"]:raise ValueError("ref was not discovered")
  rec=s["discovered"][ref];api=rec["api_url"]
  if not re.fullmatch(r"https://api.github.com/repos/[^/]+/[^/]+/issues/\d+",api):raise ValueError("invalid API URL")
  issue=self.fetch(api,self.token)
  if issue.get("html_url")!=rec["url"]:raise ValueError("source identity mismatch")
  body=(issue.get("body") or "")[:1400]
  if len(body.strip())<30:raise ValueError("insufficient first-party problem statement")
  evidence={"ref":ref,"url":rec["url"],"title":issue.get("title","")[:180],"problem_statement":body,"repo":rec["repo"],"comments_count":issue.get("comments",0),"type":"PUBLIC_REQUEST_NOT_VERIFIED_PAYMENT"}
  s["inspected"][ref]=evidence
  return {"stage":"inspected","receipt":"inspect:"+digest(evidence),"observation":evidence}
 def propose(self,s,title,buyer,pain,deliverable,price_twd,source_refs,validation_metric):
  if not isinstance(source_refs,list) or len(set(source_refs))<2 or any(x not in s["inspected"] for x in source_refs):raise ValueError("two inspected refs required")
  if len({s["inspected"][x]["repo"] for x in source_refs})<2:raise ValueError("two independent repositories required")
  for k,v in {"title":title,"buyer":buyer,"pain":pain,"deliverable":deliverable,"validation_metric":validation_metric}.items():
   if not isinstance(v,str) or not 12<=len(v.strip())<=400:raise ValueError(k+" must be specific")
  if type(price_twd) is not int or not 30<=price_twd<=20000:raise ValueError("bounded hypothetical price required")
  offer={"title":title,"buyer":buyer,"pain":pain,"deliverable":deliverable,"price_twd_hypothesis":price_twd,"source_refs":source_refs,"source_urls":[s["inspected"][x]["url"] for x in source_refs],"validation_metric":validation_metric,"verified_revenue_twd":None,"status":"draft"}
  oid="offer-"+digest(offer);offer["id"]=oid;s["offers"][oid]=offer;s["current_offer"]=oid
  return {"stage":"proposed","receipt":oid,"observation":offer}
 def evaluate(self,s,offer_id):
  offer=s["offers"].get(offer_id)
  if not offer or s["current_offer"]!=offer_id:raise ValueError("unknown offer")
  sources=[s["inspected"][x] for x in offer["source_refs"]]
  reasons=[]
  if len({x["repo"] for x in sources})<2:reasons.append("sources not independent")
  if not any(x["comments_count"] or len(x["problem_statement"])>120 for x in sources):reasons.append("weak demand context")
  offer["status"]="experiment_ready" if not reasons else "rejected"
  review={"status":offer["status"],"reasons":reasons,"claim":"WILLINGNESS_TO_PAY_UNVERIFIED","sources":offer["source_urls"]}
  offer["review"]=review
  return {"stage":"evaluated" if not reasons else "rejected","receipt":"review:"+digest(review),"observation":review}
 def queue_build(self,s,offer_id):
  o=s["offers"].get(offer_id)
  if not o or s["current_offer"]!=offer_id or o["status"]!="experiment_ready":raise ValueError("experiment not approved")
  if not self.token:raise ValueError("Actions issue permission unavailable")
  marker="BUSINESS_AGENT_OFFER:"+offer_id
  listing=self.gh("repos/"+self.repo+"/issues?state=all&per_page=100")
  found=next((x for x in listing if marker in (x.get("body") or "")),None)
  if not found:
   body=("<!-- "+marker+" -->\n## Evidence-backed build experiment\n\n**Buyer:** "+o["buyer"]+"\n\n**Pain:** "+o["pain"]+"\n\n**Deliverable:** "+o["deliverable"]+"\n\n**Price hypothesis (NOT revenue):** TWD "+str(o["price_twd_hypothesis"])+"\n\n**Success metric:** "+o["validation_metric"]+"\n\n**Sources:**\n"+"\n".join("- "+u for u in o["source_urls"])+"\n\nGate: build MVP, verify, distribute; do not invent orders.\n")
   data=json.dumps({"title":"[Agent experiment] "+o["title"][:140],"body":body}).encode()
   req=urllib.request.Request("https://api.github.com/repos/"+self.repo+"/issues",data=data,headers={"Authorization":"Bearer "+self.token,"Accept":"application/vnd.github+json","Content-Type":"application/json","User-Agent":"BusinessAgent/0.1"},method="POST")
   try:
    with urllib.request.urlopen(req,timeout=16) as r:found=json.loads(r.read(60000))
   except urllib.error.HTTPError as e:raise ValueError("issue_post_http_"+str(e.code)) from None
  o["build_issue_url"]=found["html_url"];o["status"]="queued_for_build"
  s["pending"][offer_id]={"type":"build_experiment","issue_url":found["html_url"],"MVP":"NOT_BUILT","revenue":"NOT_VERIFIED"}
  return {"stage":"queued","receipt":"build_queue:"+digest(found["html_url"]),"observation":{"offer_id":offer_id,"url":found["html_url"],"status":"QUEUED_NOT_BUILT"}}
 def build_product(self,s,offer_id,capability):
  o=s["offers"].get(offer_id)
  if not o or offer_id!=s["current_offer"] or o.get("status")!="queued_for_build":raise ValueError("only a queued, reviewed offer may build")
  if capability!="ci_flake_audit" or "CI" not in (o["title"]+o["deliverable"]):raise ValueError("no registered builder for this offer")
  root=Path(__file__).resolve().parents[1]
  source=root/"templates"/capability
  if not source.is_dir():raise ValueError("builder capability source unavailable")
  target=root/"runtime"/"public"/"products"/offer_id
  manifest={}
  for rel in ["flake_audit.py","README.md","tests/test_flake_audit.py"]:
   p=source/rel;manifest[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
  if target.exists():
   for rel,sha in manifest.items():
    if not (target/rel).exists() or hashlib.sha256((target/rel).read_bytes()).hexdigest()!=sha:raise ValueError("previous generated product drift; no destructive replacement")
  else:shutil.copytree(source,target,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
  env={k:v for k,v in os.environ.items() if not any(x in k.upper() for x in ["TOKEN","SECRET","PASSWORD","KEY"])}
  test=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],cwd=target,env=env,capture_output=True,text=True,timeout=25)
  if test.returncode:raise ValueError("builder verification failed: "+(test.stderr or test.stdout)[-500:])
  o["product"]={"capability":capability,"path":str(target.relative_to(root)).replace("\\","/"),"verified_manifest":manifest,"tests":"PASS","distribution":"NOT_PUBLISHED"}
  o["status"]="built_verified"
  s["pending"][offer_id]["MVP"]="VERIFIED_BUILT"
  return {"stage":"built","receipt":"build:"+digest(o["product"]),"observation":{"offer_id":offer_id,"path":o["product"]["path"],"tests":"PASS","source":"REGISTERED_AUDITED_BUILDER","revenue":"NOT_VERIFIED"}}
 def publish_product(self,s,offer_id):
  o=s["offers"].get(offer_id)
  if not o or offer_id!=s["current_offer"] or o.get("status")!="built_verified":raise ValueError("verified build required")
  if not self.token:raise ValueError("owner-repo release requires scoped token")
  root=Path(__file__).resolve().parents[1];folder=root/o["product"]["path"];tag="product-"+offer_id+"-v0.1"
  url="https://api.github.com/repos/"+self.repo+"/releases/tags/"+tag
  try:release=self.fetch(url,self.token)
  except ValueError as e:
   if str(e)!="github_http_404":raise
   body={"tag_name":tag,"target_commitish":"main","name":o["title"][:130]+" — public beta","body":"Evidence-backed public beta, NOT a paid or proven-income product.\\n\\nSources:\\n" + "\\n".join(o["source_urls"]) + "\\n\\nUsage in attached README. No verified purchases.", "draft":False,"prerelease":True}
   data=json.dumps(body).encode()
   req=urllib.request.Request("https://api.github.com/repos/"+self.repo+"/releases",data=data,headers={"Authorization":"Bearer "+self.token,"Accept":"application/vnd.github+json","Content-Type":"application/json","User-Agent":"BusinessAgent/0.1"},method="POST")
   try:
    with urllib.request.urlopen(req,timeout=15) as r:release=json.load(r)
   except urllib.error.HTTPError as e:raise ValueError("release_post_http_"+str(e.code)) from None
  filename=offer_id+"-ci-flake-audit.zip"
  assets=release.get("assets",[])
  asset=next((x for x in assets if x["name"]==filename),None)
  if not asset:
   buf=io.BytesIO()
   with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
    for rel in o["product"]["verified_manifest"]:
     z.write(folder/rel,"ci-flake-audit/"+rel)
   archive=buf.getvalue()
   upload_url=release["upload_url"].split("{",1)[0]+"?"+urllib.parse.urlencode({"name":filename})
   req=urllib.request.Request(upload_url,data=archive,headers={"Authorization":"Bearer "+self.token,"Accept":"application/vnd.github+json","Content-Type":"application/zip","User-Agent":"BusinessAgent/0.1"},method="POST")
   try:
    with urllib.request.urlopen(req,timeout=25) as r:asset=json.load(r)
   except urllib.error.HTTPError as e:raise ValueError("release_asset_http_"+str(e.code)) from None
  o["status"]="published_beta";o["product"]["distribution"]=release["html_url"];o["product"]["asset_url"]=asset["browser_download_url"];o["product"]["release_tag"]=tag
  s["pending"][offer_id]["MVP"]="PUBLISHED_BETA";s["pending"][offer_id]["distribution_url"]=asset["browser_download_url"]
  return {"stage":"published","receipt":"release:"+digest({"tag":tag,"asset":asset["browser_download_url"]}),"observation":{"release":release["html_url"],"asset":asset["browser_download_url"],"downloads":asset.get("download_count",0),"verified_sales":"NONE_OBSERVED"}}
 def measure_product(self,s,offer_id):
  o=s["offers"].get(offer_id)
  if not o or o.get("status")!="published_beta":raise ValueError("no published product")
  r=self.fetch("https://api.github.com/repos/"+self.repo+"/releases/tags/"+o["product"]["release_tag"],self.token)
  asset=next((x for x in r.get("assets",[]) if x.get("browser_download_url")==o["product"]["asset_url"]),None)
  if not asset:raise ValueError("published asset absent")
  measure={"download_count":asset.get("download_count",0),"observed_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"purchase_count":None,"gross_revenue_twd":None,"classification":"PLATFORM_DOWNLOAD_METRIC_NOT_PAYMENT_EVIDENCE"}
  o["product"]["latest_measure"]=measure
  return {"stage":"measured","receipt":"distribution_measure:"+digest(measure),"observation":measure}
 def audit_asset(self,s,url):
  if not isinstance(url,str) or not re.fullmatch(r"https://tibame201020.github.io/[a-zA-Z0-9/_-]+/?",url):raise ValueError("only owner's published sites")
  req=urllib.request.Request(url,headers={"User-Agent":"BusinessAgent/0.1"})
  try:
   with urllib.request.urlopen(req,timeout=12) as r:code=r.status;body=r.read(120000)
  except urllib.error.HTTPError as e:code=e.code;body=b""
  record={"url":url,"status":code,"bytes":len(body),"scope":"AVAILABILITY_NOT_REVENUE","checked_at":datetime.datetime.now(datetime.timezone.utc).isoformat()}
  return {"stage":"audited","receipt":"audit:"+digest(record),"observation":record}
