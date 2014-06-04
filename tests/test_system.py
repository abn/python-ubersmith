import datetime
from decimal import Decimal
import json

from mock import Mock
import pytest

import ubersmith
import ubersmith.api
import ubersmith.order


def setup_module():
    ubersmith.init(**{
        'base_url': '',
        'username': '',
        'password': '',
    })


def teardown_module():
    ubersmith.api._DEFAULT_REQUEST_HANDLER = None


@pytest.fixture
def requests(monkeypatch):
    requests = Mock()
    monkeypatch.setattr(ubersmith.api, 'requests', requests)
    return requests


@pytest.fixture
def response(requests):
    response = Mock()
    response.headers = {
        'content-type': 'application/json',
    }
    response.text = u""
    requests.post.return_value = response
    return response


def test_invoice_list(response):
    response.text = json.dumps({
        "status": True,
        "error_code": None,
        "error_message": "",
        "data": {
            "60": {
                u'invid': u'60',
                u'clientid': u'50',
                u'amount': u'50.00',
                u'amount_unpaid': u'0.00',
                u'date': u'1272400333',
                u'datepaid': u'1272400333',
                u'due': u'1274414400',
            },
        },
    })
    # TODO: add cleaners to this call
    # TODO: make this a group call
    expected = {
        u'60': {
            u'invid': u'60',
            u'clientid': u'50',
            u'amount': u'50.00',
            u'amount_unpaid': u'0.00',
            u'date': u'1272400333',
            u'datepaid': u'1272400333',
            u'due': u'1274414400',
        }
    }
    assert ubersmith.client.invoice_list(client_id=50) == expected


# TODO: need to handle pdf files based on content type header (merge in 0.2.5)
@pytest.mark.xfail
def test_invoice_get_pdf(response):
    response.headers = {
        'content-type': 'application/pdf',
        'content-disposition': 'inline; filename=Invoice-60.pdf'
    }
    response.text = u"Some PDF data."
    response.content = str(response.text)
    uberfile = ubersmith.client.invoice_get(invoice_id=60, format="pdf")
    assert uberfile.type == 'application/pdf'
    assert uberfile.filename == "Invoice-60.pdf"
    assert str(uberfile.data) == response.text


def test_uber_documentation(response):
    response.headers = {
        'content-type': 'application/pdf',
        'content-disposition': 'inline; filename="doc.pdf";'
    }
    response.text = u"Some PDF data."
    response.content = str(response.text)
    uberfile = ubersmith.uber.documentation()
    assert uberfile.type == 'application/pdf'
    assert uberfile.filename == "doc.pdf"
    assert str(uberfile.data) == response.text


def test_order_list(response):
    response.text = json.dumps({
        "status": True,
        "error_code": None,
        "error_message": "",
        "data": {
            "60": {
                "order_id": "60",
                "client_id": "50",
                "activity": "1272400333",
                "ts": "1272400333",
                "total": "33.22",
            },
        },
    })
    expected = {
        60: {
            u'client_id': 50,
            u'activity': datetime.datetime.fromtimestamp(float("1272400333")),
            u'ts': datetime.datetime.fromtimestamp(float("1272400333")),
            u'total': Decimal('33.22'),
            u'order_id': 60,
        }
    }
    assert ubersmith.order.list(client_id=50) == expected