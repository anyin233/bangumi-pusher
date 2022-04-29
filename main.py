import logging

from fastapi import FastAPI
from helper.BGMClient import build_authorization_url, client
from helper.BGMService import BGMService
from utils import get_subject_id_list
from pypushdeer import PushDeer
from config import PUSH_KEY, CLIENT_ID
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

app = FastAPI()
deer = PushDeer(pushkey=PUSH_KEY)

print(build_authorization_url(CLIENT_ID))

scheduler = BackgroundScheduler()  # add a scheduler to execute push service automatically
jobs = []

logger = logging.getLogger(__name__)


def background_task():
    # create service node
    deer.send_text("开始获取今日番剧 (*ﾟ∀ﾟ*)")
    global scheduler
    client.refresh()
    service = BGMService(client)

    service.set_user_info()
    data = service.get_user_collect_list()['data']

    # set in_progress bangumi ids
    in_progress_ids = get_subject_id_list(data)

    any_bangumi = False
    for bid in in_progress_ids:
        name = service.get_subject_name(bid)
        latest = service.get_today_eps(bid)
        if latest is not None:
            any_bangumi = True
            deer.send_text("今日更新番剧：{}".format(name), desp="剧集名称: {}".format(latest['name_cn']))
    if not any_bangumi:
        deer.send_text("今天没有番剧更新哦 (|||ﾟдﾟ)")


@app.get("/callback")
def create_client(code: str):
    status = client.auth(code)
    new_job = scheduler.add_job(background_task, 'interval', minutes=1)
    jobs.append(new_job)
    scheduler.start()
    return {"status": status}


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
