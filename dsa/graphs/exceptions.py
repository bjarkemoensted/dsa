class GraphError(Exception):
    pass


class NoPathError(GraphError):
    pass


class CycleError(GraphError):
    pass
