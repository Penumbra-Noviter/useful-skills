# Python Friction Signals

Use these signals during the Explore phase to identify shallow modules. Apply **every signal** to the code under review — each one is a distinct failure mode. Missed signals are candidates you never find.

---

## 1. Pass-through `__init__.py`

A package whose `__init__.py` re-exports symbols from submodules without adding abstraction or orchestration. The package surface is a hallway, not a room.

```python
# shallow: reporting/__init__.py
from .parser import parse
from .formatter import format
from .sender import send
```

**Deepening:** consolidate orchestration logic into the package's own module. The `__init__.py` exports one high-level operation instead of three pass-throughs.

---

## 2. Single-implementation Protocol

A `typing.Protocol` or `abc.ABC` with exactly one concrete subclass. The abstract contract adds ceremony without leverage — no second adapter justifies the seam.

**Deepening:** inline the protocol's contract into its sole consumer. Keep only when a second adapter is imminent and the interface is already stabilised.

---

## 3. Fat Delegator

A class whose `__init__` accepts many dependencies and every method delegates to one of them with minimal transformation. The class is a concierge, not a doer.

```python
class ReportGenerator:
    def __init__(self, fetcher, parser, formatter, sender, logger):
        self._fetcher = fetcher
        self._parser = parser
        self._formatter = formatter
        # ...

    def generate(self, query):
        data = self._fetcher.fetch(query)
        parsed = self._parser.parse(data)
        return self._formatter.format(parsed)
```

**Deepening:** replace with plain functions that import dependencies directly, or extract the orchestration into a function and keep the class only if state needs to persist between calls.

---

## 4. Wrapper Cascade

Three or more functions where each calls the next with trivial argument transformation. The intermediates are sediment.

```python
def load_data(path):       return _read_raw(path)
def _read_raw(path):       return _parse_csv(path)
def _parse_csv(path):      return pd.read_csv(path)
```

**Deepening:** collapse into one public function; inline private helpers that add no transformation logic.

---

## 5. Undefined Surface

A module without `__all__`, or with `__all__` that exports symbols only used internally. Every undocumented export is a commitment the author didn't mean to make.

**Deepening:** define `__all__` explicitly; prune to what consumers actually import. Run `grep -r 'from .* import'` across the codebase to discover real usage.

---

## 6. Orphan Mixin

A mixin class that defines no methods, or only data attributes and dunder-config. A mixin should mix in **behaviour**, not serve as a namespace for constants.

```python
class LogMixin:
    logger = logging.getLogger(__name__)
    log_format = "%(asctime)s %(message)s"
```

**Deepening:** inline the data into consuming classes; replace module-level constants with a `dataclass` if grouping is needed.

---

## 7. Callback Class

A class whose sole purpose is to be passed as a callback or strategy, where a plain function or `functools.partial` would serve. The class adds protocol ceremony without leverage.

```python
# shallow
class ErrorPrinter:
    def handle(self, err): print(f"Error: {err}")

# deep enough
def handle_error(err): print(f"Error: {err}")
```

**Deepening:** replace with a plain function. Reach for `typing.Protocol` only when the strategy set is polymorphic and growing.
