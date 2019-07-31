import json
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from .models import LinePush, LineMessage
import linebot
from linebot.models import TextSendMessage


line_bot_api = linebot.LineBotApi('アクセストークン')


@csrf_exempt
def callback(request):
    """ラインの友達追加時・メッセージ受信時に呼ばれる"""
    if request.method == 'POST':
        request_json = json.loads(request.body.decode('utf-8'))
        events = request_json['events']
        line_user_id = events[0]['source']['userId']

        # チャネル設定のWeb hook接続確認時にはここ。このIDで見に来る。
        if line_user_id == 'Udeadbeefdeadbeefdeadbeefdeadbeef':
            pass

        # 友達追加時
        elif events[0]['type'] == 'follow':
            profile = line_bot_api.get_profile(line_user_id)
            LinePush.objects.create(user_id=line_user_id, display_name=profile.display_name)

        # アカウントがブロックされたとき
        elif events[0]['type'] == 'unfollow':
            LinePush.objects.filter(user_id=line_user_id).delete()

        # メッセージ受信時
        elif events[0]['type'] == 'message':
            text = request_json['events'][0]['message']['text']
            line_push = get_object_or_404(LinePush, user_id=line_user_id)
            LineMessage.objects.create(push=line_push, text=text, is_admin=False)

    return HttpResponse()


class LineUserList(generic.ListView):
    model = LinePush
    template_name = 'app/line_user_list.html'


class LineMessageList(generic.CreateView):
    model = LineMessage
    fields = ('text',)
    template_name = 'app/line_message_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        line_push = get_object_or_404(LinePush, pk=self.kwargs['pk'])
        context['message_list'] = LineMessage.objects.filter(push=line_push)
        context['push'] = line_push
        return context

    def form_valid(self, form):
        line_push = get_object_or_404(LinePush, pk=self.kwargs['pk'])
        message = form.save(commit=False)
        message.push = line_push
        message.is_admin = True
        message.save()
        line_bot_api.push_message(line_push.user_id, messages=TextSendMessage(text=message.text))
        return redirect('app:line_message_list', pk=line_push.pk)
