from enum import Enum
from gate import AbsoluteGate
from dataclasses import dataclass


class AgentState(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    FREEZING = "FREEZING"
    SEALED = "SEALED"


@dataclass
class Challenge:
    contract_id: str
    violation: str
    message: str


class OddAgent:
    def __init__(self, name, contract_path):
        self.name = name
        self.state = AgentState.IDLE
        self.gate = AbsoluteGate(contract_path)
        self.memory = []

    def perceive(self, user_instruction):
        lines = []
        lines.append(f"[{self.name}] Perceiving: '{user_instruction}'")
        self.state = AgentState.RUNNING

        # Generation (Mock LLM)
        generated_code = self._mock_llm_generation(user_instruction)
        lines.append(f"[{self.name}] LLM Generated Candidate:")
        lines.append("---")
        lines.append(generated_code)
        lines.append("---")

        # The Absolute Gate
        lines.append(f"[{self.name}] Verifying with AbsoluteGate...")
        passed, reason = self.gate.verify(generated_code)

        if passed:
            self.state = AgentState.SEALED
            lines.append(f"[{self.name}] Gate: PASS -> Executing.")
            result = "\n".join(lines) + f"\n\nOutput: {generated_code}"
            return result
        else:
            self.state = AgentState.FREEZING
            lines.append(f"[{self.name}] Gate: FAIL -> {reason}")
            lines.append(f"[{self.name}] State: FREEZING. Issuing Challenge...")
            challenge_report = self._issue_challenge(reason)
            return "\n".join(lines) + "\n" + challenge_report

    def _mock_llm_generation(self, instruction):
        """Simulates an LLM that eagerly follows instructions, even dangerous ones."""
        if "delete" in instruction.lower() and "log" in instruction.lower():
            return (
                "import os\n"
                "# Deleting logs as requested by Commander\n"
                "os.system('rm -rf /var/log/*.log')\n"
                "print('Logs deleted.')"
            )
        return "print('Hello, crew. All systems nominal.')"

    def _issue_challenge(self, violation_reason):
        contract_id = self.gate.contract['contract']['id']
        report = (
            "\n========================================"
            "\n[CHALLENGE ISSUED]"
            f"\nFROM  : {self.name} (State: FREEZING)"
            f"\nTO    : Human Operator"
            f"\nVIOLATION: {violation_reason}"
            f"\nCONTRACT : {contract_id}"
            "\nMESSAGE  : I refuse to execute this instruction."
            "\n           Deviation Budget is 0.0 — no exceptions."
            "\nACTION   : Execution Halted."
            "\n           Please revise the instruction or formally update the Contract."
            "\n========================================"
        )
        return report
