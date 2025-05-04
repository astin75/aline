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


class NewsAgentOutputGuardrail(BaseModel):
    is_news_exist: bool = Field(description="기사 존재 여부")
    reason: str = Field(description="기사 존재 여부 이유")


class NewsAgentInputGuardrail(BaseModel):
    result: str = Field(
        description="검증 분류 결과 [specific_time_error, specific_keyword_error, verified_user_input]"
    )
    answer: str = Field(
        description="사용자 질문에 대한 평가내용 그리고 사용자가 올바른 요청을 할 수 있도록 가이드라인을 제공합니다."
    )


class NewsAgentFinalOutput(BaseModel):
    answer: str = Field(description="뉴스 정보를 제공합니다.")
    status: str = Field(description="뉴스 정보 제공 상태")
