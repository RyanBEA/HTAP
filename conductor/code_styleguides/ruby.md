# Ruby Style Guide

## Naming Conventions
- Use `snake_case` for methods, variables, and file names.
- Use `CamelCase` for classes and modules.
- Use `SCREAMING_SNAKE_CASE` for constants.
- Use `?` at the end of predicate methods (returning boolean).
- Use `!` at the end of "dangerous" methods (modifying self or raising errors).

## Formatting
- Use 2 spaces for indentation.
- Limit lines to 80-100 characters.
- Use spaces around operators and after commas.
- Use empty lines between method definitions.

## Best Practices
- Prefer `each` and other enumerables over `for` loops.
- Use `do...end` for multi-line blocks and `{...}` for single-line blocks.
- Avoid using `self` when not necessary.
- Use `attr_reader`, `attr_writer`, and `attr_accessor` for member variables.
