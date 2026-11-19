"""Read back experiments, feedback, and nested traces as portable evidence."""
import json
from datetime import datetime, timezone
from src.evaluation import connect, OUT, write_json
from src.analyze_results import latest_folder


def portable_trace(run):
    return {"id":str(run.id),"name":run.name,"run_type":run.run_type,
            "parent_run_id":str(run.parent_run_id) if run.parent_run_id else None,
            "reference_example_id":str(run.reference_example_id) if run.reference_example_id else None,
            "start_time":run.start_time,"end_time":run.end_time,"error":run.error,
            "inputs":run.inputs,"outputs":run.outputs,
            "child_runs":[portable_trace(child) for child in (run.child_runs or [])]}


def verify():
    client=connect(); folder=latest_folder(); manifest=json.loads((folder/"manifest.json").read_text())
    receipt={"verified_at_utc":datetime.now(timezone.utc).isoformat(),"run_id":manifest["run_id"],"experiments":{}}
    for cfg,exp in manifest["experiments"].items():
        roots=list(client.list_runs(project_id=exp["project_id"],is_root=True))
        expected=json.loads((folder/f"results_{cfg}.json").read_text())
        expected_by_id={r["run_id"]:r for r in expected}
        if {str(r.id) for r in roots}!=set(expected_by_id):
            raise RuntimeError("Remote runs differ from saved results")
        feedback=list(client.list_feedback(run_ids=[r.id for r in roots]))
        by_run={str(r.id):{} for r in roots}
        for f in feedback:
            if f.key in ("correctness","citation_coverage","groundedness"):
                if f.key in by_run[str(f.run_id)]:
                    raise RuntimeError("Duplicate feedback key")
                by_run[str(f.run_id)][f.key]=f.score
        for rid,scores in by_run.items():
            for key in ("correctness","citation_coverage","groundedness"):
                if scores.get(key)!=expected_by_id[rid][key]:
                    raise RuntimeError("Remote feedback mismatch")
        trace_files=[]
        for case in (["S01","S04","S19"] if cfg=="baseline" else ["S03","S19"]):
            row=next(r for r in expected if r["case_id"]==case)
            trace=client.read_run(row["run_id"],load_child_runs=True)
            if not any(child.run_type=="llm" for child in trace.child_runs or []):
                raise RuntimeError("Wrapped model child trace missing")
            path=OUT/"traces"/f"{cfg}_{case}.json"
            payload=portable_trace(trace);payload["trace_url"]=client.get_run_url(run=trace)
            payload["feedback"]=by_run[str(trace.id)]
            write_json(path,payload)
            trace_files.append({"case_id":case,"file":str(path.relative_to(OUT)).replace("\\","/"),"trace_url":payload["trace_url"]})
        receipt["experiments"][cfg]={"root_runs":len(roots),"scored_runs":len(by_run),
            "feedback_count":sum(len(v) for v in by_run.values()),"all_feedback_matches":True,"traces":trace_files}
    write_json(OUT/"remote_verification.json",receipt)
    print(json.dumps(receipt,indent=2))
    return receipt

if __name__=="__main__":
    verify()
