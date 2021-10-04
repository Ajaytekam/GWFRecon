import signal 
import libs.workflowlibs as wflibs

def RestoreOriginalHandler():
    # restore the original signal handler 
    original_sigint_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, original_sigint_handler)

def sig_handler(signum, frame):
    # define the handler for Ctrl+C 
    # cancel the workflow
    RestoreOriginalHandler()
    wflibs.CancelWorkflow()

