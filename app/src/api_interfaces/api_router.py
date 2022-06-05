from fastapi import APIRouter


class AppRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self._jwt_secret = None
        self._user = None

    @property
    def jwt_secret(self):
        return self._jwt_secret

    @jwt_secret.setter
    def jwt_secret(self, jwt_secret):
        self._jwt_secret = jwt_secret

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        self._user = user
