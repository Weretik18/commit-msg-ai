"""Interactive selection of generated commit messages."""
from __future__ import annotations

from typing import Callable, List, Optional


REGENERATE_LABEL = "🔄 Regenerate all"
ABORT_LABEL = "❌ Abort"


def choose(candidates: List[str], regenerate_fn: Optional[Callable[[], List[str]]] = None) -> Optional[str]:
    """Show candidates and let user pick. Returns chosen message or None on abort.

    Uses `questionary` if available, falls back to simple numbered prompt.
    """
    try:
        import questionary
        return _questionary_choose(candidates, regenerate_fn)
    except ImportError:
        return _fallback_choose(candidates, regenerate_fn)


def _questionary_choose(candidates, regenerate_fn):
    import questionary
    while True:
        choices = []
        for i, msg in enumerate(candidates, 1):
            preview = msg.splitlines()[0][:80]
            choices.append(questionary.Choice(title=f"{i}. {preview}", value=msg))
        if regenerate_fn is not None:
            choices.append(questionary.Choice(title=REGENERATE_LABEL, value="__regen__"))
        choices.append(questionary.Choice(title=ABORT_LABEL, value=None))

        answer = questionary.select(
            "Pick a commit message:",
            choices=choices,
            qmark="📝",
        ).ask()

        if answer == "__regen__" and regenerate_fn is not None:
            candidates = regenerate_fn()
            continue
        return answer


def _fallback_choose(candidates, regenerate_fn):
    while True:
        print("\nGenerated commit messages:\n")
        for i, msg in enumerate(candidates, 1):
            print(f"--- [{i}] ---")
            print(msg)
            print()
        opts = "/".join(str(i) for i in range(1, len(candidates) + 1))
        extra = ", r=regenerate" if regenerate_fn is not None else ""
        prompt = f"Pick [{opts}{extra}, q=quit]: "
        choice = input(prompt).strip().lower()
        if choice == "q":
            return None
        if choice == "r" and regenerate_fn is not None:
            candidates = regenerate_fn()
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(candidates):
            return candidates[int(choice) - 1]
        print("Invalid choice, try again.")
