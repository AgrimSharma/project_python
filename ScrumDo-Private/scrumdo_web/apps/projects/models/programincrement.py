from django.db import models

# A program increment is a grouping of iterations across two levels in a portfolio.  You have one iteration in a parent
# project, and then several iterations in each of several child projects.

# PI = Program Increment

# Parent - Program Increment (an iteration)  Maybe it's named 'Increment 1'

#    Child project #1
#             Iteration 1.1
#             Iteration 1.2
#             Iteration 1.3

#    Child project #2
#             Iteration 1.1
#             Iteration 1.2
#             Iteration 1.3

#    Child project #3
#             Iteration 1.1
#             Iteration 1.2
#             Iteration 1.3

# The 1.1, 1.2, and 1.3 of each of the child projects all share start/end dates.

# Some special rules:
#   If an iteration is part of a PI, you will be prevented from:
#        1. Delete it
#        2. Change the dates
#

# The data model looks like this:
#
# In the parent project is an Iteration
# It has a ProgramIncrement record pointing to it (It does not have a ProgramIncrementSchedule record unless there is another level of parents with a PI in it)
# That ProgramIncrement has several ProgramIncrementSchedule records
# Each of those ProgramIncrementSchedule records has several Iterations pointing to it from Child projects


class ProgramIncrement(models.Model):
    iteration = models.ForeignKey("projects.Iteration", related_name="+")


class ProgramIncrementSchedule(models.Model):
    increment = models.ForeignKey(ProgramIncrement, related_name='schedule')
    start_date = models.DateField()
    default_name = models.CharField(max_length=100)
