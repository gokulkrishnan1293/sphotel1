from typing import Literal

from pydantic import BaseModel


class PreferencesUpdateRequest(BaseModel):
    theme: Literal["dark", "high_contrast", "light"]
