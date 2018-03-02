from copy import copy


def update_data_from_info(data, info):
    updated = []
    for d in data:
        copy_info = copy(info)
        if isinstance(d, str):
            copy_info['url'] = d
            updated.append(copy_info)
        else:
            copy_info.update(d)
            updated.append(copy_info)
    return updated
