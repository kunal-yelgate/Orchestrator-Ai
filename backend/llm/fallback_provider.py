"""
fallback_provider.py

Automatic Provider Fallback (Feature 3).

Wraps a primary LLM provider with a secondary "fallback" provider. Every
agent node calls state["llm"].generate(...) without knowing or caring
whether that's a single provider or a fallback pair -- so this class is
the only thing that needs to know about failover.

    Groq ❌
      |
      v
    Gemini ✅
      |
      v
    Continue Workflow

If the primary provider's generate() call raises for ANY reason (auth
error, rate limit, timeout, outage, invalid response, etc.), the fallback
provider is tried automatically before the exception is allowed to
propagate up into the calling agent node. Only if BOTH providers fail
does generate() raise -- at which point the caller's normal error
handling takes over.
"""


class FallbackProvider:

    def __init__(
        self,
        primary,
        primary_name: str,
        fallback=None,
        fallback_name: str = "",
        on_fallback=None,
    ):
        """
        primary / fallback: objects exposing .generate(system_prompt, user_prompt, temperature)
        primary_name / fallback_name: display names used in logs/events (e.g. "groq", "gemini")
        on_fallback: optional callback(event: dict) invoked whenever a fallback
                     is triggered, so the caller can record it (e.g. onto
                     workflow state for the frontend to display).
        """

        self.primary = primary
        self.primary_name = primary_name
        self.fallback = fallback
        self.fallback_name = fallback_name
        self.on_fallback = on_fallback

    def generate(self, **kwargs):

        try:
            return self.primary.generate(**kwargs)

        except Exception as primary_error:

            if not self.fallback:
                # No fallback configured/available -- behave exactly like
                # a plain provider always did.
                raise

            print(
                f"\n[Provider Fallback] {self.primary_name} failed "
                f"({primary_error}). Falling back to {self.fallback_name}...\n"
            )

            self._emit_event(
                from_provider=self.primary_name,
                to_provider=self.fallback_name,
                reason=str(primary_error),
            )

            try:
                return self.fallback.generate(**kwargs)

            except Exception as fallback_error:

                # Both providers failed -- this is a genuine, workflow-
                # halting error. Let the caller's existing error handling
                # (which every agent node already has) take over.
                raise RuntimeError(
                    f"Both providers failed. "
                    f"{self.primary_name}: {primary_error} | "
                    f"{self.fallback_name}: {fallback_error}"
                )

    def _emit_event(self, from_provider, to_provider, reason):

        if not self.on_fallback:
            return

        try:
            self.on_fallback({
                "from_provider": from_provider,
                "to_provider": to_provider,
                "reason": reason,
            })
        except Exception:
            # Recording the event must never itself break generation.
            pass
