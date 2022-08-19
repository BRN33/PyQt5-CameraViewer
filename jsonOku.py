import sys
import os
import json


def JsonOku(str):
    f = open(str,encoding='utf-8')
    data = json.load(f)
    return data

    