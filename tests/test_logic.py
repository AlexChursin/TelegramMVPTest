import pytest
from backend_api import back_api
from messenger_api import mess_api
from telegram.main_logic_bot.client_repo.client_entity import Client
from telegram.main_logic_bot.client_repo.client_provider import APIClientRepo
from telegram.main_logic_bot.client_repo.user_bot_state import State
from telegram.main_logic_bot.utils import get_cons_token

doc_token = '9076fd887d83d240cb648e13b5d191f1'


@pytest.mark.asyncio
async def test_get_list_free_days():
    r =  await  back_api.get_list_free_days(doc_token)
    assert '2day' in r
    assert '2morrow' in r


@pytest.mark.asyncio
async def test_get_doctor_from_refer():
    r = await back_api.get_doctor_name(doc_token)
    assert len(r.split()) == 2


@pytest.mark.asyncio
async def test_set_client():
    doctor_name = 'Александр Владимирович'
    doctor_name_p = await mess_api.get_petrovich(*doctor_name.split())
    client_repo = APIClientRepo()
    client = await client_repo.set_client(user_id=123, chat_id=222)
    assert client is not None
    client.status = State.await_contacts.value
    cons = await client_repo.new_consulate(client.user_id)
    assert cons is not None
    client.consulate = cons
    client = await client_repo.save_client(client)
    assert client is not None
    assert client.status == State.await_contacts.value
    assert client.consulate == cons


@pytest.mark.asyncio
async def test_get_list_times():
    r = get_list_free_times(day='2day', doc_token=doc_token)
    assert len(r) == 2
    assert r[0].id == 1
    r = get_list_free_times(day='2morrow', doc_token=doc_token)
    assert len(r) == 0


@pytest.mark.asyncio
async def test_create_dialog():
    client = Client(doctor_name='Doctor nameTest', doctor_token=doc_token)
    client.consulate.schedule_id = 3
    client.consulate.age = 22
    client.consulate.number = '89012334411'
    client.consulate.name_otch = 'Vladimir Test'
    client.consulate.reason_petition = 'Reason Test'
    dialog_id = await back_api.set_client(chat_id=1, client=client)
    assert dialog_id is not None


def test_get_refer():
    query_token = 'lfhd12jkduqwuihquxcmoewkf21312heuhhiudui'
    res, token = get_cons_token(f'/start doc_{query_token}')
    assert res is TokenResult.doctor
    assert token == query_token

    res, token = get_cons_token(f'/start cons_{query_token}')
    assert res is TokenResult.consulate
    assert token == query_token

    res, token = get_cons_token(f'/start xxx')
    assert res is TokenResult.none
    assert token is None
