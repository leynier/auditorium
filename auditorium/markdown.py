# coding: utf8

from auditorium import Show


class MarkdownLoader:
    def __init__(self, path, instance_name='show'):
        self.path = path
        self.instance_name = instance_name

    def parse(self):
        slides = []
        current_slide = []

        with open(self.path) as fp:
            for line in fp:
                line = line.strip("\n")

                if line.startswith("## ") and current_slide:
                    slides.append(current_slide)
                    current_slide = []

                current_slide.append(line)

            if current_slide:
                slides.append(current_slide)

        show = Show()

        for i, slide in enumerate(slides):
            show.slide(func=MarkdownSlide(show, slide), id='slide-%i' % (i+1))

        return show


class MarkdownSlide:
    def __init__(self, show: Show, content):
        self.show = show
        self.content = []

        state = 'markdown' # or 'code'
        split = []

        for line in content:
            if state == 'markdown':
                if line.startswith('```python'):
                    if split:
                        self.content.append(MarkdownContent(split))

                    split = []
                    state = 'code'
                else:
                    split.append(line)

            elif state == 'code':
                if line.startswith('```'):
                    if split:
                        self.content.append(PythonContent(split))

                    split = []
                    state = 'markdown'
                else:
                    split.append(line)

        if split:
            if state == 'markdown':
                self.content.append(MarkdownContent(split))
            else:
                raise ValueError("Didn't closed a Python line...")

    def __call__(self):
        for content in self.content:
            content(self.show)


class MarkdownContent:
    def __init__(self, lines):
        self.lines = "\n".join(lines)

    def __call__(self, show):
        show.markdown(self.lines)


class PythonContent:
    def __init__(self, lines):
        self.lines = "\n".join(lines)

    def __call__(self, show):
        exec(self.lines, dict(show=show), dict())