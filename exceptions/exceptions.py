class CheckResponseStatusException(Exception):
    def __init__(self, error):
        super().__init__(error)


class CheckKeyHomeworksException(Exception):
    def __init__(self, error):
        super().__init__(error)


class EmptyValueException(Exception):
    def __init__(self, error):
        super().__init__(error)


class StatusHWException(Exception):
    def __init__(self, error):
        super().__init__(error)