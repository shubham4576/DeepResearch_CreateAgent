from dataclasses import dataclass, field
from threading import Lock


class FirecrawlBudgetExceeded(RuntimeError):
    pass


@dataclass
class FirecrawlBudget:
    max_pages: int
    max_credits: int
    pages_used: int = 0
    credits_used: int = 0
    _lock: Lock = field(default_factory=Lock, init=False, repr=False, compare=False)

    def ensure_available(self, estimated_credits: int = 1) -> None:
        with self._lock:
            self._ensure_available_unlocked(estimated_credits)

    def record_usage(self, estimated_credits: int = 1) -> None:
        with self._lock:
            self.pages_used += 1
            self.credits_used += estimated_credits

    def reserve_usage(self, estimated_credits: int = 1) -> None:
        with self._lock:
            self._ensure_available_unlocked(estimated_credits)
            self.pages_used += 1
            self.credits_used += estimated_credits

    def refund_usage(self, estimated_credits: int = 1) -> None:
        with self._lock:
            self.pages_used = max(0, self.pages_used - 1)
            self.credits_used = max(0, self.credits_used - estimated_credits)

    def _ensure_available_unlocked(self, estimated_credits: int) -> None:
        if self.pages_used + 1 > self.max_pages:
            raise FirecrawlBudgetExceeded("Firecrawl page budget exceeded")
        if self.credits_used + estimated_credits > self.max_credits:
            raise FirecrawlBudgetExceeded("Firecrawl credit budget exceeded")
