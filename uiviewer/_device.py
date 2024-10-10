# -*- coding: utf-8 -*-

import abc
import tempfile
from typing import List, Dict, Union, Tuple, Optional
from functools import cached_property  # python3.8+

from PIL import Image
from requests import request
import tidevice
import adbutils
import wda
import uiautomator2 as u2
from hmdriver2 import hdc
from fastapi import HTTPException

from uiviewer._utils import file2base64, image2base64
from uiviewer._models import Platform, BaseHierarchy
from uiviewer.parser import android_hierarchy, ios_hierarchy, harmony_hierarchy


def list_serials(platform: str) -> List[str]:
    devices = []
    if platform == Platform.ANDROID:
        raws = adbutils.AdbClient().device_list()
        devices = [item.serial for item in raws]
    elif platform == Platform.IOS:
        raw = tidevice.Usbmux().device_list()
        devices = [d.udid for d in raw]
    else:
        devices = hdc.list_devices()

    return devices


class DeviceMeta(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def take_screenshot(self) -> str:
        pass

    def dump_hierarchy(self) -> Dict:
        pass


class HarmonyDevice(DeviceMeta):
    def __init__(self, serial: str):
        self.serial = serial
        self.hdc = hdc.HdcWrapper(serial)

    @cached_property
    def _display_size(self) -> Tuple:
        return self.hdc.display_size()

    def take_screenshot(self) -> str:
        with tempfile.NamedTemporaryFile(delete=True, suffix=".png") as f:
            path = f.name
            self.hdc.screenshot(path)
            return file2base64(path)

    def dump_hierarchy(self) -> BaseHierarchy:
        packageName, pageName = self.hdc.current_app()
        raw: Dict = self.hdc.dump_hierarchy()
        hierarchy: Dict = harmony_hierarchy.convert_harmony_hierarchy(raw)
        return BaseHierarchy(
            jsonHierarchy=hierarchy,
            activityName=pageName,
            packageName=packageName,
            windowSize=self._display_size,
            scale=1
        )


class AndroidDevice(DeviceMeta):
    def __init__(self, serial: str):
        self.serial = serial
        self.d: u2.Device = u2.connect(serial)

    @cached_property
    def _window_size(self) -> Tuple:
        return self.d.window_size()

    def take_screenshot(self) -> str:
        img: Image.Image = self.d.screenshot()
        return image2base64(img)

    def dump_hierarchy(self) -> BaseHierarchy:
        current = self.d.app_current()
        page_xml = self.d.dump_hierarchy()
        page_json = android_hierarchy.convert_android_hierarchy(page_xml)
        return BaseHierarchy(
            jsonHierarchy=page_json,
            activityName=current['activity'],
            packageName=current['package'],
            windowSize=self._window_size,
            scale=1
        )


class IosDevice(DeviceMeta):
    def __init__(self, udid: str, wda_url: str, max_depth: int) -> None:
        self.udid = udid
        self.wda_url = wda_url
        self._max_depth = max_depth
        self.client = wda.Client(wda_url)

    @property
    def max_depth(self) -> int:
        return int(self._max_depth) if self._max_depth else 30

    @cached_property
    def scale(self) -> int:
        return self.client.scale

    @cached_property
    def _window_size(self) -> Tuple:
        return self.client.window_size()

    def _check_wda_health(self) -> bool:
        resp = request("GET", f"{self.wda_url}/status", timeout=5).json()
        state = resp.get("value", {}).get("state")
        return state == "success"

    def take_screenshot(self) -> str:
        img: Image.Image = self.client.screenshot()
        return image2base64(img)

    def _current_bundle_id(self) -> str:
        resp = request("GET", f"{self.wda_url}/wda/activeAppInfo", timeout=10).json()
        bundleId = resp.get("value", {}).get("bundleId", None)
        return bundleId

    def dump_hierarchy(self) -> BaseHierarchy:
        self.client.appium_settings({"snapshotMaxDepth": self.max_depth})
        data: Dict = self.client.source(format="json")
        hierarchy: Dict = ios_hierarchy.convert_ios_hierarchy(data, self.scale)
        return BaseHierarchy(
            jsonHierarchy=hierarchy,
            activityName=None,
            packageName=self._current_bundle_id(),
            windowSize=self._window_size,
            scale=self.scale
        )


def get_device(platform: str, serial: str, wda_url: str, max_depth: int) -> Union[HarmonyDevice, AndroidDevice, IosDevice]:
    if platform == Platform.HARMONY:
        return HarmonyDevice(serial)
    elif platform == Platform.ANDROID:
        return AndroidDevice(serial)
    else:
        return IosDevice(serial, wda_url, max_depth)


# Global cache for devices
cached_devices = {}


def init_device(platform: str, serial: str, wda_url: str, max_depth: int):

    if serial not in list_serials(platform):
        raise HTTPException(status_code=500, detail=f"Device<{serial}> not found")

    try:
        device: Union[HarmonyDevice, AndroidDevice] = get_device(platform, serial, wda_url, max_depth)
        cached_devices[(platform, serial)] = device

        if isinstance(device, IosDevice):
            return device._check_wda_health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return True