

#  Copyright 2017-2018 Luiz Augusto Alves Ferraz
#  .
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  .
#      http://www.apache.org/licenses/LICENSE-2.0
#  .
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json
import os

import easygoogle

__local__ = os.path.dirname(os.path.abspath(__file__))

MOCKED_APIS = json.load(open(os.path.join(__local__, 'data', 'apis.json')))

SCOPES = ['scope.unique', 'scope.multiple']
RESULT_SCOPES = [
    "https://testscopes.exemple.org/auth/scope.multiple",
    "https://testscopes.exemple.org/auth/scope.unique"
]


def test_inheritance():
    assert issubclass(easygoogle.oauth2, easygoogle._api_builder)


def test_creation_call(mocker, tmpdir):
    mocker.patch.dict('easygoogle.registeredApis', values=MOCKED_APIS)
    mocker.patch('easygoogle.InstalledAppFlow')
    mocker.patch('easygoogle.google')
    mocker.patch('easygoogle.os.path.isfile', return_value=False)
    mocker.patch('easygoogle.json')
    open_mock = mocker.mock_open()
    mocker.patch('easygoogle.open', open_mock, create=True)
    easygoogle.six.string_types = (type(mocker.sentinel.json_file),)

    model_spec = {
        'refresh_token': 'credentials.refresh_token',
        'client_id': 'credentials.client_id',
        'client_secret': 'credentials.client_secret',
        'token_uri': 'credentials.token_uri',
        'id_token': 'credentials.id_token',
        'scopes': ['list(credentials.scopes)']
    }

    credentials_mock = mocker.MagicMock()
    credentials_mock.configure_mock(**model_spec)
    easygoogle.InstalledAppFlow.from_client_secrets_file.return_value = (
        easygoogle.InstalledAppFlow())
    easygoogle.InstalledAppFlow().run_local_server.return_value = (
        credentials_mock)

    oauth = easygoogle.oauth2(
        mocker.sentinel.json_file, ['scope.unique'],
        user="testuser",
        app_dir=str(tmpdir.dirpath()))

    easygoogle.InstalledAppFlow.from_client_secrets_file.assert_called_once_with(
        mocker.sentinel.json_file,
        scopes=["https://testscopes.exemple.org/auth/scope.unique"])

    open_mock.assert_called_once_with(
        str(
            tmpdir.dirpath('.credentials',
                           'google_client_library_-_python#testuser.json')),
        'w')
    easygoogle.json.dump.assert_called_once_with(model_spec, open_mock())

    credentials_mock.refresh.assert_called_once_with(
        easygoogle.google.auth.transport.requests.Request())

    assert oauth.credentials is credentials_mock


def test_creation_from_default(mocker):
    mocker.patch.dict('easygoogle.registeredApis', values=MOCKED_APIS)
    mocker.patch('easygoogle.google')

    easygoogle.google.auth.default.return_value = (
        mocker.sentinel.credentials, mocker.sentinel.project)

    oauth = easygoogle.oauth2(None, ['scope.unique'])

    assert oauth.credentials is mocker.sentinel.credentials
