# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import json
from unittest.mock import patch

import pytest
from flask_appbuilder.security.sqla.models import User
from sqlalchemy.orm import Session

from superset.dashboards.commands.exceptions import DashboardAccessDeniedError
from superset.extensions import cache_manager
from superset.key_value.commands.entry import Entry
from superset.key_value.utils import cache_key
from superset.models.dashboard import Dashboard
from tests.integration_tests.base_tests import login
from tests.integration_tests.fixtures.world_bank_dashboard import (
    load_world_bank_dashboard_with_slices,
    load_world_bank_data,
)
from tests.integration_tests.test_app import app

key = "test-key"
value = "test"


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def dashboard_id(load_world_bank_dashboard_with_slices) -> int:
    with app.app_context() as ctx:
        session: Session = ctx.app.appbuilder.get_session
        dashboard = session.query(Dashboard).filter_by(slug="world_health").one()
        return dashboard.id


@pytest.fixture
def admin_id() -> int:
    with app.app_context() as ctx:
        session: Session = ctx.app.appbuilder.get_session
        admin = session.query(User).filter_by(username="admin").one_or_none()
        return admin.id


@pytest.fixture(autouse=True)
def cache(dashboard_id, admin_id):
    entry: Entry = {"owner": admin_id, "value": value}
    cache_manager.filter_state_cache.set(cache_key(dashboard_id, key), entry)


def test_post(client, dashboard_id: int):
    login(client, "admin")
    payload = {
        "value": value,
    }
    resp = client.post(f"api/v1/dashboard/{dashboard_id}/filter_state", json=payload)
    assert resp.status_code == 201


def test_post_bad_request(client, dashboard_id: int):
    login(client, "admin")
    payload = {
        "value": 1234,
    }
    resp = client.post(f"api/v1/dashboard/{dashboard_id}/filter_state", json=payload)
    assert resp.status_code == 400


@patch("superset.security.SupersetSecurityManager.raise_for_dashboard_access")
def test_post_access_denied(mock_raise_for_dashboard_access, client, dashboard_id: int):
    login(client, "admin")
    mock_raise_for_dashboard_access.side_effect = DashboardAccessDeniedError()
    payload = {
        "value": value,
    }
    resp = client.post(f"api/v1/dashboard/{dashboard_id}/filter_state", json=payload)
    assert resp.status_code == 403


def test_post_same_key_for_same_tab_id(client, dashboard_id: int):
    login(client, "admin")
    payload = {
        "value": value,
    }
    resp = client.post(
        f"api/v1/dashboard/{dashboard_id}/filter_state?tab_id=1", json=payload
    )
    data = json.loads(resp.data.decode("utf-8"))
    first_key = data.get("key")
    resp = client.post(
        f"api/v1/dashboard/{dashboard_id}/filter_state?tab_id=1", json=payload
    )
    data = json.loads(resp.data.decode("utf-8"))
    second_key = data.get("key")
    assert first_key == second_key


def test_post_different_key_for_different_tab_id(client, dashboard_id: int):
    login(client, "admin")
    payload = {
        "value": value,
    }
    resp = client.post(
        f"api/v1/dashboard/{dashboard_id}/filter_state?tab_id=1", json=payload
    )
    data = json.loads(resp.data.decode("utf-8"))
    first_key = data.get("key")
    resp = client.post(
        f"api/v1/dashboard/{dashboard_id}/filter_state?tab_id=2", json=payload
    )
    data = json.loads(resp.data.decode("utf-8"))
    second_key = data.get("key")
    assert first_key != second_key


def test_post_different_key_for_no_tab_id(client, dashboard_id: int):
    login(client, "admin")
    payload = {
        "value": value,
    }
    resp = client.post(f"api/v1/dashboard/{dashboard_id}/filter_state", json=payload)
    data = json.loads(resp.data.decode("utf-8"))
    first_key = data.get("key")
    resp = client.post(f"api/v1/dashboard/{dashboard_id}/filter_state", json=payload)
    data = json.loads(resp.data.decode("utf-8"))
    second_key = data.get("key")
    assert first_key != second_key


def test_put(client, dashboard_id: int):
    login(client, "admin")
    payload = {
        "value": "new value",
    }
    resp = client.put(
        f"api/v1/dashboard/{dashboard_id}/filter_state/{key}", json=payload
    )
    assert resp.status_code == 200


