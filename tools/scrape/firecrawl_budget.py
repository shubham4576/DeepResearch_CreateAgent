from dataclasses import dataclass


@dataclass
class FirecrawlBudget:
    max_pages: int
    max_credits: int
    pages_used: int = 0
    credits_used: int = 0

    def ensure_available(self, estimated_credits: int = 1) -> None:
        if self.pages_used + 1 > self.max_pages:
            raise RuntimeError("Firecrawl page budget exceeded")
        if self.credits_used + estimated_credits > self.max_credits:
            raise RuntimeError("Firecrawl credit budget exceeded")

    def record_usage(self, estimated_credits: int = 1) -> None:
        self.pages_used += 1
        self.credits_used += estimated_credits
