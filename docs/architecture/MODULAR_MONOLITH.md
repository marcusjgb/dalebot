# Modular Monolith

Monolith does not mean mixed code. Each module represents a domain and maintains high cohesion.

## Future Extraction
A module is only considered a candidate for an independent service when:
- it has stable boundaries;
- it requires different scaling;
- it presents a measured bottleneck;
- it needs independent deployment;
- the benefit outweighs the operational cost.

Premature extraction is forbidden.
