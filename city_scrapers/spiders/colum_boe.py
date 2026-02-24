from urllib.parse import urlencode
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import random
import scrapy
from dateutil.parser import parse as dateparse


class ColumBoeSpider(CityScrapersSpider):
    # just for easy access
    # https://go.boarddocs.com/oh/columbus/Board.nsf/Public

    name = "colum_boe"
    agency = "Columbus Board of Education"
    timezone = "America/Chicago"
    api_url = "https://go.boarddocs.com/oh/columbus/Board.nsf/BD-GetMeetingsList?open&0.{random_digit}"  # noqa
    detail_url = "https://go.boarddocs.com/oh/columbus/Board.nsf/BD-GetMeeting?open&0.{random_digit}"  # noqa

    get_agenda_url = "https://go.boarddocs.com/oh/columbus/Board.nsf/BD-GetAgenda?open&0.{random_digit}"
    agenda_url = "https://go.boarddocs.com/oh/columbus/Board.nsf/BD-GetAgendaItem?open&0.{random_digit}"

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
                body=f"current_committee_id={self.boarddocs_committee_id}&id={meeting_id}",
                meta={"meeting_id": meeting_id},
                callback=self._get_agenda,
            )
            break

    def _get_agenda(self, response):
        yield scrapy.Request(
            url=self.agenda_url.format(random_digit=self.random_digit),
            method="POST",
            body=f"current_committee_id={self.boarddocs_committee_id}&id=DQ3VPZ80F262",
            meta={"detail_response": response},
            callback=self.parse,
        )

    def parse(self, response):
        meeting = Meeting(
            title=self._parse_title(response),
            description=self._parse_description(response),
            classification=BOARD,
            start=self._parse_start(response),
            end=None,
            all_day=False,
            time_notes="",
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=response.url,
        )

        # meeting["status"] = self._get_status(meeting)
        meeting["status"] = PASSED
        meeting["id"] = self._get_id(meeting)

    def _parse_title(self, item):
        title = item.css(".meeting-name::text").get()
        return title

    def _parse_description(self, item):
        desc_text = item.css(".meeting-description::text").getall()
        return " ".join(desc_text).strip()

    def _parse_start(self, item):
        start = item.css(".meeting-date::text").get()
        return dateparse(start)

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        return []