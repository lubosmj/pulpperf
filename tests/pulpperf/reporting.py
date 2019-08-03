import datetime
import statistics

DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"


def tasks_table(tasks):
    """Return overview of tasks in the table"""
    out = "%56s\t%27s\t%27s\t%27s\t%s\n" \
        % ('task', 'created', 'started', 'finished', 'state')
    for t in tasks:
        out += "%s\t%s\t%s\t%s\t%s\n" \
            % (t['_href'], t['_created'], t['started_at'], t['finished_at'],
               t['state'])
    return out


def tasks_min_max_table(tasks):
    """Return overview of tasks dates min and max in a table"""
    out = "\n%11s\t%27s\t%27s\n" % ('field', 'min', 'max')
    for f in ('_created', 'started_at', 'finished_at'):
        sample = [datetime.datetime.strptime(t[f], DATETIME_FMT)
                  for t in tasks]
        out += "%s\t%s\t%s\n" \
            % (f,
               min(sample).strftime(DATETIME_FMT),
               max(sample).strftime(DATETIME_FMT))
    return out


def data_stats(data):
    return {
        'samples': len(data),
        'min': min(data),
        'max': max(data),
        'mean': statistics.mean(data),
        'stdev': statistics.stdev(data) if len(data) > 1 else 0.0,
    }


def tasks_waiting_time(tasks):
    """Analyse tasks waiting time (i.e. started_at - _created)"""
    durations = []
    for t in tasks:
        diff = datetime.datetime.strptime(t['started_at'], DATETIME_FMT) \
            - datetime.datetime.strptime(t['_created'], DATETIME_FMT)
        durations.append(diff.total_seconds())
    return data_stats(durations)


def tasks_service_time(tasks):
    """Analyse tasks service time (i.e. finished_at - started_at)"""
    durations = []
    for t in tasks:
        diff = datetime.datetime.strptime(t['finished_at'], DATETIME_FMT) \
            - datetime.datetime.strptime(t['started_at'], DATETIME_FMT)
        durations.append(diff.total_seconds())
    return data_stats(durations)


def fmt_start_end_date(label, start, end):
    return "%s: %s - %s" % (label, start.strftime(DATETIME_FMT), end.strftime(DATETIME_FMT))
