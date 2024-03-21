from datetime import datetime
import jwt
from httpx import AsyncClient
from components.responses.rpc import RpcResponse
from config import JWT_SECRET, CONTENT_API_URL


class ContentApi:
    access_token: str
    headers: dict

    def __init__(self, user_id: str):
        ts_now = datetime.now().timestamp()
        jwt_data = {'id': user_id,
                    'role': 'Admin',
                    'iat': ts_now,
                    'exp': ts_now + 10 # Токен будет жить 10 секунд, для разовых операций
                    }
        self.access_token = jwt.encode(payload=jwt_data, key=JWT_SECRET)
        self.headers = {'Authorization': f'Bearer {self.access_token}'}

    async def upload(self, data: bytes, file_name: str) -> RpcResponse:
        async with AsyncClient(verify=True) as async_session:
            response = await async_session.post(
                url=CONTENT_API_URL + "/files/upload",
                files={'file': (file_name, data, 'application/xlsx')},
                headers=self.headers
            )
        return RpcResponse.from_json(response.json())
