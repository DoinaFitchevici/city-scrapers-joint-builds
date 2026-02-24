from turtle import title
from urllib.parse import urlencode
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import random
import scrapy
from dateutil.parser import parse
import re


class ColumBoeSpider(CityScrapersSpider):
    # just for easy access
    # https://go.boarddocs.com/oh/columbus/Board.nsf/Public

    name = "colum_boe"
    agency = "Columbus Board of Education"
    timezone = "America/Chicago"
    api_url = "https://go.boarddocs.com/oh/columbus/Board.nsf/BD-GetMeetingsList?open&0.{random_digit}"  # noqa
    detail_url = "https://go.boarddocs.com/oh/columbus/Board.nsf/BD-GetMeeting?open&0.{random_digit}"  # noqa

    get_agenda_url = "https://go.boarddocs.com/oh/columbus/Board.nsf/BD-GetAgenda?open&0.{random_digit}"
    agenda_url = "https://go.boarddocs.com/oh/columbus/Board.nsf/goto?open&id={attachment_id}" # noqa

    boarddocs_committee_id = "A9HCVU32F33A"

    random_digit = random.randint(10**14, 10**15 - 1)

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.api_url.format(random_digit=self.random_digit),
            method="POST",
            body=f"current_committee_id={self.boarddocs_committee_id}",
            callback=self._get_meeting_detail,
        )

    def _get_meeting_detail(self, response):
        meetings = response.json()

        for meeting in meetings:
            meeting_id = meeting.get("unique")
            yield scrapy.Request(
                url=self.detail_url.format(random_digit=self.random_digit),
                method="POST",
                body=f"current_committee_id={self.boarddocs_committee_id}&id={meeting_id}",  # noqa
                meta={"meeting_id": meeting_id},
                callback=self._get_agenda,
            )
            break

    def _get_agenda(self, response):
        raw_description = response.css(".meeting-description::text").getall()
        meeting_id = response.meta["meeting_id"]
        yield scrapy.Request(
            url=self.get_agenda_url.format(random_digit=self.random_digit),
            method="POST",
            body=f"current_committee_id={self.boarddocs_committee_id}&id={meeting_id}",
            meta={"detail_response": response, "raw_description": raw_description},
            callback=self.parse,
        )
      

    def parse(self, response):
        detail_response = response.meta["detail_response"]
        raw_description = response.meta["raw_description"]
        meeting = Meeting(
            title=self._parse_title(detail_response),
            description=self._parse_description(raw_description),
            classification=BOARD,
            start=self._parse_start(raw_description, detail_response),
            end=None,
            all_day=False,
            time_notes="",
            location=self._parse_location(detail_response, raw_description),
            links=self._parse_links(response),
            source=response.url,
        )

        # meeting["status"] = self._get_status(meeting)
        meeting["status"] = PASSED
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_title(self, item):
        title = item.css(".meeting-name::text").get()
        return title

    def _parse_description(self, item):
        return " ".join(item)

    def _parse_start(self, raw_description, detail_response):
        date = detail_response.css(".meeting-date::text").get()
       
        return parse(date)

    def _parse_location(self, detail_response, raw_description):
        """Parse or generate location."""
        title_location = self._parse_title(detail_response).lower()
        if "board" in title_location and "special" not in title_location:
            return {
                "name": "COLUMBUS CITY SCHOOLS",
                "address": "3700 S. HIGH ST. COLUMBUS, OH 43207"
            }
        return {
            "address": "",
            "name": "TBD",
        }

    def _parse_links(self, item):
        agenda_id = item.css("li.XXXXXXui-corner-all::attr(unique)").get()

        return [{"title": "Agenda", "href": self.agenda_url.format(attachment_id=agenda_id)}] if agenda_id else [] # noqa