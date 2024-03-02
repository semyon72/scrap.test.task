import os
from typing import Callable, Union, Mapping

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


class ScheduleTabItem(ma.Schema):
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

    def data2job(self, data: dict, **kwargs):
        errors = {}
        job = self.__model__(data.pop('interval'))
        job._do_name = data.pop('do')
        job._run_once = data.pop('run_once')

        for fn, v in data.items():
            try:
                attr = getattr(job, fn)  # if this property it (as side effect) will set a right value of job.unit
                if attr is not job and isinstance(attr, Callable):
                    attr(v)
                else:
                    # redefine interval for keys like minutes, days .... last be winner
                    job.interval = v

            except Exception as exc:
                if isinstance(exc, (AttributeError, KeyError, ScheduleValueError)):
                    errors[fn] = str(exc)
                else:
                    raise exc
        if errors:
            raise ma.exceptions.ValidationError(errors)
        return job

    @ma.post_load
    def make_object(self, data, **kwargs):
        return self.data2job(data, **kwargs)


def load_jobs(env: Env, obj: Union[object, dict], scheduler: Scheduler = None):
    """
    Loads Job-s from environment to schedules
    :param env: Env to get env.dict('SCHEDTAB_NN')
    :param obj: class or object where the functions or methods will be looking
    :param scheduler:
    :return Scheduler: new or passed
    """
    vname = 'SCHEDTAB_'
    if not scheduler:
        scheduler = Scheduler()

    def find_callable(fn_name: str, obj: Union[object, Mapping]) -> Callable:
        parts = fn_name.split('.')

        dparts = [p for p in parts if p.startswith('_')]
        if dparts:
            raise ValueError(f'protected and private attributes forbidden {dparts}')

        lparts = len(parts)
        if not lparts:
            if isinstance(obj, Callable):
                return obj
            else:
                raise ValueError(f'`fn_name` is empty but `obj` is not Callable')

        if isinstance(obj, Mapping):
            if lparts < 2:
                raise ValueError(
                    f'`obj` is Mapping but fn_name is not dot separated. Try pass "key_in_obj.{parts[0]}"'
                )
            # get object by key
            obj = obj[parts.pop(0)]

        fn = obj
        for attr in parts:
            fn = getattr(fn, attr)

        if not isinstance(fn, Callable):
            raise ValueError(
                f'`{fn_name}` attribute of `obj` isn\'t Callable.'
            )
        return fn

    for tab_name in (k for k in os.environ if k.startswith(vname)):
        job: Job = ScheduleTabItem().load(env.dict(tab_name))
        fn = find_callable(job._do_name, obj)
        if job._run_once:
            fn = run_once(fn)
        job.scheduler = scheduler
        job.do(fn)

    return scheduler
