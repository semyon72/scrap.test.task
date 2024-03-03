import os
from typing import Callable, Optional

import marshmallow as ma

from environs import Env
from schedule import Job, ScheduleValueError, Scheduler

from .decorators import run_once


def prefixed_env_to_dict(env: Env, prefix: str, sufixes: list):
    res = {}
    with env.prefixed(f'{prefix}_'):
        for s in sufixes:
            _sn, _sm = s, Env.str
            if isinstance(s, (list, tuple)):
                _sn, _sm = s
            res[_sn.lower()] = _sm(env, _sn)
    return res


class ScheduleJobSchema(ma.Schema):
    __model__ = Job

    schedule_weekdays = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

    interval = ma.fields.Int(allow_none=True, load_default=1, load_only=True)
    do = ma.fields.String(required=True, allow_none=False, load_only=True)
    seconds = ma.fields.Int(load_only=True)
    minutes = ma.fields.Int(load_only=True)
    hours = ma.fields.Int(load_only=True)
    days = ma.fields.Int(load_only=True)
    dayofweek = ma.fields.Int(load_only=True, validate=ma.fields.validate.OneOf(schedule_weekdays))
    at = ma.fields.String(load_only=True)
    to = ma.fields.Int(load_only=True)
    until = ma.fields.String(load_only=True)
    tag = ma.fields.String(load_only=True)
    run_once = ma.fields.Bool(load_default=False, load_only=True)

    def __init__(self, *args, do_map: dict[str, Callable], **kwargs):
        self.do_map = do_map
        super().__init__(*args, **kwargs)

    def data2job(self, data: dict, **kwargs):
        """
        !!! It does not initialize `do` and `scheduler` attributes
        But all other will be checked and initialized.

        :param data:
        :param kwargs:
        :return: ScheduleJob validated and prepared instance
        """

        errors = {}
        job = self.__model__(data.pop('interval'))
        do_name = data.pop('do')
        if not isinstance(self.do_map.get(do_name), Callable):
            errors['do'] = f"Value '{do_name}' is not valid. Available values are {[*self.do_map.keys()]}"
        else:
            job.do_name = do_name

        # Job has no run_once attribute. Remove it before preparation.
        job.run_once = data.pop('run_once')

        for fname, v in data.items():
            try:
                attr = getattr(job, fname)  # if this property it (as side effect) will set a right value of job.unit
                if attr is not job and isinstance(attr, Callable):
                    attr(v)
                else:
                    # redefine interval for keys like minutes, days .... last be winner
                    job.interval = v

            except Exception as exc:
                if isinstance(exc, (AttributeError, KeyError, ScheduleValueError)):
                    errors[fname] = str(exc)
                else:
                    raise exc
        if errors:
            raise ma.exceptions.ValidationError(errors)
        return job

    @ma.post_load
    def make_object(self, data, **kwargs):
        return self.data2job(data, **kwargs)


def load_jobs(env: Env, do_map: dict[str, Callable], scheduler: Scheduler = None):
    """
    Loads Job-s from environment to schedules
    :param env: Env to get env.dict('SCHEDTAB_NN')
    :param do_map: dict mapping the environment job 'do' name to a Callable
    :param scheduler:
    :return Scheduler: new or passed
    """
    vname = 'SCHEDTAB_'
    if not scheduler:
        scheduler = Scheduler()

    for tab_name in (k for k in os.environ if k.startswith(vname)):
        job: Job = ScheduleJobSchema(do_map=do_map).load(env.dict(tab_name))
        func = do_map[job.do_name]
        if job.run_once:
            func = run_once(func)
        job.scheduler = scheduler
        job.do(func)

    return scheduler
