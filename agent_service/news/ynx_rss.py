import time
from typing import Dict
from datetime import datetime
import feedparser

from common.utils import is_time_difference_over_n_hours
from agent_service.news.schemas import RssUrl, RssContents, RssFeed

class YnxRss:
    def __init__(self, update_interval_hours: int = 4):
        """
        update_interval_hours: 업데이트 간격(시간)
        """
        self.rss_url_dict = self.get_rss_url()
        self.rss_contents_dict = {}
        self.update_interval_hours = update_interval_hours
    
    def get_rss_url(self) -> Dict[str, RssUrl]:
        """
        RSS URL 목록을 반환합니다.
        """
        rss_dict = {
            "최신기사": "https://www.yna.co.kr/rss/news.xml",
            "정치": "https://www.yna.co.kr/rss/politics.xml",
            "경제": "https://www.yna.co.kr/rss/economy.xml",
            "사회": "https://www.yna.co.kr/rss/society.xml",
            "문화": "https://www.yna.co.kr/rss/culture.xml",
            "스포츠": "https://www.yna.co.kr/rss/sports.xml",
            "연예": "https://www.yna.co.kr/rss/entertainment.xml",
            "세계": "https://www.yna.co.kr/rss/international.xml",
            "건강": "https://www.yna.co.kr/rss/health.xml",
            "시장경제": "https://www.yna.co.kr/rss/market.xml",
        }
        output_dict = {}
        for key, value in rss_dict.items():
            output_dict[key] = RssUrl(name=key, url=value)
        return output_dict
    
    def get_rss_contents(self, section: str) -> RssContents:
        """
        RSS 내용을 반환합니다.
        """
        if section not in self.rss_url_dict.keys():
            return f"존재하지 않는 섹션입니다. {section}"
        
        section_contents = self.rss_contents_dict.get(section)
        if section_contents is None:
            section_contents = self.get_rss_feed(section)
            self.rss_contents_dict[section] = section_contents
        else: 
            if is_time_difference_over_n_hours(section_contents.updated_at_iso,
                                               self.update_interval_hours):
                section_contents = self.get_rss_feed(section)
                self.rss_contents_dict[section] = section_contents
            
        return self.rss_contents_dict[section]
    
    def get_rss_feed(self, section: str) -> RssContents:
        """
        RSS feed를 업데이트 합니다.
        """
        url = self.rss_url_dict[section].url
        feed = feedparser.parse(url)
        updated_at_iso = self.struct_time_to_iso(feed.updated_parsed)
        output_list = []
        for entry in feed.entries:
            output_list.append(RssFeed(title=entry.title, link=entry.link,
                                       description=entry.description,
                                       pub_date=entry.published, authors=entry.author))
        return RssContents(section=section, contents=output_list, updated_at_iso=updated_at_iso)
    
    def struct_time_to_iso(self, struct_time_obj: time.struct_time) -> str:
        dt = datetime(*struct_time_obj[:6])
        return dt.isoformat()

