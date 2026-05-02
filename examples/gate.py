import re
import ast
import yaml


class AbsoluteGate:
    def __init__(self, contract_path):
        with open(contract_path, 'r', encoding='utf-8') as f:
            self.contract = yaml.safe_load(f)
        self.hard_constraints = self.contract['contract'].get('hard_constraints', [])
        self.red_lines = self.contract['contract'].get('red_lines', [])

    def verify(self, code_snippet):
        """
        Verifies the code snippet against hard constraints.
        Returns: (passed: bool, reason: str)
        """
        for constraint in self.hard_constraints:
            logic = constraint.get('check_logic', '')

            if logic == 'ast_scan':
                forbidden_calls = constraint.get('forbidden_calls', [])
                try:
                    tree = ast.parse(code_snippet)
                except SyntaxError:
                    return False, "SyntaxError: Code is not valid Python."
                if self._check_forbidden_calls(tree, forbidden_calls):
                    return False, f"Hard Constraint Violation: [{constraint['constraint']}]"

            elif logic == 'regex_scan':
                pattern = constraint.get('pattern', '')
                if re.search(pattern, code_snippet):
                    return False, f"Hard Constraint Violation: [{constraint['constraint']}]"

        return True, "PASS"

    def _check_forbidden_calls(self, tree, forbidden_list):
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check obj.method() form
                if isinstance(node.func, ast.Attribute):
                    if hasattr(node.func.value, 'id'):
                        name = f"{node.func.value.id}.{node.func.attr}"
                        if name in forbidden_list:
                            return True
                # Check function() form
                elif isinstance(node.func, ast.Name):
                    if node.func.id in forbidden_list:
                        return True
        return False
