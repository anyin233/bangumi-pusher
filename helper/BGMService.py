from enum import Enum
import time
import logging
from pprint import pprint
import requests

from helper.BGMClient import generate_headers, Client

api_base_url = "https://api.bgm.tv"


class SubjectType(Enum):
    BOOK = 1
    ANIME = 2
    MUSIC = 3
    GAME = 4
    OTHER = 6


class CollectionType(Enum):
    WANT = 1
    WATCHED = 2
    IN_PROGRESS = 3
    PUT_ASIDE = 4
    ABANDON = 5

class EpType(Enum):
    NORMAL = 0
    SP = 1
    OP = 2
    ED = 3
    AD = 4
    MAD = 5
    OTHERS = 6


# use client which init by oauth to start services
class BGMService:
    def __init__(self, client):
        assert isinstance(client, Client)
        self.client = client
        self.set_user_info()
        self.logger = logging.getLogger(str(self.__class__))

    def set_user_info(self):
        '''
        设置用户信息，当username有效时设置为username，否则为uid
        '''
        endpoint = "/v0/me"
        headers = generate_headers(
            logged=True, access_token=self.client.get_token())
        r = requests.get(
            api_base_url + endpoint,
            headers=headers
        )

        if r.status_code == 200:
            content = r.json()
            try:
                self.uid = content['username']
            except:
                self.uid = str(content['id'])
        elif r.status_code == 403:
            raise RuntimeError("User unauthorized, please auth first")
        else:
            raise RuntimeError("Unknown Error")

    def get_user_collect_list(self, subject: SubjectType = SubjectType.ANIME, collection: CollectionType = CollectionType.IN_PROGRESS):
        '''
        获取用户的收藏信息
        Args:
            subject: type is SubjectType, default value is SubjectType.ANIME, figure out which type of content you want to get
            collection: type is CollectionType, default value is CollectionType.IN_PROGRESS, figure out which status of your content will be shown
        Return:
            A json object which contains a list of valid contents
        Raise:
            RuntimeError: when get error code from bgm.tv service
        '''
        endpoint = "/v0/users/{}/collections".format(self.uid)
        headers = generate_headers(
            logged=True, access_token=self.client.get_token())
        payload = {
            "username": self.uid,
            "subject_type": subject.value,
            "type": collection.value
        }
        r = requests.get(
            api_base_url + endpoint,
            headers=headers,
            params=payload
        )

        if r.status_code == 200:
            return r.json()
        elif r.status_code == 400:
            self.logger.error("Validation Error")
            return {"data": []}
        elif r.status_code == 404:
            self.logger.error("No user")
            return {"data": []}
        
        
    def get_subject_name(self, subject_id):
        endpoint = "/v0/subjects/" + str(subject_id)
        headers = generate_headers(
            logged=True, access_token=self.client.get_token()
        )
        r = requests.get(
            api_base_url + endpoint,
            headers=headers,
        )

        if r.status_code == 200:
            content = r.json()
            try:
                return content['name_cn']
            except:
                return content['name']
            

    
    def get_ep_info(self, subject_id, limit:int = 100, offset:int = 0, type: EpType = EpType.NORMAL):
        endpoint = "/v0/episodes"
        headers = generate_headers(
            logged=True, access_token=self.client.get_token()
        )
        payload = {
            "subject_id": subject_id,
            "type": type.value,
            "limit": limit,
            "offset": offset
        }
        r = requests.get(
            api_base_url + endpoint,
            headers=headers,
            params=payload
        )

        if r.status_code == 200:
            content = r.json()['data']
            ep_list = []
            for ep in content:
                name = ep.get("name_cn", None)
                if name == None:
                    name = ep.get("name", None)
                if not name == None and not name == "":
                    ep_list.append(ep)
            return ep_list
        elif r.status_code == 400:
            self.logger.error("Validation Error")
            return {"data": []}
        elif r.status_code == 404:
            self.logger.error("No user")
            return {"data": []}

    def get_today_eps(self, id):
        ep_list = self.get_ep_info(id)
        if len(ep_list) > 0:
            today = time.strftime("%Y-%m-%d", time.localtime())
            latest_ep = ep_list[len(ep_list) - 1]
            if today == latest_ep['airdate']:
                return latest_ep
            else:
                return None
        return None
            
