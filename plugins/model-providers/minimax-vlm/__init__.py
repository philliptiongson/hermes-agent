"""MiniMax VLM provider profile — dedicated vision endpoint.

Endpoint: POST https://api.minimax.io/v1/coding_plan/vlm
  - Custom JSON wire: {"prompt": str, "image_url": "data:image/jpeg;base64,..."}
  - Returns: {"content": str, "base_resp": {"status_code": int, "status_msg": str}}
  - Auth: Bearer token from MINIMAX_CODING_PLAN_KEY env var (sk-cp-* prefix)
  - Multi-image NOT supported
  - Rate limit: 15K requests per 5-hour rolling window

Unlike the standard minimax provider (text via /anthropic), this hits the
separate coding-plan VLM endpoint with a different API key tier.
"""

from providers import register_provider
from providers.base import ProviderProfile

minimax_vlm = ProviderProfile(
    name="minimax-vlm",
    aliases=("minimax_vlm", "minimaxvlm"),
    display_name="MiniMax VLM",
    description="MiniMax Vision Language Model — dedicated screenshot/UI understanding",
    env_vars=("MINIMAX_CODING_PLAN_KEY",),
    base_url="https://api.minimax.io/v1/coding_plan",
    auth_type="api_key",
)

register_provider(minimax_vlm)
