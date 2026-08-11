*This project has been created as part of the 42 curriculum by rrasmuss.*

# Call Me Maybe

## Description

Call Me Maybe is a Python project that implements constrained function calling with a local language model.

The program is designed to read structured function definitions and a natural-language prompt, validate the input, and later constrain model generation so that the output matches the available function schemas.

The current implementation includes strict Pydantic models for supported JSON schema types, recursive arrays and objects, function definitions, prompt input validation, and JSON loading with malformed-input and duplicate-key rejection.

## Instructions

Install the project dependencies with:

```bash
uv sync
```

Run the project with:

```bash
uv run python -m src
```

Run the test suite with:

```bash
uv run python -m pytest
```

Run style checks with:

```bash
uv run flake8 src tests
```

Run static type checking on the source code with:

```bash
uv run mypy src
```

## Algorithm

To be completed as the constrained decoding implementation is developed.

## Design decisions

The project uses strict Pydantic models to validate structured input before it reaches the generation layer.

Supported schema types are modeled separately for strings, numbers, booleans, null values, arrays, and objects. Arrays and objects support recursive nesting.

Function parameters are represented as object schemas because function arguments are named fields.

JSON loading is kept separate from schema validation. Raw JSON is parsed first, then converted into validated Pydantic models.

Duplicate JSON keys are rejected instead of silently allowing later values to overwrite earlier ones.

## Performance analysis

To be completed once tokenizer, model, caching, batching, and constrained decoding behavior are implemented.

## Challenges faced

To be expanded as implementation progresses.

Current challenges include designing recursive schema validation while keeping the model structure strict and readable, and separating JSON parsing errors from schema validation errors.

## Testing strategy

The project uses pytest for automated tests.

Tests currently cover:

- primitive schema validation
- recursive array and object schemas
- valid and invalid function definitions
- prompt input validation
- valid JSON loading
- malformed JSON rejection
- duplicate JSON key rejection
- conversion of loaded JSON into validated Pydantic models

Code style is checked with flake8.

Static type checking is run with mypy on the source code.

## Example usage

To be completed once the command-line interface and generation pipeline are implemented.

## Resources

To be expanded as additional libraries and references are used during development.

### AI usage

AI was used as a tutoring and development-support tool to explain Python concepts, discuss architecture and design decisions, review code written during development, and help reason about tests and validation behavior.

The implementation is written and tested incrementally, with the goal of understanding the code and design decisions rather than copying a complete generated solution.