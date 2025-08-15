import io
from backend.rag.upload import upload_file
from backend.rag.format import format_file
from backend.rag.splitter import split_by_header

async def test_splitter():
    test = ['> 과학기술정보통신부 공고 제2025-0830호\n\n\n## 2025년도 최고급 AI 해외인재 유치지원 사업 재공고\n\n\n과학기술정보통신부는 우수한 글로벌 AI 인재 유치를 통해 국내 AI 인재양성 및 AI 연구생태계 활성화를 위한 2025년도 최고급 AI 해외인재 유치지원 사업을 재공고하오니 많은 관심과 참여를 바랍니다.\n\n2025년 8월 11일 과학기술정보통신부 장관 정보통신기획평가원장\n\n과학기술정보통신부 공고 제2025-0692호(2025년 6월 20일 공고)에 따라 기선정된 과제 이외의 과제에 대해 다음과 같이 재공고하며, 지원대상, 지원분야, 인건비 비중, 선정 평가 항목 등 수정 사항이 있습니다.\n\n☐ 지원대상 사업 : 2025년도 최고급 AI 해외인재 유치지원 사업\n\n☐ 사업목적 :\n\n☐ ○ 우수한 AI 해외 인재 유치를 지원하여 기업의 Al 혁신 연구프로젝트 수행 및 국내 AI 고급인재 양성, 글로벌 네트워크 구축 등 AI 연구생태계 질적 제고\n\n☐ 공고기간 : 2025. 8. 11.(월) ~ 2025. 9. 9.(화) 오후 3시, 30일간\n\n○ 전산 접수기간 : 2025. 8. 20.(수) ~ 2025. 9. 9.(화) 오후 3시까지(IRIS 시스템 시간 기준) ☐\n\n☐ 지원대상 : 1 기업, 2 기업 + 대학 컨소시엄, 3 기업 간 컨소시엄\n\n* 주관기관은 ‘기업’\n\n☐ 지원분야 : AI 분야* 최고급 해외인재 유치 지원\n\n* (예시) 생성AI, 피지컬AI, AI에이전트 등 고도화된 AI 기술 또는 모빌리티, 헬스케어, 금융, 에너지, 교육 등 AI 융합 분야 전 영역\n\n□ 접수방법 : 범부처통합연구지원시스템 (iris.go.kr)을 통한 신청 접수 ☐\n\n※ IRIS를 통한 접수 방법은 매뉴얼 참조\n\n※ 관련 법령 개정 등 주요한 변경 사항 발생 시 수정 공고문을 게시할 수 있습니다.\n\n【 연구개발계획서 작성. 신청시 중점 고려사항 안내 】\n\n과학기술정보통신부와 정보통신기획평가원에서는 ICT R&D 우수성과 결과물이 R&D로 끝나지 않고 후속연구 및 시장으로 보급. 확산될 수 있도록 새롭게 시행하는 사항들에 대해 안내드리오니 연구개발계획서 작성시 안내 사항들을 충분히 검토 후 반영하여 과제를 시alld zj- mlalilpl\n\n', "*Page - 1 -*\n\n\n정부에서 지원하는 R&D가 R&D로 끝나지 않고 혁신적인 기술 및 파급력 있는 성과창출이 될 수 있도록 연구개발계획서에 적절하게 반영 후 신청하여 주시기 바랍니다.\n\n### 【 과제 선정 이후 연구자의 이행사항 안내 】\n\n\nICT R&D 연구자간 시너지 향상과 우수성과 결과물이 R&D로 끝나지 않고 시장으로 보급. 확산될 수 있도록 연구수행시 이행하여야 할 사항을 안내드리오니 협조 부탁드립니다.\n\n1 연구책임자는 특별한 사유가 없는 한 IITP에서 진행하는 각종 평가에 최소 1회/연 참여를 협조하여 주시기 바랍니다.\n\n평가자와 피평가자 모두가 만족할 수 있는 평가 운영을 위해 IITP에서 진행하는 각종 평가. 검토에 참여하신 연구자분들은 과제 기획위원 또는 정부정책 및 사업추진 관련 전문가 회의시 우선적으로 위촉하여 드릴 예정이오니, 전문성을 갖춘 연구자분들의 적극적인 참여를 부탁드립니다.\n\n2 국가연구개발혁신법 제15조(특별평가를 통한 연구개발과제의 변경 및 중단)에 의거하여 수행중인 연구과제 중단 여부 또는 목표변경 등을 결정하기 위한 평가가 진행될 수 있습니다.\n\n* 연구개발 환경이 변경되어 연구개발과제를 계속하여 수행하는 것이 불필요하다고 판단되는 경우, 연구 개발 환경이 변경되었거나 연구개발과제 목표를 조기에 달성하여 연구개발과제를 계속하여 수행하는 것이 필요하지 아니하다고 판단되는 경우 등\n\n3 연구기관 및 연구자는 수행 중이거나 종료된 과제에서 우수한 성과가 창출된 경우, 관련 성과물(논문, 특허, 표준화, 기술이전 등)을 부처(과기정통부 등) 및 IITP에 통보 및 관련 자료를 제출하여야 하며, 성과 홍보에 노력하여야 합니다.\n\n또한, 연구기관 및 연구자는 성과 홍보 시(각종 전시 참여. 홍보 등) 다음의 사사 (ack nowledgement) 문구(안)을 포함하여야 하며, 언론 홍보가 예정되어 있는 경우, IITP와 협의 등 적극적인 협조를 부탁드립니다.\n\n* (문구 예시) ~~ (중략) 0000 연구성과는 과기정통부 · 정보통신기획평가원의 'ooooo사업'으로 수행한 결과입니다. (생략)\n\n국가연구개발사업 성공과 우리나라 ICT 기술 발전과 경쟁력 강화를 위해 연구자분들의 많은 관심과 적극적인 참여를 당부드립니다.\n\n### 1 사업개요\n\n\n☐ (사업목적) 우수한 AI 해외 인재 유치를 지원하여 기업의 AI 혁신 연구프로젝트 수행 및 국내 AI 고급인재 양성, 글로벌 네트워크 구축 등 AI 연구 생태계 질적 제고\n\n"]
    for page in test:
        splited = split_by_header(page)
        
        for sp in splited:
            print(sp.strip())
            print("===" * 10)


async def main():
    with open("Document Print.pdf", "rb") as file:  # encoding 제거
        file_stream = io.BytesIO(file.read())
        file_name = "Document Print.pdf"
        
        # Upload the file to Azure Blob Storage
        blob_url, err = await upload_file(file_stream, file_name)
        if err:
            print(f"Error uploading file: {err}")
            return

        print(f"File uploaded to: {blob_url}")
        
        # Process the uploaded file
        result, err = await format_file(blob_url)
        if err:
            print(f"Error processing file: {err}")
        else:
            for page in result:
                print(page)
    
    with open("result.txt", "w", encoding="utf-8") as result_file:  # 여기는 텍스트 모드니까 OK
        result_file.write(str(result))


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_splitter())
    