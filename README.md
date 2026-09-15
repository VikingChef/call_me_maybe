**This project has been created as part of the 42 curriculum by rrasmuss.**

# Call Me Maybe

## Description

Call Me Maybe implements constrained function calling with a local language model.

It reads function definitions and natural-language prompts, validates the input, asks the supplied local model to choose the best function, and generates the required parameters as schema-valid JSON.

Each result contains exactly:

- the original prompt
- the selected function name
- the generated parameters

The project uses the supplied `llm_sdk` interface. Project source code does not directly import PyTorch, Hugging Face, or Transformers.

The main idea is simple enough to describe, although considerably less simple to actually make behave:

**let the model make the semantic decisions, but only allow it to generate structurally valid answers.**

## Instructions

Install dependencies:

```bash
uv sync
```

or:

```bash
make install
```

Run with the default input/output paths:

```bash
uv run python -m src
```

or:

```bash
make run
```

Default paths:

```text
data/input/functions_definition.json
data/input/function_calling_tests.json
data/output/function_calling_results.json
```

Custom paths:

```bash
uv run python -m src \
    --functions_definition path/to/functions.json \
    --input path/to/prompts.json \
    --output path/to/results.json
```

Run tests:

```bash
uv run python -m pytest
```

Run linting and static type checks:

```bash
make lint
```

Clean generated caches:

```bash
make clean
```

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

At each step:

1. the model scores the possible next tokens
2. candidates are considered from highest score downward
3. invalid continuations are rejected
4. the highest-scoring valid continuation is selected
5. generation continues until a complete function name is reached

This means the model still chooses the function, but it cannot suddenly decide that the best available function is `"here_is_a_small_poem"`.

### Stage 2: parameter generation

The model then receives:

- the original request
- the selected function
- its description
- its parameter names and types

The parameter object is generated token by token.

Every candidate must remain valid according to both:

1. JSON syntax
2. the selected function's parameter schema

`JSONState` tracks the current JSON syntax state.

`SchemaState` tracks what is allowed by the selected schema.

`ConstrainedState` combines the two.

The basic generation loop is:

**model scores → reject invalid tokens → choose the best valid token → update state → continue**

The model still decides what to generate. The constraints only prevent it from producing output that cannot satisfy the required structure.

After generation finishes, the completed text is parsed as JSON and checked against the required schema again as a final safety check.

### Explicit string preservation

There is one deliberately narrow post-generation rule for prompts that contain exactly one string parameter and provide its value explicitly after a colon.

For example:

```text
Format template: Say "hello" to {name}
```

In that case the explicit value after the colon is preserved exactly.

This prevents a small model from helpfully "improving" a literal string that the user actually wanted unchanged.

The rule is intentionally narrow rather than a general attempt to rewrite model output in Python.

## Design decisions

### Two-stage generation

Function selection and parameter generation use separate model contexts.

Stage 1 answers:

> Which function should be called?

Stage 2 answers:

> What arguments should that function receive?

Keeping those tasks separate proved much more reliable than asking a small model to solve both at once.

It also makes failures easier to reason about, which became increasingly valuable somewhere around the point where I had stared at token streams for long enough to develop opinions about individual braces.

### Constrained decoding

The project does not generate arbitrary text and repair it afterward.

Constraints are applied **while tokens are being generated**.

The model's scores are preserved, and the highest-scoring token that remains legal is selected at every step.

That distinction is important: the Python code enforces structure, but it does not replace the model's semantic decision-making.

### Separate JSON and schema state

JSON syntax and schema validation are handled separately.

`JSONState` manages:

- strings
- escaping
- numbers
- booleans and null
- arrays
- objects
- commas and colons
- nesting

`SchemaState` manages:

- allowed value types
- valid property names
- required keys
- duplicate keys
- array item schemas
- nested objects and arrays

`ConstrainedState` feeds generated characters through both.

Keeping the responsibilities separate made the state machine much easier to reason about and considerably less likely to become a small haunted forest.

### Strict input validation

Pydantic models validate prompt input and function definitions before generation begins.

Validation is strict, and unexpected fields are rejected.

The supplied function-definition format is converted into the internal schema models at the input boundary, so the rest of the generation pipeline can work with validated Python objects rather than repeatedly questioning whether the JSON it received is secretly plotting against it.

### Duplicate-key rejection

Duplicate JSON keys are rejected both when reading input and when validating generated output.

Python's normal JSON parser would otherwise quietly keep the later value.

That behaviour is convenient until two values are fighting over the same parameter and the parser resolves the dispute without telling anybody.

### SDK adapter

`LLMSDKAdapter` isolates the supplied `llm_sdk` from the rest of the project.

The rest of the application depends on the project's small `LanguageModel` and `Tokenizer` protocols rather than SDK-specific implementation details.

The adapter exposes the public SDK operations needed by the project:

- encoding text
- decoding token IDs
- obtaining next-token scores

This keeps the constrained-generation code independent from the concrete model wrapper.

### Error handling

Project-specific exceptions separate input failures from generation failures.

Input errors include:

- unreadable files
- malformed JSON
- invalid input structures

Generation errors include:

- no valid next token
- token-limit exhaustion
- completed output that fails schema validation
- invalid function selection

At the CLI boundary, known project errors become concise user-facing messages rather than full Python tracebacks.

## Performance analysis

### Accuracy

On the supplied 11-prompt evaluation dataset:

