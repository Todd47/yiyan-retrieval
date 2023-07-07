from typing import List, Optional
import os

from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens
import requests
import json
import constants


class YiyanLLM(LLM):
    max_token: int = 10000
    # temperature: float = 0.1
    temperature: float = 0.95
    top_p = 0.9
    history = []

    def __init__(self):
        super().__init__()

    @property
    def _llm_type(self) -> str:
        return "YiyanLLM"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        access_token = self.get_access_token()

        # headers中添加上content-type这个参数，指定为json格式
        headers = {'Content-Type': 'application/json'}
        data = {
            'prompt': prompt,
            'temperature': self.temperature,
            'history': self.history,
            'max_length': self.max_token
        }

        with open('WRITER/data.json', 'w') as file:
            json.dump(data, file, indent=4)

        data_yiyan = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature
        }

        with open('WRITER/yiyan_data.json', 'w') as file:
            json.dump(data_yiyan, file, indent=4)

        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + access_token
        # 调用api
        payload = json.dumps(data_yiyan)
        response = requests.post(url, headers=headers, data=payload)

        response_dict = json.loads(response.text)
        with open('WRITER/response_data.json', 'w') as file:
            json.dump(response_dict, file, indent=4)

        return response_dict["result"]

        # if response.status_code != 200:
        #     return "查询结果错误"
        # resp = response.json()
        # if stop is not None:
        #     response = enforce_stop_tokens(response, stop)
        # self.history = self.history + [[None, resp['response']]]
        #
        #
        # return resp['response']

    def get_access_token(self):
        file_path = "token.json"

        if os.path.exists(file_path):
            # 存在token.json文件
            with open(file_path, "r") as file:
                data = json.load(file)
            access_token = data.get("token")
            return access_token
        else:
            # 无token.json文件
            url = "https://aip.baidubce.com/oauth/2.0/token"
            params = {"grant_type": "client_credentials", "client_id": constants.api_key,
                      "client_secret": constants.secret_key}
            response = requests.post(url, params=params)
            access_token = response.json().get("access_token")
            # print(response.json())
            data = {
                "token": access_token
            }
            with open("token.json", "w") as file:
                json.dump(data, file)
            return access_token

# if __name__ == '__main__':
#     import requests
#
#     D = {"prompt": "", "history": []}
#     D["prompt"] = " 感冒发烧怎么引起的?"
#     print(D)
#     data = requests.post("http://127.0.0.1:8000", json=D, headers={"Content-Type": "application/json"})
#     print(data.text)
