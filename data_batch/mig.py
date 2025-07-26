prompts = [

]
import openai
from pydantic import BaseModel, Field
import requests
class GPTPrompt(BaseModel):
    title: str = Field(..., description="프롬프트의 제목")
    description: str = Field(..., description="프롬프트의 설명")
    tags: list[str] = Field(..., description="프롬프트의 태그 목록")

for prompt in prompts:
    system_prompt = """"
    
    # 역할
    해당 프롬프트는 해외영업지원부서에서 사용하는 에이전트들 프롬프트야.
    너는 해당 프롬프트를 읽고 해당 프롬프트의 제목, 설명, 태그를 추출하면 돼.
    태그목록은 명확하고 간결하게 2~3개만 넣어줘.
    프롬프트의 설명은 2-3 문장으로 이 프롬프트를 가장 잘 표현할 수 있는 문장으로 작성해줘.

    ## 제한사항
    - 반드시 한국어로 작성해야해.
    """
    gptPrompt = openai.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        response_format=GPTPrompt
    )
    target = gptPrompt.choices[0].message.parsed
    default_title = "GPT 프롬프트 제목"
    default_description = "GPT 프롬프트 설명"
    default_tags = ["GPT", "프롬프트", "자동화"]
    if target:
        print(f"Title: {target.title}")
        print(f"Description: {target.description}")
        print(f"Tags: {', '.join(target.tags)}")

        default_title = target.title
        default_description = target.description
        default_tags = target.tags

    
    body = {
      "agent": {
        "department_name": "InternationalSales",
        "description": default_description,
        "name": default_title,
        "prompt": prompt,
        "tags": default_tags
      }
    }
    resp = requests.post(
        "http://localhost:8000/api/v1/agents/publish",
        json=body
    )
    print(resp.json())

