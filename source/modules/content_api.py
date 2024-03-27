from datetime import datetime
import jwt
from httpx import AsyncClient
from components.responses.content import UploadFileResponse
from config import JWT_SECRET, CONTENT_API_URL


class ContentApi:
    access_token: str
    headers: dict

    def __init__(self, user_id: str):
        ts_now = datetime.now().timestamp()
        jwt_data = {'id': user_id,
                    'role': 'Admin',
                    'iat': ts_now,
                    'exp': ts_now + 10  # Токен будет жить 10 секунд, для разовых операций
                    }
        self.access_token = jwt.encode(payload=jwt_data, key=JWT_SECRET)
        self.headers = {'Authorization': f'Bearer {self.access_token}'}

    async def upload(self, data: bytes, file_name: str) -> UploadFileResponse:
        """
        Метод для загрузки файла в байтах в файловую систему контентого мс.
        :param data: данные файла
        :param file_name: имя файла с расширением
        :return: ответ от контентного мс UploadFileResponse
        """

        async with AsyncClient(verify=True) as async_session:
            response = await async_session.post(
                url=CONTENT_API_URL + "/upload",
                files={'file': (file_name, data, 'application/xlsx')},
                headers=self.headers
            )
            return UploadFileResponse.from_dict(response.json())

    async def delete(self, file_url: str) -> None:
        """
        Метод для удаления файла из файловой системы контентого мс.
        :param file_url: ссылка на файл
        """

        async with AsyncClient(verify=True) as async_session:
            response = await async_session.delete(
                url=file_url,
                headers=self.headers
            )

            if response.status_code != 200:
                raise Exception(f"Ошибка при удалении: {response.text}")
