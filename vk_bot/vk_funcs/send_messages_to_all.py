from .config import *


def seq_separator(sequence, size):
    return [sequence[offset:offset + size] for offset in range(0, len(sequence), size)]


cur.execute('SELECT vk_id FROM reports_student WHERE vk_id IS NOT NULL')
user_ids = [str(i['vk_id']) for i in cur.fetchall()]
print(len(user_ids))
usersets = seq_separator(user_ids, 99)
for s in usersets:
    print(s)
    var_message(
        user_ids=','.join(s),
        text='Привет, хорошие новости, у меня появился брат - https://vk.com/kubmedoc\n'
             'Теперь не нужно будет просить кого-то скинуть методички, учебники, планы занятий...\n'
             'Пока он просто бот, но скоро станет ещё и сайтом\n\n'
             'P.S.\nБез тебя база документов не будет пополняться',
        attach_list=['wall-210457778_1']
    )
