import argparse,json,sys
from pathlib import Path
from .core import Controller,Store,Blocked
from .model import LivePlanner,ExternalDecisionPlanner
from .ports import BusinessPorts
def main():
 p=argparse.ArgumentParser()
 p.add_argument("command",choices=["tick","status"])
 p.add_argument("--state",default="runtime/public/state.json")
 p.add_argument("--max-steps",type=int,default=1)
 p.add_argument("--decision-file",default=None,help="One structured decision from the caller model (ChatGPT/MCP).")
 a=p.parse_args();store=Store(a.state)
 if a.command=="status":
  print(json.dumps({"stage":store.state["stage"],"events":len(store.state["events"]),"offers":list(store.state["offers"]),"pending":store.state["pending"],"revenue":store.state["revenue"]},ensure_ascii=False));return 0
 if a.decision_file:
  decision=json.loads(Path(a.decision_file).read_text(encoding="utf8"))
  model=ExternalDecisionPlanner(decision)
  steps=1
 else:model=LivePlanner();steps=min(max(a.max_steps,1),5)
 agent=Controller(store,model,BusinessPorts())
 for i in range(steps):
  try:print(json.dumps(agent.tick(),ensure_ascii=True))
  except Blocked as e:print(json.dumps({"status":"BLOCKED","reason":str(e),"last_event":store.state["events"][-1] if store.state["events"] else None,"stage":store.state["stage"]}));return 3
 return 0
if __name__=="__main__":sys.exit(main())