- function selection was correct for 11/11 prompts
- all generated parameter objects were valid JSON
- all generated parameter objects matched the required schemas
- the complete function calls were accepted for all 11 prompts

The model is still responsible for semantic generation.

For example, on one numeric-regex prompt it generated:

```text
34|233
```

rather than a more general digit pattern.

That regex still performs the requested replacement for the supplied input, but it demonstrates an important distinction:

- structural correctness is enforced by the project
- semantic quality still comes from the language model

Constrained decoding can prevent invalid JSON.

It cannot make a 0.6B model suddenly develop several billion additional parameters through force of personality.

### Speed

A full end-to-end run:

```bash
time uv run python -m src
```

completed in approximately:

```text
2 minutes 22 seconds
```

This is comfortably below the five-minute evaluation limit.

The main cost is model inference because every generated token requires another set of next-token scores.

Token filtering was therefore implemented by considering candidates in descending model-score order and stopping as soon as the highest-scoring valid token is found.

This avoids validating the entire vocabulary when the first few candidates already contain a legal continuation.

### Reliability

The automated test suite contains **141 tests**.

The suite covers both normal behaviour and failure paths, including:

- malformed JSON
- missing files
- invalid Pydantic models
- duplicate keys
- invalid JSON syntax
- schema violations
- token-generation failures
- token-limit exhaustion
- incorrect generated types
- nested objects and arrays

In addition to pytest, the project is checked with both flake8 and mypy.

## Challenges faced

### Recursive schemas

Arrays and objects can contain more arrays and objects.

That means both the schema representation and the validator need to work recursively rather than only handling the flat examples that are easiest to stare at while feeling optimistic.

The project handles nested schemas through recursive Pydantic models and recursive validation/state tracking.

### Constrained generation

The main architectural challenge was preventing invalid output without simply replacing model decisions with hardcoded Python logic.

The solution was to separate:

- **semantic choice:** driven by model scores
- **structural validity:** enforced by the constrained state machines

That lets the model remain responsible for choosing values while the decoder controls what forms those values are allowed to take.

### Literal strings

Small models sometimes transform strings that should be copied exactly.

That became especially visible with template-like prompts containing quotes, braces, or other punctuation.

A narrow preservation rule was therefore added for the specific case where a prompt clearly provides the single required string value after a colon.

The important part was keeping this rule narrow enough that it did not turn into a second, increasingly desperate function-calling system made out of string parsing.

### Performance

The original token-filtering approach checked too many vocabulary tokens during every generation step.

It was replaced with score-first filtering:

1. obtain the model scores
2. rank candidate tokens by score
3. test them in that order
4. stop at the first valid candidate

This preserves the model's preference ordering while avoiding unnecessary validation work.

### Prompt design

Prompt wording had a surprisingly large effect on generation quality.

The final design uses separate function-selection and parameter-generation prompts and keeps the parameter-generation context deliberately focused.

More instructions did not always make the model smarter.

Sometimes they merely gave it more opportunities to become creatively wrong.

## Testing strategy

The project uses pytest for automated testing.

The **141 tests** cover:

- schema models
- recursive arrays and objects
- function definitions
- prompt validation
- input normalization
- malformed JSON
- duplicate keys
- JSON syntax state
- schema state
- combined constrained state
- token validation
- highest-scoring valid-token selection
- constrained generation
- function selection
- parameter generation
- retry behaviour
- generated-output validation
- prompt construction
- SDK adapter behaviour
- CLI input loading
- complete result generation
- output writing
- project-specific errors

Style checking uses flake8.

Static type checking uses mypy, including checks for untyped definitions, unchecked function bodies, unused ignores, and unsafe return types.

Run both with:

```bash
make lint
```

They can also be run directly:

```bash
uv run flake8 src tests
uv run mypy src tests
```

## Project structure

The main responsibilities are divided between a small set of modules:

- `src/__main__.py`  
  CLI entry point and overall pipeline coordination.

- `src/models.py`  
  Strict Pydantic models for prompts, function definitions, and schemas.

- `src/input_loader.py`  
  JSON loading, duplicate-key detection, normalization, and input validation.

- `src/prompt_builder.py`  
  Builds the Stage 1 and Stage 2 model contexts.

- `src/function_selector.py`  
  Performs constrained function-name selection.

- `src/function_call_generator.py`  
  Coordinates function selection and parameter generation.

- `src/constrained_decoder.py`  
  Runs token-by-token constrained JSON generation.

- `src/json_state.py`  
  Tracks whether generated characters remain valid JSON syntax.

- `src/schema_state.py`  
  Tracks whether generated values remain valid for the required schema.

- `src/constrained_state.py`  
  Combines JSON syntax and schema constraints.

- `src/token_filter.py`  
  Selects the highest-scoring token that remains valid.

- `src/schema_validator.py`  
  Performs final recursive validation of generated Python values.

- `src/generated_output.py`  
  Parses completed generated JSON and validates it against the schema.

- `src/llm_sdk_adapter.py`  
  Adapts the supplied SDK to the project's tokenizer/model protocols.

## Example usage

Running:

```bash
uv run python -m src
```

with a prompt such as:

```text
What is the sum of 2 and 3?
```

can produce:

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {
    "a": 2,
    "b": 3
  }
}
```

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

The project was developed incrementally. Suggestions were reviewed, understood, tested, rejected when they made things worse — which happened more than once — and adjusted before being included in the final implementation.

That last part turned out to be fairly important.
