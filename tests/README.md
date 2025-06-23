# README.md

"""
Deze map bevat alle tests voor het framework, gestructureerd naar type:
- unit/: Unit tests
- integration/: Integratietests
- performance/: Performance- en loadtests
- async/: Asynchrone tests
- data_driven/: Data-driven tests
- advanced/: Geavanceerde patronen en scenario's
- data/: Testdata (JSON)
"""

# Teststructuur

Deze map bevat alle tests voor het project, logisch gescheiden per type.

## Subfolders

- **unit/**: Kleine, snelle unittests van losse functies/classes.
- **integration/**: Integratie- en end-to-end tests, vaak met echte afhankelijkheden of mocks.
- **performance/**: Alle performance- en loadtests, inclusief async en rate limiting.
- **async/**: Async/mocking/timeout tests, inclusief respx en semaphores.
- **data_driven/**: Data-gedreven en parametrische tests, vaak met veel scenario's.
- **advanced/**: Geavanceerde patronen, custom ID's, complexe parametrisatie.

## Algemene bestanden
- `conftest.py`, `conftest_async.py`: Fixtures en testconfiguratie
- `helper_functions.py`: Herbruikbare testhelpers

## Voorbeelden: Alleen een bepaalde testgroep draaien

Alleen unittests:
```
pytest tests/unit
```

Alleen integratietests:
```
pytest tests/integration
```

Alleen performance tests:
```
pytest tests/performance
```

Alle async/mocking tests:
```
pytest tests/async
```

Alle data-driven tests:
```
pytest tests/data_driven
```

Alle advanced tests:
```
pytest tests/advanced
```

## Best practice
- Houd nieuwe tests bij in de juiste subfolder.
- Gebruik duidelijke namen en docstrings.
- Gebruik parametrisatie en fixtures voor herbruikbaarheid. 