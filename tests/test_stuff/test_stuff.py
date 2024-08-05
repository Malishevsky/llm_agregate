#####################################################################################################

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

#####################################################################################################

@pytest.mark.benchmark()
def test_benchmark(benchmark: BenchmarkFixture) -> None:
    runs = []
    benchmark.pedantic(runs.append, args=[123])
    assert runs == [123]

#####################################################################################################
