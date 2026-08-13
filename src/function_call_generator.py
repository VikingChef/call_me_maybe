import json

from src.constrained_decoder import generate_constrained_json
from src.function_selector import choose_function_name
from src.language_model import LanguageModel
from src.models import FunctionDefinition
from src.tokenizer import Tokenizer


def generate_function_call(
    model: LanguageModel,
    tokenizer: Tokenizer,
    token_ids: list[int],
    functions: list[FunctionDefinition],
) -> tuple[str, dict]:
    function_names = [function.name for function in functions]

    selected_name = choose_function_name(
        model,
        tokenizer,
        token_ids,
        function_names,
    )

    selected_function = next(
        function
        for function in functions
        if function.name == selected_name
    )

    parameter_start = len(token_ids)

    generate_constrained_json(
        model,
        tokenizer,
        token_ids,
        selected_function.parameters,
    )

    parameter_token_ids = token_ids[parameter_start:]
    parameter_text = tokenizer.decode(parameter_token_ids)
    parameters = json.loads(parameter_text)

    return selected_name, parameters
