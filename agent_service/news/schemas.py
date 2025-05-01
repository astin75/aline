from pydantic import BaseModel, Field

class RssUrl(BaseModel):
    name: str = Field(description="RSS 이름")
    url: str = Field(description="RSS URL")

class RssFeed(BaseModel):
    title: str = Field(description="RSS 제목")
    link: str = Field(description="RSS 링크")
    description: str = Field(description="RSS 설명")
    pub_date: str = Field(description="RSS 게시일")
    authors: str = Field(description="RSS 작성자")
    
class RssContents(BaseModel):
    section: str = Field(description="RSS 섹션")
    contents: list[RssFeed] = Field(description="RSS 내용")
    updated_at_iso: str = Field(description="RSS 업데이트 시간 ISO 형식")
    
class NewsAgentTimeGuardrail(BaseModel):
    is_specific_time: bool = Field(description="특정 시간대 기사 검색을 요청했는지 여부")
    reason: str = Field(description="특정 시간대 기사 검색을 요청했는지 아닌 이유")
    
class NewsAgentOutputGuardrail(BaseModel):
    is_news_exist: bool = Field(description="기사 존재 여부")
    reason: str = Field(description="기사 존재 여부 이유")
