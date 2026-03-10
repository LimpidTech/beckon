class Collection:
    """Base class for arbitrary collections of items."""

    name: str | None = None

    def items(self, request):
        raise NotImplementedError
