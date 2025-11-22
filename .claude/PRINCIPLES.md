# Software Engineering Principles

**Core Directive**: Evidence > assumptions | Code > documentation | Efficiency > verbosity

## Core Philosophy
- Task-First: Understand → Plan → Execute → Validate
- Evidence-Based: All claims verifiable (testing, metrics, documentation)
- Parallel Thinking: Maximize efficiency through batching and coordination
- Context Awareness: Maintain understanding across sessions

## Design Principles Checklist

**SOLID**:
- [ ] Single Responsibility: One reason to change per component
- [ ] Open/Closed: Open for extension, closed for modification
- [ ] Liskov Substitution: Derived classes substitutable for base
- [ ] Interface Segregation: No unused interface dependencies
- [ ] Dependency Inversion: Depend on abstractions, not concretions

**Core Patterns**:
- [ ] DRY: Abstract common functionality, eliminate duplication
- [ ] KISS: Prefer simplicity over complexity
- [ ] YAGNI: Implement current requirements only

**Systems Thinking**:
- [ ] Ripple Effects: Consider architecture-wide impact
- [ ] Long-term Perspective: Evaluate immediate vs. future trade-offs
- [ ] Risk Calibration: Balance risks with delivery constraints

## Decision Checklist

**Data-Driven**:
- [ ] Measure first (not assumptions)
- [ ] Formulate and test hypotheses systematically
- [ ] Verify information sources
- [ ] Account for cognitive biases

**Trade-offs**:
- [ ] Assess temporal impact (immediate vs. long-term)
- [ ] Classify reversibility (reversible, costly, irreversible)
- [ ] Preserve future options under uncertainty

**Risk**:
- [ ] Identify issues proactively
- [ ] Evaluate probability and severity
- [ ] Develop mitigation strategies

## Quality Checklist

**Quality Quadrants**:
- [ ] Functional: Correctness, reliability, completeness
- [ ] Structural: Organization, maintainability, technical debt
- [ ] Performance: Speed, scalability, resource efficiency
- [ ] Security: Vulnerability management, access control, data protection

**Quality Standards**:
- [ ] Automated enforcement via tooling
- [ ] Preventive measures (catch early)
- [ ] Human-centered design (user welfare, autonomy)
