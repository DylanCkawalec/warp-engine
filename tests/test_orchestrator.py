from typing import Dict, Any

from warpengine.orchestrator.chain import run_latex_workflow


class DummyClient:
    def __init__(self, outputs):
        self.outputs = outputs
        self.calls = []

    def complete(self, *, job_id: str, agent: str, input_text: str, context=None, mode: str = "high_reasoning") -> Dict[str, Any]:
        # Pop next output in sequence
        self.calls.append(agent)
        return {"id": job_id, "output": self.outputs[len(self.calls)-1]}


def test_chain_with_dummy_client(monkeypatch):
    # Prepare deterministic responses for plan, exec, refine
    outputs = [
        "- Plan bullets",
        "Draft output",
        "Final refined output",
    ]

    from warpengine import orchestrator

    dummy = DummyClient(outputs)

    def fake_client_init(self):
        return None

    # Monkeypatch A2AClient to use DummyClient.complete
    monkeypatch.setattr(orchestrator.chain, "A2AClient", lambda: dummy)

    job_id, final = run_latex_workflow("\\section{A} Example")
    assert isinstance(job_id, str) and job_id
    assert final == "Final refined output"

