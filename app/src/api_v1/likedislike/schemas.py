from typing import Optional
from pydantic import BaseModel

class VoteSerializer(BaseModel):
    vote_type: bool

class VoteCommentSerializer(VoteSerializer):
    comment_id: Optional[int] = None

class VoteChapterSerializer(VoteSerializer):
    chapter_id: Optional[int] = None
