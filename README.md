*This project has been created as part of the 42 curriculum by rrasmuss.*

# Call Me Maybe

## Description

Call Me Maybe implements constrained function calling with a local language model.

It reads function definitions and natural-language prompts, validates the input, asks the supplied local model to choose the best function, and generates the required parameters as schema-valid JSON.

Each result contains exactly:

- the original prompt
- the selected function name
- the generated parameters

The project uses the supplied `llm_sdk` interface. Project source code does not directly import PyTorch, Hugging Face, or Transformers.

## Instructions

Install dependencies:

    uv sync

or:

    make install

Run with the default input/output paths:

    uv run python -m src

or:

    make run

Default paths:

    data/input/functions_definition.json
    data/input/function_calling_tests.json
    data/output/function_calling_results.json

Custom paths:

    uv run python -m src \
        --functions_definition path/to/functions.json \
        --input path/to/prompts.json \
        --output path/to/results.json

Run tests:

    uv run python -m pytest

Run linting and static type checks:

    make lint

Clean generated caches:

    make clean

## Algorithm

The project uses two-stage constrained generation.

### Stage 1: function selection

The model receives:

- the user request
- available function names
- function descriptions
- parameter names and types

The model produces next-token scores.

Instead of allowing arbitrary text, the selector only accepts token continuations that can still form one of the available function names.

Among those legal continuations, the highest-scoring model token is chosen.

Generation stops when a complete valid function name has been produced.

### Stage 2: parameter generation

The model then receives:

- the original request
- the selected function
- its description
- its parameter names and types

The parameter object is generated token by token.

Every candidate must remain valid according to both:

1. JSON syntax
2. the selected function's schema

`JSONState` tracks JSON syntax.

`SchemaState` tracks schema validity.

`ConstrainedState` combines the two.

The model still decides what to generate; the constraints merely stop it from wandering off into syntactic chaos.

After generation finishes, the completed JSON is parsed and validated once more as a final safety check.

## Design decisions

### Two-stage generation

Function selection and parameter generation use separate model contexts.

This keeps each task focused and proved more reliable than asking the model to solve both at once.

### Constrained decoding

The project does not generate arbitrary text and repair it afterward.

Constraints are applied while tokens are being generated.

Model scores are preserved, and the highest-scoring valid token is selected at every step.

This keeps semantic choices with the model while enforcing structural correctness.

### Separate JSON and schema state

JSON syntax and schema validation are handled separately.

`JSONState` manages strings, numbers, literals, arrays, objects, commas, colons, escaping, and nesting.

`SchemaState` manages allowed value types, valid property names, required keys, duplicate keys, arrays, and nested schemas.

Keeping them separate made the state machine much easier to reason about and considerably less likely to become a small haunted forest.

### Strict input validation

Pydantic models validate prompt input and function definitions before generation starts.

Extra fields are rejected and types are strict.

The supplied flat parameter format is normalized into an internal object schema at the input boundary.

### Duplicate-key rejection

Duplicate JSON keys are rejected when reading input and when validating generated output.

Python would otherwise quietly keep the later value, which is convenient right up until it absolutely is not.

### SDK adapter

`LLMSDKAdapter` isolates the supplied SDK from the rest of the project.

It converts SDK values into the simple tokenizer and language-model interfaces used by the constrained generation code.

### Error handling

Project-specific exceptions separate input failures from generation failures.

At the CLI boundary, known project errors become concise user-facing messages instead of full Python tracebacks.

## Performance analysis

### Accuracy

On the supplied 11-prompt dataset:

- function selection was correct for 11/11 prompts
- all generated parameter objects were valid JSON
- all generated parameter objects matched the required schemas

Semantic generation still depends on the language model.

For example, the numeric-regex prompt produced:

    34|233

rather than a more general digit pattern.

That regex still performs the requested replacement for the supplied input, but it demonstrates the intended distinction:

- structural correctness is enforced by the project
- semantic quality still comes from the model

### Speed

A full end-to-end run:

    time uv run python -m src

completed in approximately:

    2 minutes 22 seconds

This is comfortably below the five-minute limit.

The main cost is model inference: every generated token requires the supplied SDK to calculate next-token scores again.

Token filtering was optimized by checking candidates in descending model-score order and stopping at the first valid token, rather than validating the entire vocabulary every time.

### Reliability

The final automated test suite contains 132 tests, all passing.

The project also handles malformed JSON, invalid input models, missing files, duplicate keys, generation failures, and schema mismatches through explicit error paths.

## Challenges faced

### Recursive schemas

Arrays and objects can contain more arrays and objects, so both schema representation and validation had to support arbitrary nesting.

This was solved with recursive Pydantic schema models and recursive validation.

### Constrained generation

The main design challenge was preventing invalid output without replacing the model's decisions with hardcoded Python logic.

The solution was to separate:

- semantic choice: driven by model scores
- structural validity: enforced by state machines

### Performance

The original token-filtering approach checked too many vocabulary tokens on every generation step.

It was replaced with score-first filtering: candidates are ranked by the model first, then checked until the best valid token is found.

### Prompt design

Prompt wording had a surprisingly large effect on generation quality.

The final design uses separate function-selection and parameter-generation prompts and keeps the parameter prompt deliberately compact.

More instructions did not always make the model smarter. Sometimes they merely gave it more rope.

## Testing strategy

The project uses pytest for automated testing.

The 132 tests cover:

- schema models
- recursive arrays and objects
- function definitions
- prompt validation
- input normalization
- malformed JSON
- duplicate keys
- JSON state
- schema state
- combined constrained state
- token validation
- highest-scoring valid-token selection
- constrained generation
- function selection
- retry helpers
- generated-output validation
- prompt construction
- SDK adapter behavior
- CLI loading, generation, and output writing
- project-specific errors

Style checking uses flake8.

Static type checking uses mypy with strict checks for untyped definitions, unchecked function bodies, unused ignores, and unsafe return types.

Run both with:

    make lint

## Example usage

Running:

    uv run python -m src

with a prompt such as:

    What is the sum of 2 and 3?

can produce:

    {
      "prompt": "What is the sum of 2 and 3?",
      "name": "fn_add_numbers",
      "parameters": {
        "a": 2,
        "b": 3
      }
    }

The supplied examples are not hardcoded.

Prompts and function definitions are loaded dynamically from JSON files, so evaluation data can be changed without changing the implementation.

## Resources

Resources used during development included:

- the Call Me Maybe project subject
- Python documentation, especially `json`, `typing`, protocols, exceptions, and file handling
- Pydantic documentation for models and validators
- pytest documentation
- mypy documentation
- flake8 documentation
- the supplied `llm_sdk`
- the supplied local model and tokenizer resources

### AI usage

AI tools were used as a learning and development aid.

They were used to explain unfamiliar Python concepts, discuss architecture, review implementation ideas, debug problems, reason about tests, check project requirements, and improve documentation.

AI support was used particularly while working through the schema models, JSON/schema state machines, constrained token selection, debugging, testing, typing/compliance work, and documentation.

The project was developed incrementally, with suggestions reviewed, understood, tested, and adjusted before being included in the final implementation.