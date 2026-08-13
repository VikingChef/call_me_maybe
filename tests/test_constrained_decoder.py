from src.constrained_decoder import generate_constrained_json
from src.models import NumberSchema, ObjectSchema, StringSchema


class FakeTokenizer:
    def encode(self, text: str) -> list[int]:
        return []

    def decode(self, token_ids: list[int]) -> str:
        token_map = {
            0: "{",
            1: '"x"',
            2: ":",
            3: "1",
            4: "}",
        }

        return "".join(token_map[token_id] for token_id in token_ids)


class FakeModel:
    def next_token_scores(self, token_ids: list[int]) -> list[float]:
        next_token = len(token_ids)

        score_sets = [
            [10.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 10.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 10.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 10.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 10.0],
        ]

        return score_sets[next_token]


def test_generate_constrained_json_completes_object() -> None:
    model = FakeModel()
    tokenizer = FakeTokenizer()
    schema = ObjectSchema(
        type="object",
        properties={
            "x": NumberSchema(type="number"),
        },
        required=["x"],
    )

    result = generate_constrained_json(
        model,
        tokenizer,
        [],
        schema,
    )

    assert result == [0, 1, 2, 3, 4]


def test_generate_constrained_json_stops_at_token_limit() -> None:
    model = FakeModel()
    tokenizer = FakeTokenizer()
    schema = ObjectSchema(
        type="object",
        properties={
            "x": NumberSchema(type="number"),
        },
        required=["x"],
    )

    try:
        generate_constrained_json(
            model,
            tokenizer,
            [],
            schema,
            max_new_tokens=3,
        )
    except RuntimeError as error:
        assert str(error) == "maximum token limit reached"
    else:
        assert False


def test_generate_constrained_json_avoids_wrong_schema_token() -> None:
    model = FakeModel()
    tokenizer = FakeTokenizer()
    schema = ObjectSchema(
        type="object",
        properties={
            "x": StringSchema(type="string"),
        },
        required=["x"],
    )

    result = generate_constrained_json(
        model,
        tokenizer,
        [],
        schema,
    )

    assert result == [0, 1, 2, 1, 4]
