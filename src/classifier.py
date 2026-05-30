from src.mail import Mail


CATEGORY_KEYWORDS = {
    "incidents": [
        "критический инцидент",
        "критичный инцидент",
        "массовый сбой",
        "ошибка 500",
        "работа остановлена",
        "недоступен",
        "не отвечает",
        "падает",
        "сервер упал",
        "critical",
        "incident",
    ],
    "access": [
        "запрос доступа",
        "нужны права",
        "выдать права",
        "нет доступа",
        "пропал доступ",
        "vpn",
        "gitlab",
        "confluence",
        "1c",
        "1с",
        "почта",
        "корпоративный портал",
        "active directory",
        "логин",
        "пароль",
    ],
    "hardware": [
        "принтер",
        "ноутбук",
        "мышь",
        "клавиатура",
        "монитор",
        "гарнитура",
        "сканер",
        "оборудование",
        "ремонт",
        "замена",
        "не печатает",
        "картридж",
    ],
    "software": [
        "антивирус",
        "chrome",
        "excel",
        "word",
        "zoom",
        "teams",
        "outlook",
        "adobe reader",
        "после обновления",
        "не запускается",
        "не открывается",
        "зависает",
        "приложение",
        "браузер",
    ],
    "monitoring": [
        "[info]",
        "[warning]",
        "[critical]",
        "[alert]",
        "cpu usage",
        "disk usage",
        "memory usage",
        "healthcheck",
        "мониторинг",
        "система мониторинга",
        "метрика",
        "alert",
        "warning",
    ],
    "documents": [
        "счёт",
        "счет",
        "оплата",
        "платеж",
        "платёж",
        "invoice",
        "payment",
        "договор",
        "контракт",
        "акт",
        "закрывающие документы",
        "техническое задание",
        "тз",
        "инструкция",
        "реквизиты",
        "документ",
        "согласование",
    ],
    "hr": [
        "отпуск",
        "больничный",
        "график работы",
        "нетрудоспособность",
        "новый сотрудник",
        "оформление нового сотрудника",
        "кадры",
        "hr",
        "собеседование",
        "увольнение",
    ],
    "external": [
        "внешний пользователь",
        "клиент",
        "жалоба клиента",
        "партнёр",
        "партнер",
        "тикет",
        "api",
        "интеграция",
        "контрагент",
        "поставщик",
    ],
    "info": [
        "дайджест",
        "приглашение на демо",
        "демо",
        "перенос созвона",
        "статус задач",
        "созвон",
        "новости",
        "информация",
        "напоминание",
    ],
    "spam": [
        "вы выиграли",
        "розыгрыш",
        "скидка",
        "акция",
        "подарок",
        "exclusive offer",
        "limited time",
        "offer",
        "promotion",
        "подтвердите личность",
        "верификация аккаунта",
        "аккаунт будет заблокирован",
        "перейдите по ссылке",
    ],
}


CATEGORY_PRIORITY = [
    "spam",
    "monitoring",
    "incidents",
    "access",
    "hardware",
    "software",
    "documents",
    "hr",
    "external",
    "info",
]


HIGH_PRIORITY_KEYWORDS = [
    "срочно",
    "немедленно",
    "критично",
    "critical",
    "urgent",
    "asap",
]


class MailClassifier:
    def __init__(self):
        self.categories = CATEGORY_KEYWORDS

    def classify(self, mail: Mail) -> str:
        if mail.is_empty():
            return "unclassified"

        subject = mail.subject.lower()
        body = mail.body.lower()

        scores = {}

        for category, keywords in self.categories.items():
            score = 0

            for keyword in keywords:
                keyword = keyword.lower()

                if keyword in subject:
                    score += 3

                if keyword in body:
                    score += 1

            scores[category] = score

        best_score = max(scores.values())

        if best_score == 0:
            return "unclassified"

        best_categories = [
            category
            for category, score in scores.items()
            if score == best_score
        ]

        for category in CATEGORY_PRIORITY:
            if category in best_categories:
                return category

        return best_categories[0]

    def define_priority(self, mail: Mail) -> str:
        text = mail.full_text().lower()

        for keyword in HIGH_PRIORITY_KEYWORDS:
            if keyword in text:
                return "high"

        return "normal"