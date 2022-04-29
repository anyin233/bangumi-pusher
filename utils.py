def get_subject_id_list(bgm_list):
    id_list = []
    for bgm in bgm_list:
        bgm_id = bgm['subject_id']
        id_list.append(bgm_id)
    return id_list

    