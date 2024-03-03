import datetime
import functools
import os
import time
from pathlib import Path
from typing import Callable

import requests

from app.helpers.decorators import log
from app.scrappers.ria_used_cars import page_item_parser, ItemInfo
from app.db import DBUtils
from app.helpers.env import prefixed_env_to_dict, load_jobs
from app import env, Env, logger


class Executor:
    env_scrapper = 'SCRAPPER'
    env_schedule = 'SCHEDULE'
    env_settings = {
        env_scrapper: [
            ('ROOT_URL', Env.url), 'URL_PAGE_PARM_NAME', ('PAGE_START', Env.int),
            ('PAGE_END', Env.int), ('SLEEP_AFTER_REQUEST', Env.float)
        ],
        env_schedule: ['TIME_START', ('ONCE', Env.bool)]
    }

    def __init__(self, env: Env, db: DBUtils = None):
        self.env = env
        self._db = db

    @property
    def publish_map(self) -> dict[str, Callable]:
        return {
            'scrap': self.main,
            'dump': self.db.dump,
            'to_csv': self.db.to_csv
        }

    @functools.cached_property
    def db(self):
        return DBUtils(self.env)

    def scrap(self):
        opts = prefixed_env_to_dict(self.env, self.env_scrapper, self.env_settings[self.env_scrapper])
        s = requests.Session()

        page, page_end, page_param_name = opts['page_start'], opts['page_end'], opts['url_page_parm_name']
        sleep_after_request = opts['sleep_after_request']

        url_params = {page_param_name: page}
        while page <= page_end:
            try:
                items_url = page_item_parser(opts['root_url'].geturl(), s, url_params)
                if not items_url:
                    break
            except ValueError as exc:
                break
            else:
                for url in items_url:
                    item_info = ItemInfo(url, s)
                    self.db.update_or_insert(item_info.as_dict)

                page += 1
                url_params[page_param_name] = page
                time.sleep(sleep_after_request)

    def main(self):
        base_dir = Path(__file__).parent.parent
        os.chdir(base_dir)
        pid_file_name = self.env('PIDFILE')
        pid_file_path: Path = base_dir / pid_file_name
        if pid_file_path.is_file():
            raise SystemExit(f'Other instance is already running. {pid_file_path} file exists')

        self.db.dump()
        self.db.to_csv()

        try:
            with open(pid_file_path, 'w') as f:
                f.write(f'{os.getpid()}')
                self.scrap()

        finally:
            pid_file_path.unlink(missing_ok=True)

    def main_forever(self):
        ctime = datetime.datetime.now()
        opts = prefixed_env_to_dict(self.env, self.env_schedule, self.env_settings[self.env_schedule])
        try:
            stime = datetime.time.fromisoformat(opts.get('time_start'))
        except ValueError:
            stime = ctime
        else:
            stime = ctime.replace(hour=stime.hour, minute=stime.minute, second=stime.second, microsecond=0)

        if ctime < stime:
            time.sleep((stime - ctime).seconds)
        once = opts.get('once', True)
        while True:
            self.main()
            if once:
                break
            stime += datetime.timedelta(seconds=86400)
            time.sleep((stime - datetime.datetime.now()).seconds)

    def execute(self):
        do_map = {
            'dump': log(self.db.dump),
            'to_csv': log(self.db.to_csv),
            'scrap': log(self.scrap),
            'alive': log(functools.partial(logger.debug, f'I am alive'))
        }
        scheduler = load_jobs(env, do_map)

        logger.info('Starting')
        i, l_jobs = 0, len(scheduler.jobs)
        while now_dt := scheduler.get_next_run():
            cl_jobs = len(scheduler.jobs)
            if i == 0 or cl_jobs != l_jobs:
                for j, job in enumerate(scheduler.jobs):
                    logger.info(f'\tActive job#{j}#{job}')
                l_jobs = cl_jobs

            logger.debug(f'iteration#{i}#Next run at {now_dt}#before [run_pending]')
            scheduler.run_pending()
            logger.debug(f'jobs#{cl_jobs}#{scheduler.jobs}#after [run_pending]')

            now_dt, next_dt = datetime.datetime.now(), scheduler.next_run
            if next_dt is None:
                break

            ssec = round(next_dt.timestamp() - now_dt.timestamp(), 3)
            if ssec < 0:
                logger.warning(f'Next run [{next_dt}] less [{now_dt}]')
            ssec = max(ssec, 0)
            logger.debug(f'sleep#{ssec}sec#after [run_pending]')
            time.sleep(ssec)
            i += 1
