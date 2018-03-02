class Payload:
    @staticmethod
    def update(payload, info, skip_list=[]):
        for k, v in info.items():
            keys = payload.keys()
            if k not in keys and k not in skip_list:
                payload[k] = info[k]
        return payload
