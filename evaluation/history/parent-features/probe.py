import asyncio,json,sys,importlib.util
from pathlib import Path
sys.path.insert(0,r"C:\Users\piatkowskigs\Documents\mcp-mother-child")
if importlib.util.find_spec("truststore"):
 import truststore;truststore.inject_into_ssl()
from mc import parent_resources as p
async def main():
 results={}
 for name,call in [("recalls",lambda:p.recalls("ibuprofen",lot="EXAMPLE-LOT",max_results=2)),("alerts",lambda:p.safety_alerts("cetirizine",3)),("registries",lambda:p.pregnancy_registries("sertraline",3)),("trials",lambda:p.recruiting_studies("asthma","pediatric","United States",2)),("public_input",lambda:p.input_opportunities("maternal","NIH",3)),("medication_info",lambda:p.medication_info("sertraline"))]:
  try:
   out=await call();results[name]={"ok":True,"result":out};print(name,"OK",flush=True)
  except Exception as e:results[name]={"ok":False,"error_type":type(e).__name__};print(name,type(e).__name__,flush=True)
 Path(__file__).with_name("live-source-results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
asyncio.run(main())
