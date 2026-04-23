# Alan M. Turing — On Computable Numbers (1936)

> "The 'computable' numbers may be described briefly as the real numbers whose expressions as a decimal are calculable by finite means."
> — A. M. Turing, 1936

## About the Paper

**Full Title:** On Computable Numbers, with an Application to the Entscheidungsproblem  
**Author:** Alan Mathison Turing  
**Published in:** Proceedings of the London Mathematical Society, Series 2, Vol. 42  
**Received:** 28 May 1936 — Read: 12 November 1936

This paper is widely regarded as the founding document of computer science. When Turing wrote it at 24, no physical computer existed. He was building a purely mental model — yet that model became the theoretical foundation of the greatest technological revolution of the 20th century.

## Three Big Claims

**1. The Turing Machine**  
A minimal, abstract machine model capable of performing any computation. Four operations: write a symbol, erase a symbol, move left, move right.

**2. The Universal Turing Machine**  
A single machine that can simulate any other Turing machine. The conceptual predecessor of our modern computers.

**3. The Undecidability of the Entscheidungsproblem**  
Hilbert's 1928 question — "Is there a mechanical procedure to determine the truth of any mathematical statement?" Answer is No. Such an algorithm cannot exist.

## Files

| File | Contents | Paper Section |
|---|---|---|
| `section3_example1.py` | Turing machine that produces 010101... | §3, Example I |
| `section3_example2.py` | Turing machine that produces 001011011101111... | §3, Example II |

## Key Concepts

**Computable Number:** A number whose decimal digits can be produced step by step by a machine. π, e, and all algebraic numbers are computable.

**m-configuration (State):** The internal condition of the machine at any given moment. There are finitely many states.

**Configuration:** The pair (current state, scanned symbol). This pair completely determines the machine's next move.

**Circular Machine:** A machine that eventually produces only finitely many meaningful symbols — it gets stuck. The formal counterpart of the Halting Problem.

**Circle-free Machine:** A machine that keeps producing meaningful output indefinitely.

## Links

- [Original paper (PDF)](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf)
- [Medium article](#) *(coming soon)*
- [Wikipedia — Turing Machine](https://en.wikipedia.org/wiki/Turing_machine)
- [Wikipedia — Halting Problem](https://en.wikipedia.org/wiki/Halting_problem)

## Further Reading

- Alonzo Church — "An Unsolvable Problem of Elementary Number Theory" (1936) — Reached the same conclusion via Lambda Calculus at the same time.
- Kurt Gödel — "Über formal unentscheidbare Sätze" (1931) — The Incompleteness Theorems that deeply influenced Turing's approach.
- John von Neumann — "First Draft of a Report on the EDVAC" (1945) — Translated Turing's theoretical model into a physical machine architecture.
