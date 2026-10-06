import ast
import operator
from datetime import datetime

from ollama import ChatResponse, chat


class MaxStepsExceeded(RuntimeError):
    """Raised when the agent does not produce a final answer in time."""

    def __init__(self, max_steps: int, tokens_used: int):
        self.max_steps = max_steps
        self.tokens_used = tokens_used
        super().__init__(
            f"Agent reached max_steps={max_steps} without producing a final answer."
        )


def get_time():
    """Returns the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluate_arithmetic(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_arithmetic(node.left)
        right = _evaluate_arithmetic(node.right)
        return _BINARY_OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        operand = _evaluate_arithmetic(node.operand)
        return _UNARY_OPERATORS[type(node.op)](operand)

    raise ValueError("Expression contains unsupported syntax")


def calculator(expression: str) -> int | float:
    """Safely calculates an arithmetic expression."""
    try:
        parsed_expression = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise ValueError("Invalid arithmetic expression") from error

    return _evaluate_arithmetic(parsed_expression.body)


def try_again():
    """Asks the agent to try again instead of providing a final answer."""
    return "try again"


calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Calculates the result of a mathematical expression.",
        "parameters": {
            "type": "object",
            "required": ["expression"],
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate.",
                },
            },
        },
    },
}


def llm_call(messages: list) -> ChatResponse:
    """Calls the LLM with the given prompt and returns the response."""
    llm: ChatResponse = chat(
        model="gemma4:31b-cloud",
        messages=messages,
        tools=[get_time, calculator_tool, try_again],
    )

    return llm


def run_agent(user_question: str, max_steps: int) -> tuple[str, int]:
    """Runs the agent with the given user question and maximum steps."""
    if max_steps < 1:
        raise ValueError("max_steps must be at least 1")

    available_functions = {
        "get_time": get_time,
        "calculator": calculator,
        "try_again": try_again,
    }

    messages = [{"role": "user", "content": user_question}]

    tokens_used = 0

    for step in range(1, max_steps + 1):
        print(f"Agent step {step}/{max_steps}")
        response = llm_call(messages)

        print(response)
        # Accumulate token usage from this LLM call
        if response.prompt_eval_count:
            tokens_used += response.prompt_eval_count

        if response.eval_count:
            tokens_used += response.eval_count

        print("Input Tokens used:", response.prompt_eval_count)
        print("Output Tokens used:", response.eval_count)

        if not response.message.tool_calls:
            return response.message.content, tokens_used

        messages.append(response.message)

        for tool in response.message.tool_calls:
            # Ensure the function is available, and then call it
            if function_to_call := available_functions.get(tool.function.name):
                print("Calling function:", tool.function.name)
                print("Arguments:", tool.function.arguments)
                try:
                    output = function_to_call(**tool.function.arguments)
                    print("Function output:", output)
                except Exception as error:
                    output = (
                        f"Tool '{tool.function.name}' failed with "
                        f"{type(error).__name__}: {error}. "
                        "Correct the input and try again."
                    )
                    print(output)
                
            else:
                print("Function", tool.function.name, "not found")
                output = "Function not found"

            # Add each tool result as a separate message
            messages.append(
                {
                    "role": "tool",
                    "content": str(output),
                    "tool_name": tool.function.name,
                }
            )

    # A limit is a failed run, not a successful answer.
    raise MaxStepsExceeded(max_steps=max_steps, tokens_used=tokens_used)


if __name__ == "__main__":
    try:
        answer, total_tokens = run_agent(
            "Use the calculator tool to evaluate 1/0. You must call the tool.",
            max_steps=5,
        )
    except MaxStepsExceeded as error:
        print("Agent stopped:", error)
        print("Total tokens used:", error.tokens_used)
    else:
        print("Final answer:", answer)
        print("Total tokens used:", total_tokens)
