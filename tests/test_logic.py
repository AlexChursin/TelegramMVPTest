import pytest
from backend import back_api
from telegram.main_logic_bot.client_repo.client_entity import Client

doc_token = '9076fd887d83d240cb648e13b5d191f1'


@pytest.mark.asyncio
async def test_get_list_free_days():
    r = back_api.get_list_free_days(doc_token)
    assert '2day' in r
    assert '2morrow' in r


@pytest.mark.asyncio
async def test_get_doctor_from_refer():
    r = await back_api.get_doctor(doc_token)
    assert len(r.split()) == 2


@pytest.mark.asyncio
async def test_get_list_times():
    r = back_api.get_list_free_times(day='2day', doc_token=doc_token)
    assert len(r) == 2
    assert r[0].id == 1
    r = back_api.get_list_free_times(day='2morrow', doc_token=doc_token)
    assert len(r) == 0


@pytest.mark.asyncio
async def test_create_dialog():
    client = Client(doctor_name='Doctor nameTest', doc_token=doc_token)
    client.consulate.schedule_id = 1
    client.consulate.age = 22
    client.consulate.number = '89012334411'
    client.consulate.name_otch = 'Vladimir Test'
    client.consulate.reason_petition = 'Reason Test'
    dialog_id = await back_api.create_dialog(chat_id=1, client=client)
    assert dialog_id is not None
