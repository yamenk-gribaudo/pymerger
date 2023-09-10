from collections.abc import Callable


def bisection(function: Callable[[float], float], a: float, b: float) -> float:
    start: float = a
    end: float = b
    if function(a) == 0:
        return a
    elif function(b) == 0:
        return b
    elif (
        function(a) * function(b) > 0
    ):
        raise ValueError("could not find root in given interval.")
    else:
        mid: float = start + (end - start) / 2.0
        while abs(start - mid) > 10**-7:
            if function(mid) == 0:
                return mid
            elif function(mid) * function(start) < 0:
                end = mid
            else:
                start = mid
            mid = start + (end - start) / 2.0
        return mid


def f(x: float) -> float:
    return x**3 - 2 * x - 5


if __name__ == "__main__":
    print(bisection(f, 1, 1000))

    import doctest

    doctest.testmod()
