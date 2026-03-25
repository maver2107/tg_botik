from pydantic import BaseModel, Field


class ProfileCheck(BaseModel):
    is_valid: bool = Field(description="Is profile acceptable")
    toxicity: float = Field(description="0 to 1 toxicity score")
    nsfw: bool = Field(description="Contains sexual content")
    spam: bool = Field(description="Contains ads or spam")
    summary: str = Field(description="Short neutral summary")
