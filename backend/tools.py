import ast
import os
import operator

# ---------------------------------------------------------------------------
# Tool definitions — these are sent to Claude so it knows what tools exist
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate a safe mathematical expression. Use this for any maths.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A mathematical expression e.g. '2 * (3 + 4)'"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file the user has uploaded.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the file to read e.g. 'notes.txt'"
                }
            },
            "required": ["filename"]
        }
    }
]

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

# Safe calculator — uses AST instead of eval() to prevent code injection
def run_calculator(expression: str) -> str:
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def eval_node(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return SAFE_OPERATORS[type(node.op)](
                eval_node(node.left), eval_node(node.right)
            )
        elif isinstance(node, ast.UnaryOp):
            return SAFE_OPERATORS[type(node.op)](eval_node(node.operand))
        else:
            raise ValueError(f"Unsupported operation: {type(node)}")

    try:
        tree = ast.parse(expression, mode='eval')
        result = eval_node(tree.body)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


def run_read_file(filename: str) -> str:
    # Sanitise filename to prevent directory traversal attacks
    filename = os.path.basename(filename)
    filepath = os.path.join("uploads", filename)

    if not os.path.exists(filepath):
        return f"File '{filename}' not found in uploads folder."

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


# ---------------------------------------------------------------------------
# Router — maps tool name to its function
# ---------------------------------------------------------------------------

def execute_tool(name: str, inputs: dict) -> str:
    if name == "calculator":
        return run_calculator(inputs["expression"])
    elif name == "read_file":
        return run_read_file(inputs["filename"])
    else:
        return f"Unknown tool: {name}"