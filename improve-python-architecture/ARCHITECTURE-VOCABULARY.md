# Python Architecture Vocabulary

The shared vocabulary for reasoning about Python module design. Adapted from `/codebase-design` principles to Python's protocol-oriented, duck-typed ecosystem. Every term below guides how you describe candidates, problems, and solutions in `improve-python-architecture`.

**Bold terms** within definitions are themselves defined here; find them by their heading.

---

## Deep / Deepen

A **deep** module has a small protocol surface relative to its implementation — the user sees a simple `from pkg import Thing` and gets rich behaviour from it. **Deepening** is the act of making a module deeper: pushing complexity behind its surface while keeping the imports simple.

Canonical Python examples: `pathlib`, `dataclasses`, `functools`. Small `__all__`, large implementation, most users never open the source.

## Shallow

A module whose protocol surface rivals its implementation in complexity — the user must understand nearly as much to use it as to write it. A pass-through `__init__.py` that only re-exports submodule symbols is the canonical Python example.

## Protocol

The public surface of a module, class, or package — what consumers import and interact with. In Python this is defined by `__all__`, `__init__.py` exports, and public (non-`_`-prefixed) names. Prefer _protocol_ over "API" or "interface"; prefer _protocol surface_ over "boundary."

## Seam

A place where behaviour can be substituted without modifying the source. In Python a seam takes the form of a `typing.Protocol`, an `abc.ABC`, a callable parameter, or a dependency injection point. A seam is justified when at least two call sites use it — one in production, one in tests. One adapter is a hypothetical seam; two makes it real.

## Locality

The property that code for a single conceptual change lives close together. When one change touches files scattered across the package tree, locality is broken. Locality is the testability lever: tests for one concept cover one module.

## Leverage

The ratio of names `__all__` exports to behaviour those names deliver. High leverage: few exports, rich behaviour. Low leverage: many exports, each doing little.

## Deletion Test

Ask: if this module were deleted, would its complexity concentrate elsewhere or scatter? If it concentrates, the module earns its keep. If it scatters — each consumer partly absorbing what the module did — the module was a pass-through, and deletion sharpens the design.

## Excavation

The process of digging into a codebase to reveal buried structure: following import chains, unwrapping delegation cascades, stripping pass-through layers until real behaviour is exposed. The leading word for the Explore phase.
