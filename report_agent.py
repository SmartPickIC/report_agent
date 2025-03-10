from base import BaseAgent
from template_generator import ResultTemplate, Product, Reviews, Purchase_Info_Stores
from youtube_reporter import youtube_main
from review_reporter import review_main
from sepcification_reporter import sepcification_main
import asyncio
from typing import Dict, Any
from abc import ABC, abstractmethod
import threading
from concurrent.futures import ThreadPoolExecutor

class ReportAgent(BaseAgent):
    def __init__(self,name="report_agent"):
        self.name=name
        self.Product=None
        self.Reviews=None
        self.Purchase_Info_Stores=None
        self.generator = ResultTemplate()
        self.result_dict = self.generator.dict
        self.repoterresponse={}
        self.youtube_report=None
        self.review_report=None
        self.specification_report=None
        self.purchase_report=None
        self.last_report=None
        
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        data=state["middleware"]
        youtube_input=data["youtube"]
        query=youtube_input["youtube"]["query"]
        review_input=data["review"]
        specification_input=data["specification"]
        
        # 동기 래퍼 함수들
        def youtube_wrapper():
            # 새 이벤트 루프를 생성하여 비동기 함수 실행
            return asyncio.run(youtube_main(youtube_input))
            
        def review_wrapper():
            return asyncio.run(review_main(review_input, query))
            
        def spec_wrapper():
            return asyncio.run(sepcification_main(specification_input, query))
        
        # 스레드 풀에서 동기 래퍼 함수들 실행
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=3) as executor:
            youtube_future = loop.run_in_executor(executor, youtube_wrapper)
            review_future = loop.run_in_executor(executor, review_wrapper)
            spec_future = loop.run_in_executor(executor, spec_wrapper)
            
            youtube, result_y = await youtube_future
            rewivew, result_r = await review_future
            specification_out, result_s = await spec_future

        specification=specification_out["Product"]
        Purchase_Info=specification_out["Purchase"]
        self.youtube_report=youtube
        self.review_report=rewivew
        self.specification_report=specification
        self.purchase_report=Purchase_Info
        self.repoterresponse["youtube"]=result_y
        self.repoterresponse["review"]=result_r
        self.repoterresponse["specification"]=result_s
        output={}
        output['report']=self.sort_result()
        return output
        
    def sort_result(self):
        self.youtube_report.set_value(self.result_dict)
        self.review_report.set_value(self.result_dict)
        self.specification_report.set_value(self.result_dict)
        self.purchase_report.set_value(self.result_dict)
        self.last_report=self.result_dict
        return self.result_dict
    
