"""The testbench is never part of the prompt."""

import re
from .llm_client import GenerationError, complete


SYSTEM_PROMPT = """Act as an RTL designer. Generate synthesizable SystemVerilog from the
specification. Follow the interface exactly; preserve module and port names.
Return the complete module and only SystemVerilog, with no explanation and no
Markdown code fences. Do not include testbenches, simulation-only constructs,
system tasks, file access, or additional modules."""


def make_prompt(specification: str) -> list[dict[str, str]]:
    if not specification.strip():
        raise GenerationError("Specification is empty.")
    return [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": specification}]


def clean_rtl(text: str) -> str:
    text = text.strip()
    fenced = re.fullmatch(r"```(?:systemverilog|verilog|sv)?\s*\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    # Validate the response envelope; the compiler checks the actual RTL syntax.
    stripped = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.DOTALL).strip()
    if not re.match(r"module\s+\w+", stripped) or not re.search(r"\bendmodule\s*$", stripped):
        raise GenerationError("Malformed RTL: expected one complete module without prose.")
    if "```" in text or len(re.findall(r"\bmodule\b", stripped)) != 1:
        raise GenerationError("Malformed RTL: expected exactly one module.")
    if re.search(r"\b(initial|final)\b|`include|\$(?!clog2\b|bits\b|signed\b|unsigned\b)\w+", stripped):
        raise GenerationError("RTL contains disallowed simulation constructs or file includes.")
    return text + "\n"


def generate(specification: str) -> tuple[str, dict, list]:
    messages = make_prompt(specification)
    response = complete(messages)
    return clean_rtl(response.pop("content")), response, messages
