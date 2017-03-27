from apps.kanban.models import Workflow

import logging

logger = logging.getLogger(__name__)


def generateGenericWorkflow(project):
    """This automatically creates a generic Workflow to be used for a project based on the positioning of
       the cells on the board.  It's fairly dumb, simply sorting cells from left to right (and then top to bottom)
       and using that as the order with a single report profile step for each cell.

       In the future, we might want to detect common patterns.  Such as a column of cells all lined up left/right to
       make summary views.

       :return: The workflow
    """
    logger.info(u"Generating default workflow for {project.slug}".format(project=project))
    cells = list(project.boardCells.order_by("x", "y"))
    workflow = _getGenericWorkflow(project)
    steps = workflow.steps.all()
    _removeOutdatedSteps(cells, steps)
    _addMissingSteps(workflow, cells)
    logger.info("Finished generating default workflow")


def _addMissingSteps(workflow, cells):
    """Makes sure that every cell has an appropriate step created, and makes sure they're in the right order.
    """
    order = 1
    for cell in cells:
        cellSteps = cell.steps.filter(workflow=workflow)
        if len(cellSteps) == 0:
            # Need to create it
            step = workflow.steps.create(order=-1)
            step.save()
            step.cells.add(cell)
        elif len(cellSteps) > 1:
            logger.warn("While generating workflow, cell %d had more than one step in the workflow!" % cell.id)
            step = cellSteps[0]
        else:
            step = cellSteps[0]

        # Now, make sure the step is all updated with current data...
        step.order = order

        # Next two are in case the cell had it's properties updated
        step.name = cell.full_label
        step.report_color = cell.headerColor
        step.save()
        order += 1


def _removeOutdatedSteps(cells, steps):
    cell_ids = [c.id for c in cells]
    for step in steps:
        if not step.cells.filter(id__in=cell_ids).exists():
            # Here is a step in our generated sequence that doesn't have a cell in our list of cells, so
            # it's not a valid step.
            logger.info(cell_ids)
            step.delete()



def _getGenericWorkflow(project):
    """ Returns the generic workflow for this project, or creates one if there isn't one
    :param project:
    :return: the workflow
    """
    workflows = list(project.workflows.filter(flow_type=Workflow.WORK_FLOW_TYPES.generated))
    if len(workflows) > 1:
        logger.warn(u"Multiple generated workflows found for {project.slug}".format(project=project))
    elif len(workflows) == 0:
        w = Workflow(project=project, name='Everything', flow_type=Workflow.WORK_FLOW_TYPES.generated)
        w.save()
        return w

    return workflows[0]
