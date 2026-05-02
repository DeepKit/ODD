# Pure ODD Agent (ODD-Agent)

This directory contains the Proof of Concept (PoC) implementation of a **Pure ODD Agent**.

> **Current Status**: This directory is a PoC support artifact for ODD practice exploration. It is not part of the current first-round public main package and should not be presented as a finished official agent release.

## Goal

To build a "Minimum Viable Pure Agent" that demonstrates the core ODD capability: **refusing to execute a user instruction because it violates a system contract**, even if the underlying LLM is willing to comply.

## Architecture

- **Shell**: Python-based `SevenOrderLoop`.
- **Gate**: Deterministic `AbsoluteGate` (non-LLM).
- **Contract**: `system_contract.yaml` defining Hard Constraints and Red Lines.
- **Challenge Engine**: Mechanism to issue "Refusal & Appeal" reports.

## Usage

Run the simulation scenario:

```bash
python run_scenario.py
```