def test_put_same_key_for_same_tab_id(client, dashboard_id: int):
    login(client, "admin")
    payload = {
        "value": value,
    }
    resp = client.put(
        f"api/v1/dashboard/{dashboard_id}/filter_state/{key}?tab_id=1", json=payload
    )
    data = json.loads(resp.data.decode("utf-8"))
    first_key = data.get("key")
    resp = client.put(
        f"api/v1/dashboard/{dashboard_id}/filter_state/{key}?tab_id=1", json=payload
    )
    data = json.loads(resp.data.decode("utf-8"))
    second_key = data.get("key")
    assert first_key == second_key


def test_put_different_key_for_different_tab_id(client, dashboard_id: int):
    login(client, "admin")
    payload = {
        "value": value,
    }
    resp = client.put(
        f"api/v1/dashboard/{dashboard_id}/filter_state/{key}?tab_id=1", json=payload
    )
    data = json.loads(resp.data.decode("utf-8"))
    first_key = data.get("key")
    resp = client.put(
        f"api/v1/dashboard/{dashboard_id}/filter_state/{key}?tab_id=2", json=payload
    )
    data = json.loads(resp.data.decode("utf-8"))
    second_key = data.get("key")
    assert first_key != second_key


def test_put_different_key_for_no_tab_id(client, dashboard_id: int):
    login(client, "admin")
    payload = {
        "value": value,
    }
    resp = client.put(
        f"api/v1/dashboard/{dashboard_id}/filter_state/{key}", json=payload
    )
    data = json.loads(resp.data.decode("utf-8"))
    first_key = data.get("key")
    resp = client.put(
        f"api/v1/dashboard/{dashboard_id}/filter_state/{key}", json=payload
    )
    data = json.loads(resp.data.decode("utf-8"))
    second_key = data.get("key")
    assert first_key != second_key


def test_put_bad_request(client, dashboard_id: int):
    login(client, "admin")
    payload = {
        "value": 1234,
    }
    resp = client.put(
        f"api/v1/dashboard/{dashboard_id}/filter_state/{key}", json=payload
    )
    assert resp.status_code == 400


@patch("superset.security.SupersetSecurityManager.raise_for_dashboard_access")
def test_put_access_denied(mock_raise_for_dashboard_access, client, dashboard_id: int):
    login(client, "admin")
    mock_raise_for_dashboard_access.side_effect = DashboardAccessDeniedError()
    payload = {
        "value": "new value",
    }
    resp = client.put(
        f"api/v1/dashboard/{dashboard_id}/filter_state/{key}", json=payload
    )
    assert resp.status_code == 403


def test_put_not_owner(client, dashboard_id: int):
    login(client, "gamma")
    payload = {
        "value": "new value",
    }
    resp = client.put(
        f"api/v1/dashboard/{dashboard_id}/filter_state/{key}", json=payload
    )
    assert resp.status_code == 403


def test_get_key_not_found(client, dashboard_id: int):
    login(client, "admin")
    resp = client.get(f"api/v1/dashboard/{dashboard_id}/filter_state/unknown-key/")
    assert resp.status_code == 404


def test_get_dashboard_not_found(client):
    login(client, "admin")
    resp = client.get(f"api/v1/dashboard/{-1}/filter_state/{key}")
    assert resp.status_code == 404


def test_get(client, dashboard_id: int):
    login(client, "admin")
    resp = client.get(f"api/v1/dashboard/{dashboard_id}/filter_state/{key}")
    assert resp.status_code == 200
    data = json.loads(resp.data.decode("utf-8"))
    assert value == data.get("value")


@patch("superset.security.SupersetSecurityManager.raise_for_dashboard_access")
def test_get_access_denied(mock_raise_for_dashboard_access, client, dashboard_id):
    login(client, "admin")
    mock_raise_for_dashboard_access.side_effect = DashboardAccessDeniedError()
    resp = client.get(f"api/v1/dashboard/{dashboard_id}/filter_state/{key}")
    assert resp.status_code == 403


def test_delete(client, dashboard_id: int):
    login(client, "admin")
    resp = client.delete(f"api/v1/dashboard/{dashboard_id}/filter_state/{key}")
    assert resp.status_code == 200


@patch("superset.security.SupersetSecurityManager.raise_for_dashboard_access")
def test_delete_access_denied(
    mock_raise_for_dashboard_access, client, dashboard_id: int
):
    login(client, "admin")
    mock_raise_for_dashboard_access.side_effect = DashboardAccessDeniedError()
    resp = client.delete(f"api/v1/dashboard/{dashboard_id}/filter_state/{key}")
    assert resp.status_code == 403


def test_delete_not_owner(client, dashboard_id: int):
    login(client, "gamma")
    resp = client.delete(f"api/v1/dashboard/{dashboard_id}/filter_state/{key}")
    assert resp.status_code == 403
