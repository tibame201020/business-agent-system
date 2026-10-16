import json,tempfile,unittest
from pathlib import Path
from agent.core import Controller,Store,Blocked,digest
from agent.ports import BusinessPorts
from agent.model import FixturePlanner

URL_A="https://github.com/acme-one/alpha/issues/42"
URL_B="https://github.com/acme-two/beta/issues/24"
API_A="https://api.github.com/repos/acme-one/alpha/issues/42"
API_B="https://api.github.com/repos/acme-two/beta/issues/24"
BODY="We manually reconcile a recurring CSV export across many accounts. The repeated steps cause wrong totals and consume hours weekly. Need an auditable batch operation."
def issue(url,api):return {"html_url":url,"url":api,"title":"Need repeatable batch validation for CSV exports","body":BODY,"comments":3,"created_at":"2026-10-01"}
def transport(url,token):
 if "/search/issues?" in url:return {"total_count":2,"items":[issue(URL_A,API_A),issue(URL_B,API_B)]}
 if url==API_A:return issue(URL_A,API_A)
 if url==API_B:return issue(URL_B,API_B)
 if "?state=all" in url:return []
 raise AssertionError("unapproved transport: "+url)
def choice(tool,**args):return {"tool":tool,"args":args,"reason":"Specific action justified by public primary-source demand."}
class BusinessTest(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.store=Store(Path(self.tmp.name)/"state.json");self.ports=BusinessPorts(token="fixture",transport=transport)
 def tearDown(self):self.tmp.cleanup()
 def test_real_tool_loop_with_model_choices_and_restart(self):
  decisions=[choice("discover",query="CSV workflow"),choice("inspect",ref="issue:"+digest({"url":URL_A})),choice("inspect",ref="issue:"+digest({"url":URL_B}))]
  c=Controller(self.store,FixturePlanner(decisions),self.ports)
  for d in decisions:c.tick()
  self.assertEqual(len(self.store.state["inspected"]),2)
  self.assertEqual(Store(self.store.path).state["stage"],"inspected")
  def decide(ctx):
   stage=ctx["stage"]
   if stage=="inspected":return choice("propose",title="Reliable audit for CSV batch workflows",buyer="Small online teams who routinely review exports",pain="Repeated manual exports lead to errors and long weekly reconciliation",deliverable="A verified local batch audit CLI with CSV report and comparison",price_twd=399,source_refs=list(self.store.state["inspected"]),validation_metric="Five independent trial installs and at least one verified paid order")
   if stage=="proposed":return choice("evaluate",offer_id=ctx["current_offer"]["id"])
   if stage=="evaluated":return choice("queue_build",offer_id=ctx["current_offer"]["id"])
  class Adaptive:
   def choose(self,ctx):return decide(ctx)
  c=Controller(Store(self.store.path),Adaptive(),self.ports)
  c.tick();c.tick()
  self.assertEqual(c.store.state["offers"][c.store.state["current_offer"]]["status"],"experiment_ready")
  self.assertEqual(c.store.state["revenue"]["verified_twd"],0)
  self.assertEqual(c.store.state["stage"],"evaluated")
  # Publishing is separately tested in a mocked HTTP transport; never send a live issue from tests.
 def test_unsafe_ref_fails_closed_and_persists_error(self):
  c=Controller(self.store,FixturePlanner([choice("inspect",ref="https://evil.example/")]),self.ports)
  with self.assertRaises(Blocked):c.tick()
  self.assertEqual(self.store.state["stage"],"new")
 def test_invalid_model_action_fails_closed(self):
  c=Controller(self.store,FixturePlanner([choice("queue_build",offer_id="fake")]),self.ports)
  with self.assertRaises(Blocked):c.tick()
  self.assertEqual(self.store.state["stage"],"new")
 def test_missing_model_does_not_fallback(self):
  class Fails:
   def choose(self,ctx):raise RuntimeError("missing inference")
  c=Controller(self.store,Fails(),self.ports)
  with self.assertRaises(Blocked):c.tick()
  self.assertEqual(self.store.state["events"][0]["kind"],"planner_blocked")
 def test_search_and_inspection_validate_actual_origin(self):
  s=self.store.state
  out=self.ports.discover(s,query="CSV workflow")
  self.assertEqual(out["stage"],"discovered")
  ref="issue:"+digest({"url":URL_A})
  self.assertEqual(self.ports.inspect(s,ref)["observation"]["url"],URL_A)
  with self.assertRaises(ValueError):self.ports.inspect(s,"unknown")
 def test_cannot_promote_one_source_as_two(self):
  s=self.store.state;self.ports.discover(s,query="CSV workflow");r="issue:"+digest({"url":URL_A});self.ports.inspect(s,r)
  with self.assertRaises(ValueError):self.ports.propose(s,"A reliable batch exporter","The small seller business team","Weekly CSV comparisons require too much time","Reusable batch comparison and audited output",399,[r,r],"At least one verified paid subscription")
 def test_no_unverified_revenue_claim(self):
  self.assertEqual(self.store.state["revenue"],{"verified_twd":0,"source":None})

if __name__=="__main__":unittest.main()
