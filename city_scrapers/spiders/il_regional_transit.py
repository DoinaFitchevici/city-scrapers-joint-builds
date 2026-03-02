from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from datetime import time, datetime
import scrapy


class IlRegionalTransitSpider(CityScrapersSpider):
    name = "il_regional_transit"
    agency = "Regional Transportation Authority"
    timezone = "America/Chicago"
    
    all_meetings_url = "https://www.rtachicago.org/about-rta/boards-and-committees/meeting-materials?year={year}"
    upcoming_meetings_url = "https://www.rtachicago.org/about-rta/boards-and-committees/meeting-materials"

    _location = {
        "name": "RTA Headquarters",
        "address": "175 W. Jackson Blvd., Chicago, IL 60604",
    }

    _time_note = "Check the source link for the most up-to-date information on meeting times and locations."

    _start_time = time(9, 0)

    custom_settings = {"ROBOTSTXT_OBEY": False}

    def start_requests(self):
        yield scrapy.Request(
            url=self.upcoming_meetings_url,
            callback=self._get_all_meetings,
        )
    def _get_all_meetings(self, response):
        upcoming_section = response.css(".mx-auto.max-w-screen-2xl.p-6")
        current_year = datetime.now().year
        print(f"HERE: {upcoming_section}")
        for year in range(current_year - 5, current_year + 1):
            print(f"YEAR: {year}")
            yield scrapy.Request(
                url=self.all_meetings_url.format(year=year),
                callback=self.parse,
            )

    def parse(self, response):
        print(f"HERE: {response.url}")
        # for item in response.css(".meetings"):
        #     meeting = Meeting(
        #         title=self._parse_title(item),
        #         description=self._parse_description(item),
        #         classification=self._parse_classification(item),
        #         start=self._parse_start(item),
        #         end=self._parse_end(item),
        #         all_day=self._parse_all_day(item),
        #         time_notes=self._parse_time_notes(item),
        #         location=self._parse_location(item),
        #         links=self._parse_links(item),
        #         source=self._parse_source(response),
        #     )

        #     meeting["status"] = self._get_status(meeting)
        #     meeting["id"] = self._get_id(meeting)

        yield None

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return None

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
