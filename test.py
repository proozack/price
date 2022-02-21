from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List


class Context():
    def __init__(self, strategy: Strategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> Strategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        self._strategy = strategy

    def do_some_business_logic(self, data: List) -> None:
        result = self._strategy.do_algorithm(data)
        print(",".join(result))


class Strategy(ABC):
    @abstractmethod
    def do_algorithm(self, data: List):
        pass


class ConcreteStrategyA(Strategy):
    def do_algorithm(self, data: List) -> List:
        return sorted(data)


class ConcreteStrategyB(Strategy):
    def do_algorithm(self, data: List) -> List:
        return reversed(sorted(data))


a = {
    'ConcreteStrategyA': ConcreteStrategyA,
    'ConcreteStrategyB': ConcreteStrategyB,
}


class AbstractFactory(ABC):
    @abstractmethod
    def do_algorithm(self) -> List:
        pass


class AfConcreteStrategyA(AbstractFactory):

    def do_algorithm(self, data: List) -> List:
        return sorted(data)


class AfConcreteStrategyB(AbstractFactory):

    def do_algorithm(self, data: List) -> List:
        return reversed(sorted(data))


def client_code(factory: AbstractFactory, example_data: List) -> None:
    f = factory()
    return f.do_algorithm(example_data)


if __name__ == "__main__":
    example_data = ["a", "b", "c", "d", "e"]
    context = Context(ConcreteStrategyA())

    print("ConcreteStrategyA strategy chosen")
    context.do_some_business_logic(example_data)

    print("ConcreteStrategyB strategy chosen")
    context.strategy = ConcreteStrategyB()
    context.do_some_business_logic(example_data)

    print("Selected ConcreteStrategyB strategy - different loading")
    r = a.get('ConcreteStrategyB')()
    print(",".join(r.do_algorithm(example_data)))

    print("Selected AfConcreteStrategyA strategy - Abstract factory ")
    print(",".join(client_code(AfConcreteStrategyA, example_data)))
