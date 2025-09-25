from dataclasses import dataclass

import regex

CATEGORY_REGEX_GROUP = "category"
LEVEL_REGEX_GROUP = "node"


@dataclass
class ParsedValue:
    id: str
    label: str
    levels: list[str]

    def __lt__(self, other) -> bool:
        if not isinstance(other, ParsedValue):
            return NotImplemented
        return self.id < other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def from_levels(cls, levels: list[str]) -> "ParsedValue":
        return cls(
            id="__".join(levels),
            label=" ".join([level.capitalize() for level in levels]),
            levels=levels,
        )


@dataclass(frozen=True)
class ParsedName:
    original_name: str
    is_match: bool
    name: ParsedValue
    category: ParsedValue | None

    @classmethod
    def from_name(
        cls,
        name: str,
        *,
        is_match: bool,
    ) -> "ParsedName":
        return cls(
            original_name=name,
            is_match=is_match,
            name=ParsedValue(id=name, label=name, levels=[name]),
            category=None,
        )

    @classmethod
    def parse_name(
        cls,
        name: str,
        pattern: str | None = None,
    ) -> "ParsedName":
        if not pattern:
            return cls.from_name(name, is_match=True)

        match = regex.search(pattern, name)

        if not match:
            return cls.from_name(name, is_match=False)

        captures = match.capturesdict()

        if LEVEL_REGEX_GROUP in captures or CATEGORY_REGEX_GROUP in captures:
            levels = captures.get(LEVEL_REGEX_GROUP, [])
            categories = captures.get(CATEGORY_REGEX_GROUP, [])

            if not levels:
                raise ValueError(
                    f"Pattern {pattern} did not capture any {LEVEL_REGEX_GROUP} from name {name}. Make sure to use a named capture group '{LEVEL_REGEX_GROUP}'."
                )

            return cls(
                original_name=name,
                is_match=True,
                name=ParsedValue.from_levels(levels),
                category=ParsedValue.from_levels(categories) if categories else None,
            )

        index = 1
        ended = False
        levels: list[str] = []

        while not ended:
            try:
                captures = match.captures(index)
                if not captures:
                    ended = True
                else:
                    levels.extend(captures)
                    index += 1
            except IndexError:
                ended = True

        if levels:
            return cls(
                original_name=name,
                is_match=True,
                name=ParsedValue.from_levels(levels),
                category=None,
            )

        return cls.from_name("__".join(match.captures(0)), is_match=True)
