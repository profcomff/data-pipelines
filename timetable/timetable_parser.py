from typing import Any, List, Dict
from bs4 import BeautifulSoup as BS


class Group:
    def __init__(self, html: BS):
        self.data = html
        self.tags: List[BS] = []
        self.result: List[Dict[str, Any]] = []

    def run(self) -> List[Dict[str, Any]]:
        body = self.data.select("body")[0]
        rows = body.select("tr")[1]
        self.tags = list(filter(lambda x: x != "\n", rows.children))

        group = self.get_group()
        lessons = self.get_lessons()
        for lesson in lessons:
            self.result.append(dict(**lesson, group=group))
        return self.result

    def get_group(self) -> str:
        """Номер группы из заголовка страницы."""
        return self.tags[1].text

    def get_lessons(self) -> List[Dict[str, Any]]:
        """Список предметов."""
        lessons: List[Dict[str, Any]] = []
        weekday = 0
        lesson_num = 1

        for tag in self.tags[2:-1]:
            if len(tag.select("td.delimiter")) != 0:
                # Парсим разрывы дней
                lesson_num = 1
                weekday += 1
                continue
            lesson = Lesson(tag).run()
            lesson['weekday'] = weekday
            lesson['num'] = lesson_num
            lesson['start'] = lesson.get('start') or lessons[-1]['start']
            lesson['end'] = lesson.get('end') or lessons[-1]['end']
            if lesson['type'] in ['KIND_ITEM1', 'KIND_SMALL1_WITHOUT_TIME', 'KIND_SMALL1_WITH_SMALL0_WITH_TIME']:
                lesson_num += 1
            lessons.append(lesson)
        return lessons


class Lesson:
    def __init__(self, html: BS):
        self.html = html
        self.type = self.define_type()
        self.result: Dict[str, Any] = {}

    def run(self) -> Dict[str, Any]:
        if self.type == 'KIND_ITEM1':
            self.result = self._get_item1()
        elif self.type == 'KIND_SMALL1_WITH_TIME':
            self.result = self._get_small1_with_time()
        elif self.type == 'KIND_SMALL1_WITHOUT_TIME':
            self.result = self._get_small1_without_time()
        elif self.type == 'KIND_ITEM1_WITH_SMALL0':
            self.result = self._get_item1_with_small0()
        elif self.type == 'KIND_SMALL1_WITH_SMALL0_WITH_TIME':
            self.result = self._get_small1_with_small0_with_time()
        elif self.type == 'KIND_SMALL1_WITH_SMALL0_WITHOUT_TIME':
            self.result = self._get_small1_with_small0_without_time()
        else:
            raise RuntimeError('Unexpected type of lesson')
        self.result.update({'type': self.type})
        return self.result

    def define_type(self):
        if len(self.html.select("td.tditem1")) != 0:
            if len(self.html.select("td.tdsmall0")) != 0:
                return 'KIND_ITEM1_WITH_SMALL0'
            return 'KIND_ITEM1'

        if len(self.html.select("td.tdsmall1")) != 0:
            if len(self.html.select("td.tdsmall0")) != 0:
                if len(self.html.select("td.tdtime")) != 0:
                    return 'KIND_SMALL1_WITH_SMALL0_WITH_TIME'
                else:
                    return 'KIND_SMALL1_WITH_SMALL0_WITHOUT_TIME'
            else:
                if len(self.html.select("td.tdtime")) != 0:
                    return 'KIND_SMALL1_WITH_TIME'
                else:
                    return 'KIND_SMALL1_WITHOUT_TIME'

    def _get_item1(self):
        html = self.html.select("td.tditem1")[0]
        time = self.html.select("td.tdtime")[0].contents
        return {"name": html.prettify(), "start": time[0], "end": time[-1], "odd": True, "even": True}

    def _get_small1_with_time(self):
        html = self.html.select("td.tdsmall1")[0]
        time = self.html.select("td.tdtime")[0].contents
        return {"name": html.prettify(), "start": time[0], "end": time[-1], "odd": True, "even": False}

    def _get_small1_without_time(self):
        html = self.html.select("td.tdsmall1")[0]
        return {"name": html.prettify(), "odd": False, "even": True}

    def _get_item1_with_small0(self):
        html = self.html.select("td.tdsmall0")[0]
        time = self.html.select("td.tdtime")[0].contents
        return {"name": html.prettify(), "start": time[0], "end": time[-1], "odd": True, "even": True}

    def _get_small1_with_small0_with_time(self):
        html = self.html.select("td.tdsmall0")[0]
        time = self.html.select("td.tdtime")[0].contents
        return {"name": html.prettify(), "start": time[0], "end": time[-1], "odd": True, "even": False}

    def _get_small1_with_small0_without_time(self):
        html = self.html.select("td.tdsmall0")[0]
        return {"name": html.prettify(), "odd": False, "even": True}


def run(html: str) -> List[Dict[str, Any]]:
    html = BS(html, "html.parser")
    tt = Group(html).run()
    return tt


