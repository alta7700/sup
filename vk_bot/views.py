import json
import traceback
from .vk_funcs.config import var_message, seq_separator
from django.http import HttpResponse
from ReportsDjango.settings import VK_CALLBACK_SECRET_KEY, VK_CALLBACK_CONFIRMATION_CODE, VK_INT_GROUP_ID, VK_STR_GROUP_ID
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

from .vk_funcs.main import message_new


@csrf_exempt
def bot_event(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if data['secret'] == VK_CALLBACK_SECRET_KEY and data['group_id'] == VK_INT_GROUP_ID:
            if data['type'] == 'message_new':
                message = data['object']['message']
                print(f'{datetime.now().strftime("%d-%m %H-%M-%S")}, from_id:{message["from_id"]}, '
                      f'payload:{message.get("payload")}, message:{message["text"]}')
                if datetime.now() - datetime.fromtimestamp(message['date']) < timedelta(seconds=7):
                    try:
                        message_new(message)
                    except:
                        line = '_________________________________________________________________'
                        tb_text = traceback.format_exc().replace("\n", "\n\n")
                        error_info = f'Ошибка от {message["from_id"]}\n{message.get("payload")}'
                        e_msg = f'{error_info}\n{datetime.now().strftime("%Y-%m-%d--%H:%M:%S")}\n{line}\n{tb_text}'
                        for p in seq_separator(e_msg, 3000):
                            var_message(672645458, p)
            elif data['type'] == 'confirmation':
                return HttpResponse(VK_CALLBACK_CONFIRMATION_CODE, content_type="text/plain", status=200)
    return HttpResponse('ok', content_type="text/plain", status=200)
