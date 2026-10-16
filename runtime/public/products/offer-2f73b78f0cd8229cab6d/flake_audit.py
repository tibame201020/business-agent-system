"""Public GitHub Actions retry-evidence exporter. Read-only; no claim that retry == proven flake."""
import argparse,csv,json,os,re,sys,urllib.parse,urllib.request,urllib.error
def api(path,token=None):
 h={"Accept":"application/vnd.github+json","User-Agent":"CI-Flake-Audit/0.1"}
 if token:h["Authorization"]="Bearer "+token
 req=urllib.request.Request("https://api.github.com/"+path,headers=h)
 with urllib.request.urlopen(req,timeout=15) as r:return json.load(r)
def analyze(runs,fetch_jobs):
 records=[]
 for run in runs:
  if run.get("conclusion")!="success" or int(run.get("run_attempt",1))<=1:continue
  n=int(run["run_attempt"]);run_id=run["id"];base=run.get("head_sha","")
  # A successful retry is correlation, not proof that the original failure was intermittent.
  previous=[]
  for attempt in range(1,min(n,6)):
   jobs=fetch_jobs(run_id,attempt)
   previous.extend(j["name"] for j in jobs if j.get("conclusion")=="failure" and isinstance(j.get("name"),str))
  if not previous:continue
  latest=fetch_jobs(run_id,n)
  latest_pass={j["name"] for j in latest if j.get("conclusion")=="success"}
  for name in sorted(set(previous)):
   records.append({"workflow":str(run.get("name",""))[:150],"run_id":run_id,"commit_sha":base,
    "attempts":n,"prior_failed_job":name,"latest_attempt_same_job_passed":name in latest_pass,
    "run_url":run.get("html_url",""),"classification":"RETRY_CORRELATED_UNVERIFIED_CAUSE"})
 return records
def gather(repo,limit=30,token=None):
 if not re.fullmatch(r"[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+",repo) or any(x in {".",".."} or x.startswith(".") for x in repo.split("/")):raise ValueError("invalid repository")
 if not 1<=limit<=100:raise ValueError("limit out of range")
 data=api("repos/"+repo+"/actions/runs?"+urllib.parse.urlencode({"per_page":limit}),token)
 def jobs(id,attempt):
  try:return api("repos/"+repo+"/actions/runs/"+str(id)+"/attempts/"+str(attempt)+"/jobs?per_page=100",token)["jobs"]
  except urllib.error.HTTPError as e:raise RuntimeError("jobs_read_http_"+str(e.code)) from None
 return analyze(data["workflow_runs"],jobs)
def main():
 p=argparse.ArgumentParser(description="Analyze previously failed GitHub Actions jobs on successful reruns.")
 p.add_argument("--repo",required=True);p.add_argument("--limit",type=int,default=30);p.add_argument("--output",default="flake-audit.csv");a=p.parse_args()
 rows=gather(a.repo,a.limit,os.getenv("GITHUB_TOKEN"))
 fields=["workflow","run_id","commit_sha","attempts","prior_failed_job","latest_attempt_same_job_passed","run_url","classification"]
 with open(a.output,"w",encoding="utf-8-sig",newline="") as f:
  writer=csv.DictWriter(f,fields);writer.writeheader();writer.writerows(rows)
 print(json.dumps({"status":"OK","repository":a.repo,"findings":len(rows),"output":a.output,"claim":"retry evidence, not proof of causal flakiness"}))
if __name__=="__main__":main()
