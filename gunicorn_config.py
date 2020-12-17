bind = "0.0.0.0:5000"
workers = 4
threads = 4
timeout = 120
#
#   Logging
#
#   logfile - The path to a log file to write to.
#
#       A path string. "-" means log to stdout.
#
#   loglevel - The granularity of log output
#
#       A string of "debug", "info", "warning", "error", "critical"
#
errorlog = 'gunicorn.err.log'
loglevel = 'error'
accesslog = 'gunicorn.acc.log'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
reload = True
