
def expandCommentRun(allowContinue=False):
    list = "Resume, Restart"
    linesStr = '''
#------------------------------------------------------------------------------------------
# {section}{has_question} Comment
#------------------------------------------------------------------------------------------
# Display comment
DisplayComment = False

# {text} Write a comment:
""" 
Describe your run here...
"""
#-----------------------------------------------------------------------------
# {section} Run 
#-----------------------------------------------------------------------------
# Run name:
""" 
This will identify your protocol run. It need to be unique for each protocol. 
You could have <run1>, <run2> for protocol X, but not two run1 for same protocol. 
This name together with the protocol output folder will determine the working
directory for this run.
"""
RunName = "run_001"

# {list}(%(list)s) Run behavior
""" 
Resume from the last step, restart the whole process 
or continue at a given step or iteration.
"""
Behavior = "Resume"
'''
    if allowContinue:
        list += ", Continue"
        linesStr += '''
# {condition}(Behavior=="Continue") Resume at iteration:
""" Set to a positive number N to continue the protocol run at step N. """
ContinueAtStep = 1
'''
    return linesStr % locals()

def expandParallel(threads=1, mpi=8, condition="", hours=72):
    if len(condition) > 0:
        condition = "{condition}(%s)" % condition
    linesStr = ''' 
#------------------------------------------------------------------------------------------
# {section} %(condition)s Parallelization
#------------------------------------------------------------------------------------------
'''
    if threads > 0:
        linesStr += '''
# Number of threads
""" 
This option provides shared-memory parallelization on multi-core machines.
It does not require any additional software, other than <Xmipp>
"""
NumberOfThreads = %(threads)d
'''
    if mpi > 0:
        linesStr += '''
# Number of MPI processes
""" 
This option provides the number of independent processes spawned 
in parallel by <mpirun> command in a cluster, usually throught
a queue system. This will require that you have compile <Xmipp>
with <mpi> support.
"""
NumberOfMpi = %(mpi)d

# Submit to queue ? 
"""Submit to queue
"""
SubmitToQueue = True

# {expert}{condition}(SubmitToQueue) Queue name
"""Name of the queue to submit the job
"""
QueueName = "default"

# {condition}(SubmitToQueue) Queue hours
"""This establish a maximum number of hours the job will
be running, after that time it will be killed by the
queue system
"""
QueueHours = %(hours)d
''' 
        return linesStr % locals()