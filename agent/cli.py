import argparse,json,sys
from .core import Controller,Store,Blocked
from .model import LivePlanner
from .ports import BusinessPorts
def main():
 p=argparse.ArgumentParser()
 p.add_argument("command",choices=["tick","status"]);p.add_argument("--state",default="runtime/public/state.json");p.add_argument("--max-steps",type=int,default=1)
 a=p.parse_args();store=Store(a.state)
 if a.command=="status":
  print(json.dumps({"stage":store.state["stage"],"events":len(store.state["events"]),"offers":list(store.state["offers"]),"pending":store.state["pending"],"revenue":store.state["revenue"]},ensure_ascii=False));return 0
 agent=Controller(store,LivePlanner(),BusinessPorts())
 for i in range(min(max(a.max_steps,1),5)):
  try:print(json.dumps(agent.tick(),ensure_ascii=False))
  except Blocked as e:print(json.dumps({"status":"BLOCKED","reason":str(e),"stage":store.state["stage"]}));return 3
 return 0
if __name__=="__main__":sys.exit(main())
