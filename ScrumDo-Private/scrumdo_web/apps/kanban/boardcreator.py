from .models import Workflow, BoardCell, Policy, BoardHeader, WorkflowStep

import logging

logger = logging.getLogger(__name__)


CELL_WIDTH = 275
DEFAULT_ROW_HEIGHT = 125

colors = [
    0x444444,
    0x777777,
    0x1F1581,
    0x448CCA,
    0x0D7D5B,
    0xFFC54A,
    0xff7f0e,
    0xA60D05,
    0x818B16,
    0x8dc73e
]


def _createBoardWorkflow(sourceProject, destProject):
    workflow = Workflow(project=destProject, name="Overall")
    workflow.save()
    statuses = list(sourceProject.status_choices())
    order = 0
    for status in statuses:
        step = WorkflowStep(order=order,
                            workflow=workflow,
                            name=status[1],
                            report_color=colors[status[0]-1]
                            )

        step.save()
        order += 1
    return workflow


def _createClassOfService(name, sourceProject, destProject, index, startX, startY, height, wips,
                          wipType, overallWip, statusPolicies, boardWorkflow):
    """ Create a workflow for each COS.  Then create a workflow step for each story status in the project
        Lastly, create a cell for each step """
    logger.debug("Creating COS %d %s" % (index, name))
    logger.debug("  Overall Wip %d" % overallWip)
    logger.debug("  Cell Wips %s" % wips)
    logger.debug("  %d,%d x%d" % (startX, startY, height))

    cellMap = {}
    overallPolicy = None

    workflow = Workflow(project=destProject, name=name)
    workflow.save()
    order = 0
    statuses = list(sourceProject.status_choices())

    header = BoardHeader(label=name,
                         project=destProject,
                         sx=startX,
                         sy=startY,
                         ey=startY + 25,
                         ex=startX + len(statuses) * CELL_WIDTH,
                         background=0x282828
                         )
    header.save()

    if overallWip != -1:
        if wipType == "cards":
            ptype = Policy.POLICY_TYPE_STORY_WIP
        else:
            ptype = Policy.POLICY_TYPE_POINTS_WIP

        overallPolicy = Policy(policy_type=ptype,
                               user_defined=True,
                               name="%s Overall" % name,
                               related_value=overallWip,
                               project=destProject
                               )
        overallPolicy.save()
        header.policy = overallPolicy
        header.save()

    for status in statuses:
        step = WorkflowStep(order=order,
                            workflow=workflow,
                            name=status[1],
                            report_color=colors[status[0]-1]
                            )

        step.save()

        cell = BoardCell(project=destProject,
                         label=status[1],
                         headerColor=colors[status[0]-1],
                         x=startX + order * CELL_WIDTH,
                         y=startY + 25,
                         width=CELL_WIDTH,
                         height=height - 25
                         )

        if status[0] in wips:
            if wipType == "cards":
                cell.wipLimit = wips[status[0]]
            else:
                cell.pointLimit = wips[status[0]]

        cell.save()

        if statusPolicies and status[0] in statusPolicies:
            statusPolicy = statusPolicies[status[0]]
            cell.policies.add(statusPolicy)

        if overallPolicy:
            cell.policies.add(overallPolicy)

        cellMap[status[0]] = cell
        cell.steps.add(step)
        cell.steps.add(boardWorkflow.steps.get(name=status[1]))
        order += 1
    return cellMap


def _getOverallWIPS(config):
    hasWips = False
    wips = {}
    for i in xrange(1, 11):
        key = "overallc%d" % i
        if key in config:
            try:
                wips[i] = int(config[key][0])
                hasWips = True
            except:
                pass

    if hasWips:
        return wips
    else:
        return None


