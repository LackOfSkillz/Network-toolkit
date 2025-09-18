import pytest
from backend.src.models.network_device import NetworkDevice
from backend.src.models.topology import TopologyLink


@pytest.mark.asyncio
async def test_accept_creates_device_and_link_inherits_config_and_enable(db_session, client):
    # create parent device using the provided session
    parent = NetworkDevice(name='parent', ip_address='192.0.2.1', mac_address='aa:bb:cc:00:00:01', enable_lldp=1, configuration_id=123)
    db_session.add(parent)
    db_session.commit()
    db_session.refresh(parent)

    # use client fixture to call API
    payload = { 'neighbor': { 'remote_mgmt_ips': ['198.51.100.5'], 'remote_chassis_id': '00:11:22:33:44:55', 'remote_sys_name': 'leaf-1' } }
    resp = await client.post(f"/lldp/devices/{parent.id}/neighbors/accept", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body.get('accepted') is True
    assert body.get('created') is True
    new_dev_id = body.get('device_id')

    # verify device created and inherited fields
    created = db_session.query(NetworkDevice).filter(NetworkDevice.id == new_dev_id).first()
    assert created is not None
    assert created.enable_lldp == parent.enable_lldp
    assert created.configuration_id == parent.configuration_id

    # verify topology link
    link = db_session.query(TopologyLink).filter(TopologyLink.source_device_id == parent.id, TopologyLink.target_device_id == created.id).first()
    assert link is not None


@pytest.mark.asyncio
async def test_accept_dedup_by_mgmt_ip(db_session, client):
    # parent
    parent = NetworkDevice(name='parent2', ip_address='192.0.2.2', mac_address='aa:bb:cc:00:00:02', enable_lldp=1)
    db_session.add(parent)
    db_session.commit()
    db_session.refresh(parent)

    # existing device that should match by mgmt ip
    existing = NetworkDevice(name='existing', ip_address='198.51.100.9', mac_address='00:aa:bb:cc:dd:01')
    db_session.add(existing)
    db_session.commit()
    db_session.refresh(existing)

    payload = { 'neighbor': { 'remote_mgmt_ips': ['198.51.100.9'], 'remote_chassis_id': '11:22:33:44:55:66', 'remote_sys_name': 'leaf-2' } }
    resp = await client.post(f"/lldp/devices/{parent.id}/neighbors/accept", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body.get('accepted') is True
    assert body.get('created') is False
    assert body.get('device_id') == existing.id


@pytest.mark.asyncio
async def test_accept_dedup_by_chassis(db_session, client):
    parent = NetworkDevice(name='parent3', ip_address='192.0.2.3', mac_address='aa:bb:cc:00:00:03', enable_lldp=0)
    db_session.add(parent)
    db_session.commit()
    db_session.refresh(parent)

    existing = NetworkDevice(name='existing2', ip_address='203.0.113.5', mac_address='77:88:99:aa:bb:cc')
    db_session.add(existing)
    db_session.commit()
    db_session.refresh(existing)

    payload = { 'neighbor': { 'remote_mgmt_ips': [], 'remote_chassis_id': '77:88:99:aa:bb:cc', 'remote_sys_name': 'leaf-3' } }
    resp = await client.post(f"/lldp/devices/{parent.id}/neighbors/accept", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body.get('accepted') is True
    assert body.get('created') is False
    assert body.get('device_id') == existing.id
