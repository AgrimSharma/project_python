# Utilities to export an excel sheet to compare estimated vs. actual time entries.

from django.db.models import Sum
from django.utils.html import strip_tags

import xlwt
ezxf = xlwt.easyxf

def get_time_data(project, iteration):
    """For a given iteration and project, return an array of cards annotated with a minutes_spent attribute."""
    return iteration.stories.all().annotate(minutes_spent=Sum("time_entries__minutes_spent")).order_by('local_id')


def generate_iteration_report(project, iteration):
    stories = get_time_data(project, iteration)
    w = xlwt.Workbook(encoding='utf8')
    sheet = w.add_sheet("Cards")

    sheet.col(0).width = 37*50
    sheet.col(1).width = 37*350
    sheet.col(2).width = 37*350
    sheet.col(3).width = 37*50
    sheet.col(4).width = 37*100
    sheet.col(5).width = 37*100
    sheet.col(6).width = 37*100
    sheet.col(7).width = 37*75
    sheet.col(8).width = 37*75

    sheet.write(0, 0, "Number")
    sheet.write(0, 1, "Summary")
    sheet.write(0, 2, "Detail")
    sheet.write(0, 3, "Points")
    sheet.write(0, 4, "Cell")
    sheet.write(0, 5, "Epic")
    sheet.write(0, 6, "Assignees")
    sheet.write(0, 7, "Minutes Estimated")
    sheet.write(0, 8, "Minutes Recorded")

    wrap_format = ezxf('align: wrap on, vert top')

    row = 1
    for story in stories:
        sheet.write(row, 0, story.local_id)
        sheet.write(row, 1, strip_tags(story.summary), wrap_format)
        sheet.write(row, 2, strip_tags(story.detail), wrap_format)
        sheet.write(row, 3, story.points)
        if story.cell:
            sheet.write(row, 4, story.cell.full_label)
        if story.epic:
            sheet.write(row, 5, story.epic.summary, wrap_format)
        sheet.write(row, 6, story.assignees_cache, wrap_format)
        sheet.write(row, 7, story.estimated_minutes)
        sheet.write(row, 8, story.minutes_spent)
        row += 1

    return w