def _createOverallStatusWips(sourceProject, destProject, overallStatusWips, wipType, startX, startY):
    policies = {}  # Map of status to a policy object for that status
    if wipType == "cards":
        ptype = Policy.POLICY_TYPE_STORY_WIP
    else:
        ptype = Policy.POLICY_TYPE_POINTS_WIP

    i = 0
    for status in sourceProject.status_choices():
        statusId = status[0]
        statusName = status[1]
        policy = None
        if statusId in overallStatusWips:
            policy = Policy(policy_type=ptype,
                            user_defined=True,
                            name="%s (Overall)" % statusName,
                            related_value=overallStatusWips[statusId],
                            project=destProject
                            )
            policy.save()
            policies[statusId] = policy

        header = BoardHeader(label=statusName,
                             project=destProject,
                             sx=startX + i * CELL_WIDTH,
                             sy=startY,
                             ey=startY + 25,
                             ex=startX + (i+1) * CELL_WIDTH,
                             background=colors[statusId-1],
                             policy=policy
                             )
        header.save()
        i += 1
    return policies


def _createInputQueue(destProject):
    cell = BoardCell(project=destProject,
                     label="Input Queue",
                     headerColor=0xdddddd,
                     x=0,
                     y=0,
                     width=CELL_WIDTH,
                     height=900,
                     layout=BoardCell.LAYOUT_LIST
                     )
    cell.save()


def _createBlockedQueue(destProject, x, y, statusCount):
    cell = BoardCell(project=destProject,
                     label="Blocked",
                     headerColor=0xA60D05,
                     x=x,
                     y=y,
                     width=statusCount * CELL_WIDTH,
                     height=125,
                     layout=BoardCell.LAYOUT_COMPACT_GRID
                     )
    cell.save()


def _createRejectedQueue(destProject, x, statusCount):
    cell = BoardCell(project=destProject,
                     label="Rejected",
                     headerColor=0xe36c09,
                     x=25 + x + statusCount * CELL_WIDTH,
                     y=0,
                     width=CELL_WIDTH,
                     height=900
                     )
    cell.save()


def _createDiscarededQueue(destProject, x, y, statusCount):
    cell = BoardCell(project=destProject,
                     label="Discarded",
                     headerColor=0x666666,
                     x=x,
                     y=y,
                     width=statusCount * CELL_WIDTH,
                     height=125,
                     layout=BoardCell.LAYOUT_COMPACT_GRID
                     )
    cell.save()


def createBoard(sourceProject, destProject, config):
    cellMap = None
    statusPolicies = {}
    logger.debug(config)
    default = int(config["defaultcos"][0])
    wipType = config["wipType"][0]
    statuses = list(sourceProject.status_choices())
    y = 0
    x = 0

    overallStatusWips = _getOverallWIPS(config)

    boardWorkflow = _createBoardWorkflow(sourceProject, destProject)

    if "inputQueue" in config:
        _createInputQueue(destProject)
        x += CELL_WIDTH

    if "blockedQueue" in config:
        _createBlockedQueue(destProject, x, y, len(statuses))
        y += 150

    if "rejectedQueue" in config:
        _createRejectedQueue(destProject, x, len(statuses))

    if overallStatusWips:
        statusPolicies = _createOverallStatusWips(sourceProject, destProject, overallStatusWips, wipType, x, y)
        y += 25

    for i in xrange(1, 11):
        k = "cos%d" % i
        if k in config:
            if default == i:
                height = DEFAULT_ROW_HEIGHT * 2
            else:
                height = DEFAULT_ROW_HEIGHT
            wips = {}
            for status in xrange(1, 11):
                key = "s%dc%d" % (status, i)
                if key in config:
                    wips[status] = int(config[key][0])
            key = "overalls%d" % i
            if key in config:
                overallWip = int(config[key][0])
            else:
                overallWip = -1

            c = _createClassOfService(config[k][0], sourceProject, destProject, i-1, x, y, height, wips, wipType,
                                      overallWip, statusPolicies, boardWorkflow)
            y += height
            if cellMap is None:
                cellMap = c
            if default == i:
                cellMap = c
    if "discardedQueue" in config:
        _createDiscarededQueue(destProject, x, y + 5, len(statuses))
    return cellMap