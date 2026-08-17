class CallMeMaybeError(Exception):
    pass


class GenerationError(CallMeMaybeError):
    pass


class NoValidTokenError(GenerationError):
    pass


class TokenLimitError(GenerationError):
    pass


class SchemaMismatchError(GenerationError):
    pass


class FunctionSelectionError(CallMeMaybeError):
    pass


class InputError(CallMeMaybeError):
    pass


class InputFileError(InputError):
    pass


class InputJSONError(InputError):
    pass


class InputValidationError(InputError):
    pass
