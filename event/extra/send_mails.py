from django.core.mail import send_mail

def send_guest_mail(user, event, count):
    message=f"""
        Спасибо за регистрацию!

        Вы только что зарегистрировались на событие {event.name} организации {event.author.name} и забронировали {count} ticket(s). 
        Подтверждаем, что Ваша регистрация прошла успешно.*

        *Просим обратить внимание, что данное пригласительное не является правом на бесплатный вход, если организаторы решат сделать событие платным. Так же оно не гарантирует вход на мероприятие быстрее живой очереди.

        Информация о заказчике
        Имя:
        {user.name} {user.last_name}
        E-mail:
        {user.email}
        """
    send_mail('Регистрация на событие',
            message,
            'eventorro@gmail.com',
            [user.email, ])
    return message


def send_host_mail(user, event, count):
    message = f"""
        Новый участник!
        На ваше событие «{event.name}» забронировали {count} ticket(s).
        Email   {user.email}
        Фамилия {user.last_name}
        Имя     {user.name}
    """
    send_mail('Новые заказы в организации',
                message,
                "eventorro@gmail.com",
                [event.author.email, ])