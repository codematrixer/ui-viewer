# -*- coding: utf-8 -*-

import abc
import tempfile
from typing import List, Dict, Union

from PIL import Image
import adbutils
import uiautomator2 as u2
from hmdriver2 import hdc
from fastapi import HTTPException

from uiviewer._utils import file_to_base64, image_to_base64
from uiviewer._models import Platform, BaseHierarchy
from uiviewer.parser import android_hierarchy, ios_hierarchy, harmony_hierarchy


def list_serials(platform: str) -> List[str]:
    devices = []
    if platform == Platform.ANDROID:
        raws = adbutils.AdbClient().device_list()
        devices = [item.serial for item in raws]
    if platform == Platform.IOS:
        devices = []
    if platform == Platform.HARMONY:
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
        self.client = hdc.HdcWrapper(serial)

    def take_screenshot(self) -> str:
        with tempfile.NamedTemporaryFile(delete=True, suffix=".png") as f:
            path = f.name
            self.client.screenshot(path)
            return file_to_base64(path)

    def dump_hierarchy(self) -> BaseHierarchy:
        raw = self.client.dump_hierarchy()
        return harmony_hierarchy.convert_harmony_hierarchy(raw)


class AndroidDevice(DeviceMeta):
    def __init__(self, serial: str):
        self.serial = serial
        self.d: u2.Device = u2.connect(serial)

    def take_screenshot(self) -> str:
        img: Image.Image = self.d.screenshot()
        return image_to_base64(img)

    def dump_hierarchy(self) -> BaseHierarchy:
        current = self.d.app_current()
        page_xml = self.d.dump_hierarchy()
        page_json = android_hierarchy.get_android_hierarchy(page_xml)
        return BaseHierarchy(
            jsonHierarchy=page_json,
            activity=current['activity'],
            packageName=current['package'],
            windowSize=self.d.window_size(),
            scale=1
        )


def get_device(platform: str, serial: str) -> Union[HarmonyDevice, AndroidDevice]:
    if serial not in list_serials(platform):
        raise HTTPException(status_code=200, detail="Device not found")
    if platform == Platform.HARMONY:
        return HarmonyDevice(serial)
    elif platform == Platform.ANDROID:
        return AndroidDevice(serial)
    else:
        raise HTTPException(status_code=200, detail="Unsupported platform")


# Global cache for devices
cached_devices = {}


def init_device(platform: str, serial: str):
    device = get_device(platform, serial)
    cached_devices[(platform, serial)] = device
    return platform, serial