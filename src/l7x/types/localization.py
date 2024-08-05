#####################################################################################################

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from logging import Logger
from re import MULTILINE, UNICODE, Match, compile as _re_compile
from typing import Final

from l7x.types.language import LKey
from l7x.types.mapping import FrozenDict

#####################################################################################################
# AUTOGENERATE_BEGIN
# !!! dont change manually, use
#   ./src/_l10n.py sync

# pylint: disable=line-too-long, too-many-lines
#####################################################################################################

_DIALOG_PLACEHOLDER_MAP: Final = FrozenDict({
    LKey.AR: 'انقر على الميكروفون وابدأ الحديث',
    LKey.AZ: 'Mikrofonu vurun və danışmağa başlayın',
    LKey.DE: 'Klicken Sie auf das Mikrofon und beginnen Sie zu sprechen',
    LKey.EN: 'Click on the microphone and start talking',
    LKey.ES: 'Haga clic en el micrófono y empiece a hablar',
    LKey.FR: 'Cliquez sur le microphone et commencez à parler',
    LKey.HI: 'माइक्रोफ़ोन पर क्लिक करें और बात करना शुरू करें',
    LKey.KO: '마이크를 클릭하고 대화를 시작하세요',
    LKey.NE: 'माइक्रोफोनमा क्लिक गर्नुहोस् र कुरा सुरु गर्नुहोस्',
    LKey.RU: 'Нажмите на микрофон и начните говорить',
    LKey.TG: 'Микрофонро клик кунед ва сӯҳбатро оғоз кунед',
    LKey.UR: 'مائکروفون پر کلک کریں اور بات کرنا شروع کریں۔',
    LKey.UZ: 'Mikrofonni bosing va suhbatni boshlang',
    LKey.ZH: '点击麦克风并开始讲话',
})

#####################################################################################################

_END_DIALOG_MAP: Final = FrozenDict({
    LKey.AR: 'قم بإنهاء الحوار',
    LKey.AZ: 'Dialoqu bitirin',
    LKey.DE: 'Beenden des Dialogs',
    LKey.EN: 'End the dialog',
    LKey.ES: 'Finalizar el diálogo',
    LKey.FR: 'Terminer le dialogue',
    LKey.HI: 'संवाद समाप्त करें',
    LKey.KO: '대화 종료',
    LKey.NE: 'संवाद अन्त्य गर्नुहोस्',
    LKey.RU: 'Завершить диалог',
    LKey.TG: 'Муколамаро хотима диҳед',
    LKey.UR: 'ڈائیلاگ ختم کریں۔',
    LKey.UZ: 'Muloqot oynasini tugatish',
    LKey.ZH: '结束对话',
})

#####################################################################################################

_START_DIALOG_MAP: Final = FrozenDict({
    LKey.AR: 'ابدأ الحوار',
    LKey.AZ: 'Dialoqa başlayın',
    LKey.DE: 'Starten Sie den Dialog',
    LKey.EN: 'Start the dialog',
    LKey.ES: 'Iniciar el diálogo',
    LKey.FR: 'Démarrer le dialogue',
    LKey.HI: 'संवाद प्रारंभ करें',
    LKey.KO: '대화 시작',
    LKey.NE: 'संवाद सुरु गर्नुहोस्',
    LKey.RU: 'Начать диалог',
    LKey.TG: 'Муколамаро оғоз кунед',
    LKey.UR: 'ڈائیلاگ شروع کریں۔',
    LKey.UZ: 'Muloqot oynasini boshlang',
    LKey.ZH: '开始对话',
})

#####################################################################################################

_CLOSE_POPUP_TITLE_MAP: Final = FrozenDict({
    LKey.AR: 'هل ترغب في إنهاء الحوار؟',
    LKey.AZ: 'Dialoqu bitirmək istərdinizmi?',
    LKey.DE: 'Möchten Sie den Dialog beenden?',
    LKey.EN: 'Would you like to end the dialog?',
    LKey.ES: '¿Le gustaría finalizar el diálogo?',
    LKey.FR: 'Souhaitez-vous mettre fin au dialogue ?',
    LKey.HI: 'क्या आप संवाद समाप्त करना चाहेंगे?',
    LKey.KO: '대화를 종료하시겠습니까?',
    LKey.NE: 'के तपाइँ संवाद अन्त्य गर्न चाहनुहुन्छ?',
    LKey.RU: 'Хотите завершить диалог?',
    LKey.TG: 'Мехоҳед муколамаро хотима диҳед?',
    LKey.UR: 'کیا آپ ڈائیلاگ ختم کرنا چاہیں گے؟',
    LKey.UZ: 'Muloqotni tugatishni xohlaysizmi?',
    LKey.ZH: '您想结束对话吗？',
})

#####################################################################################################

_CLOSE_POPUP_TEXT_MAP: Final = FrozenDict({
    LKey.AR: 'سيكون من المستحيل العودة ومواصلة الحوار بعد الانتهاء.',
    LKey.AZ: 'Tamamlandıqdan sonra geri qayıtmaq və dialoqa davam etmək mümkün olmayacaq.',
    LKey.DE: 'Es ist nicht möglich, zurückzukehren und den Dialog nach Abschluss fortzuführen.',
    LKey.EN: 'It will be impossible to return and continue the dialog after completion.',
    LKey.ES: 'Será imposible volver y continuar el diálogo al finalizarlo.',
    LKey.FR: "Il sera impossible de retourner et de poursuivre le dialogue une fois qu'il sera terminé.",
    LKey.HI: 'पूरा होने के बाद वापस लौटना और संवाद जारी रखना असंभव होगा।',
    LKey.KO: '완료 후에는 대화 상자로 돌아가서 계속할 수 없습니다.',
    LKey.NE: 'यो फर्कन असम्भव हुनेछ र पूरा भएपछि संवाद जारी राख्न।',
    LKey.RU: 'После завершения будет невозможно вернуться и продолжить диалог.',
    LKey.TG: 'Пас аз ба итмом расидани муколама баргаштан ва идома додан ғайриимкон хоҳад буд.',
    LKey.UR: 'مکمل ہونے کے بعد واپسی اور ڈائیلاگ کو جاری رکھنا ناممکن ہو جائے گا۔',
    LKey.UZ: "Tugallangandan keyin qaytish va dialogni davom ettirish imkonsiz bo'ladi.",
    LKey.ZH: '完成后将无法返回并继续对话。',
})

#####################################################################################################

_CLOSE_POPUP_END_BTN_MAP: Final = FrozenDict({
    LKey.AR: 'نهاية',
    LKey.AZ: 'Son',
    LKey.DE: 'Ende',
    LKey.EN: 'End',
    LKey.ES: 'Fin',
    LKey.FR: 'Terminer',
    LKey.HI: 'अंत',
    LKey.KO: '끝',
    LKey.NE: 'अन्त्य',
    LKey.RU: 'Завершить',
    LKey.TG: 'Поён',
    LKey.UR: 'ختم',
    LKey.UZ: 'Oxiri',
    LKey.ZH: '结尾',
})

#####################################################################################################

_CLOSE_POPUP_CONTINUE_BTN_MAP: Final = FrozenDict({
    LKey.AR: 'واصل الحوار',
    LKey.AZ: 'Dialoqu davam etdirin',
    LKey.DE: 'Den Dialog fortführen',
    LKey.EN: 'Сontinue the dialog',
    LKey.ES: 'Continuar el diálogo',
    LKey.FR: 'Poursuivre le dialogue',
    LKey.HI: 'संवाद जारी रखें',
    LKey.KO: '대화를 계속하세요',
    LKey.NE: 'संवाद जारी राख्नुहोस्',
    LKey.RU: 'Продолжить диалог',
    LKey.TG: 'Муколамаро идома диҳед',
    LKey.UR: 'ڈائیلاگ جاری رکھیں',
    LKey.UZ: 'Dialogni davom ettiring',
    LKey.ZH: '继续对话',
})

#####################################################################################################

_NEXT_SURVAY_BTN_MAP: Final = FrozenDict({
    LKey.AR: 'التالي',
    LKey.AZ: 'Sonrakı',
    LKey.DE: 'Weiter',
    LKey.EN: 'Next',
    LKey.ES: 'Seguir',
    LKey.FR: 'Suivante',
    LKey.HI: 'अगला',
    LKey.KO: '다음',
    LKey.NE: 'अर्को',
    LKey.RU: 'Далее',
    LKey.TG: 'Баъдӣ',
    LKey.UR: 'اگلے',
    LKey.UZ: 'Keyingisi',
    LKey.ZH: '下一个',
})

#####################################################################################################

_SKIP_SURVAY_BTN_MAP: Final = FrozenDict({
    LKey.AR: 'أو تخطي الاستطلاع',
    LKey.AZ: 'və ya sorğunu keçin',
    LKey.DE: 'oder Überspringen Sie die Umfrage',
    LKey.EN: 'or Skip the survey',
    LKey.ES: 'o Saltar la encuesta',
    LKey.FR: "ou Passer l'enquête",
    LKey.HI: 'या सर्वेक्षण छोड़ें',
    LKey.KO: '또는 설문조사 건너뛰기',
    LKey.NE: 'वा सर्वेक्षण छोड्नुहोस्',
    LKey.RU: 'или пропустить опрос',
    LKey.TG: 'ё Пурсишро гузаред',
    LKey.UR: 'یا سروے کو چھوڑ دیں۔',
    LKey.UZ: "yoki So'rovni o'tkazib yuboring",
    LKey.ZH: '或跳过调查',
})

#####################################################################################################

_QUESTION_MAP: Final = FrozenDict({
    LKey.AR: 'سؤال',
    LKey.AZ: 'Sual',
    LKey.DE: 'Frage',
    LKey.EN: 'Question',
    LKey.ES: 'Pregunta',
    LKey.FR: 'Question',
    LKey.HI: 'सवाल',
    LKey.KO: '질문',
    LKey.NE: 'प्रश्न',
    LKey.RU: 'Вопрос',
    LKey.TG: 'Савол',
    LKey.UR: 'سوال',
    LKey.UZ: 'Savol',
    LKey.ZH: '问题',
})

#####################################################################################################

_OF_MAP: Final = FrozenDict({
    LKey.AR: 'ل',
    LKey.AZ: 'of',
    LKey.DE: 'von',
    LKey.EN: 'of',
    LKey.ES: 'de',
    LKey.FR: 'de',
    LKey.HI: 'का',
    LKey.KO: '~의',
    LKey.NE: 'को',
    LKey.RU: 'из',
    LKey.TG: 'аз',
    LKey.UR: 'کی',
    LKey.UZ: 'ning',
    LKey.ZH: '的',
})

#####################################################################################################

_SURVAY_ONE_TITLE_MAP: Final = FrozenDict({
    LKey.AR: 'يرجى التقييم على مقياس من 1 إلى 5 لمدى سهولة استخدام المترجم.',
    LKey.AZ: 'Zəhmət olmasa, tərcüməçidən istifadə etməyin sizin üçün nə dərəcədə asan olduğunu 1-dən 5-ə kimi qiymətləndirin.',
    LKey.DE: 'Bitte bewerten Sie auf einer Skala von 1 bis 5, wie einfach es für Sie war, den Übersetzer zu benutzen.',
    LKey.EN: 'Please rate on a scale from 1 to 5 how easy it was for you to use the translator.',
    LKey.ES: 'Califique en una escala del 1 al 5 qué tan fácil le resultó utilizar el traductor.',
    LKey.FR: 'Veuillez évaluer sur une échelle de 1 à 5 la facilité avec laquelle vous avez utilisé le traducteur.',
    LKey.HI: 'कृपया 1 से 5 के पैमाने पर रेटिंग दें कि आपके लिए अनुवादक का उपयोग करना कितना आसान था।',
    LKey.KO: '번역기를 사용하는 것이 얼마나 쉬웠는지 1에서 5까지 척도로 평가해 주세요.',
    LKey.NE: 'कृपया 1 देखि 5 सम्मको स्केलमा मूल्याङ्कन गर्नुहोस् कि तपाईलाई अनुवादक प्रयोग गर्न कति सजिलो थियो।',
    LKey.RU: 'Оцените, пожалуйста, по шкале от 1 до 5, насколько легко вам было пользоваться переводчиком.',
    LKey.TG: 'Лутфан, аз 1 то 5 баҳо диҳед, ки истифодаи тарҷумон барои шумо то чӣ андоза осон буд.',
    LKey.UR: 'براہ کرم 1 سے 5 کے پیمانے پر درجہ بندی کریں کہ آپ کے لیے مترجم کو استعمال کرنا کتنا آسان تھا۔',
    LKey.UZ: "Iltimos, 1 dan 5 gacha bo'lgan shkala bo'yicha baho bering, siz uchun tarjimondan foydalanish qanchalik oson bo'lgan.",
    LKey.ZH: '请按 1 到 5 的等级评价您使用翻译器的难易程度。',
})

#####################################################################################################

_SURVAY_ONE_RATE_ONE_MAP: Final = FrozenDict({
    LKey.AR: 'صعب جدا',
    LKey.AZ: 'Çox çətin',
    LKey.DE: 'Sehr schwierig',
    LKey.EN: 'Very difficult',
    LKey.ES: 'Muy difícil',
    LKey.FR: 'Très difficile',
    LKey.HI: 'बहुत कठिन',
    LKey.KO: '매우 어렵다',
    LKey.NE: 'धेरै गाह्रो',
    LKey.RU: 'Очень сложно',
    LKey.TG: 'Хеле душвор',
    LKey.UR: 'بہت مشکل',
    LKey.UZ: 'Juda qiyin',
    LKey.ZH: '非常困难',
})

#####################################################################################################

_SURVAY_ONE_RATE_TWO_MAP: Final = FrozenDict({
    LKey.AR: 'صعب',
    LKey.AZ: 'Çətin',
    LKey.DE: 'Schwierig',
    LKey.EN: 'Difficult',
    LKey.ES: 'Difícil',
    LKey.FR: 'Difficile',
    LKey.HI: 'कठिन',
    LKey.KO: '어려운',
    LKey.NE: 'गाह्रो',
    LKey.RU: 'Сложно',
    LKey.TG: 'Мушкил',
    LKey.UR: 'مشکل',
    LKey.UZ: 'Qiyin',
    LKey.ZH: '难的',
})

#####################################################################################################

_SURVAY_ONE_RATE_THREE_MAP: Final = FrozenDict({
    LKey.AR: 'حيادي',
    LKey.AZ: 'Neytral',
    LKey.DE: 'Neutral',
    LKey.EN: 'Neutral',
    LKey.ES: 'Neutral',
    LKey.FR: 'Neutre',
    LKey.HI: 'तटस्थ',
    LKey.KO: '중립적',
    LKey.NE: 'तटस्थ',
    LKey.RU: 'Средне',
    LKey.TG: 'Бетараф',
    LKey.UR: 'غیر جانبدار',
    LKey.UZ: 'Neytral',
    LKey.ZH: '中性的',
})

#####################################################################################################

_SURVAY_ONE_RATE_FOUR_MAP: Final = FrozenDict({
    LKey.AR: 'سهل',
    LKey.AZ: 'Asan',
    LKey.DE: 'Einfach',
    LKey.EN: 'Easy',
    LKey.ES: 'Fácil',
    LKey.FR: 'Facile',
    LKey.HI: 'आसान',
    LKey.KO: '쉬운',
    LKey.NE: 'सजिलो',
    LKey.RU: 'Легко',
    LKey.TG: 'Осон',
    LKey.UR: 'آسان',
    LKey.UZ: 'Oson',
    LKey.ZH: '简单的',
})

#####################################################################################################

_SURVAY_ONE_RATE_FIVE_MAP: Final = FrozenDict({
    LKey.AR: 'سهل جدا',
    LKey.AZ: 'Çox asan',
    LKey.DE: 'Sehr einfach',
    LKey.EN: 'Very easy',
    LKey.ES: 'Muy fácil',
    LKey.FR: 'Très facile',
    LKey.HI: 'बहुत आसान',
    LKey.KO: '아주 쉽게',
    LKey.NE: 'धेरै सजीलो',
    LKey.RU: 'Очень легко',
    LKey.TG: 'Хеле осон',
    LKey.UR: 'بہت آسان',
    LKey.UZ: 'Juda oson',
    LKey.ZH: '好简单',
})

#####################################################################################################

_SURVAY_TWO_TITLE_MAP: Final = FrozenDict({
    LKey.AR: 'يرجى التقييم من 1 إلى 5 إلى أي مدى من المحتمل أن توصي بخدمتنا لصديق أو زميل.',
    LKey.AZ: 'Xidmətimizi dostunuza və ya həmkarınıza tövsiyə etmək ehtimalınızı 1-dən 5-ə qədər qiymətləndirin.',
    LKey.DE: 'Bitte bewerten Sie auf einer Skala von 1 bis 5, wie wahrscheinlich es ist, dass Sie unseren Service einem Freund oder Kollegen weiterempfehlen.',
    LKey.EN: 'Please rate from 1 to 5 how likely you are to recommend our service to a friend or a colleague.',
    LKey.ES: 'Califique del 1 al 5 la probabilidad de que recomiende nuestro servicio a un amigo o colega.',
    LKey.FR: 'Veuillez évaluer de 1 à 5 la probabilité que vous recommandiez notre service à un ami ou un collègue.',
    LKey.HI: 'कृपया 1 से 5 तक रेटिंग दें कि आप किसी मित्र या सहकर्मी को हमारी सेवा की कितनी संभावना से अनुशंसा करेंगे।',
    LKey.KO: '친구나 동료에게 저희 서비스를 추천할 가능성을 1에서 5까지 평가해 주십시오.',
    LKey.NE: 'कृपया 1 देखि 5 सम्मको मूल्याङ्कन गर्नुहोस् कि तपाईले हाम्रो सेवालाई साथी वा सहकर्मीलाई सिफारिस गर्ने सम्भावना कति छ।',
    LKey.RU: 'Пожалуйста, оцените от 1 до 5, насколько вероятно, что вы порекомендуете наш сервис другу или коллеге.',
    LKey.TG: 'Лутфан аз 1 то 5 баҳо диҳед, ки то чӣ андоза шумо хидмати моро ба дӯст ё ҳамкоратон тавсия медиҳед.',
    LKey.UR: 'براہ کرم 1 سے 5 تک درجہ بندی کریں کہ آپ کسی دوست یا ساتھی کو ہماری خدمت کی سفارش کرنے کا کتنا امکان رکھتے ہیں۔',
    LKey.UZ: "Iltimos, do'stingizga yoki hamkasbingizga bizning xizmatimizni tavsiya qilish ehtimolini 1 dan 5 gacha baholang.",
    LKey.ZH: '请从 1 到 5 评分，说明您向朋友或同事推荐我们服务的可能性。',
})

#####################################################################################################

_SURVAY_TWO_RATE_ONE_MAP: Final = FrozenDict({
    LKey.AR: 'من المستبعد جدا',
    LKey.AZ: 'Çox az ehtimal',
    LKey.DE: 'Sehr unwahrscheinlich',
    LKey.EN: 'Very Unlikely',
    LKey.ES: 'Muy improbable',
    LKey.FR: 'Très improbable',
    LKey.HI: 'बहुत संभावना नहीं',
    LKey.KO: '매우 가능성 없음',
    LKey.NE: 'धेरै असम्भव',
    LKey.RU: 'Маловероятно',
    LKey.TG: 'Ба эҳтимоли зиёд',
    LKey.UR: 'بہت غیر امکان',
    LKey.UZ: 'Juda kam',
    LKey.ZH: '非常不可能',
})

#####################################################################################################

_SURVAY_TWO_RATE_TWO_MAP: Final = FrozenDict({
    LKey.AR: 'من غير المرجح',
    LKey.AZ: 'Ehtimal yoxdur',
    LKey.DE: 'Unwahrscheinlich',
    LKey.EN: 'Unlikely',
    LKey.ES: 'Improbable',
    LKey.FR: 'Improbable',
    LKey.HI: 'संभावना नहीं',
    LKey.KO: '할 것 같지 않은',
    LKey.NE: 'असम्भव',
    LKey.RU: 'Вряд ли',
    LKey.TG: 'Аз эҳтимол дур аст',
    LKey.UR: 'امکان نہیں',
    LKey.UZ: 'Darhaqiqat',
    LKey.ZH: '不太可能',
})

#####################################################################################################

_SURVAY_TWO_RATE_THREE_MAP: Final = FrozenDict({
    LKey.AR: 'حيادي',
    LKey.AZ: 'Neytral',
    LKey.DE: 'Neutral',
    LKey.EN: 'Neutral',
    LKey.ES: 'Neutral',
    LKey.FR: 'Neutre',
    LKey.HI: 'तटस्थ',
    LKey.KO: '중립적',
    LKey.NE: 'तटस्थ',
    LKey.RU: 'Нейтральный',
    LKey.TG: 'Бетараф',
    LKey.UR: 'غیر جانبدار',
    LKey.UZ: 'Neytral',
    LKey.ZH: '中性的',
})

#####################################################################################################

_SURVAY_TWO_RATE_FOUR_MAP: Final = FrozenDict({
    LKey.AR: 'محتمل',
    LKey.AZ: 'Ehtimal ki',
    LKey.DE: 'Wahrscheinlich',
    LKey.EN: 'Likely',
    LKey.ES: 'Probable',
    LKey.FR: 'Probable',
    LKey.HI: 'संभावित',
    LKey.KO: '할 것 같은',
    LKey.NE: 'सम्भावित',
    LKey.RU: 'Вероятно',
    LKey.TG: 'Эҳтимол',
    LKey.UR: 'امکان',
    LKey.UZ: 'Ehtimol',
    LKey.ZH: '有可能',
})

#####################################################################################################

_SURVAY_TWO_RATE_FIVE_MAP: Final = FrozenDict({
    LKey.AR: 'من المحتمل جدا',
    LKey.AZ: 'Çox güman ki',
    LKey.DE: 'Sehr wahrscheinlich',
    LKey.EN: 'Very Likely',
    LKey.ES: 'Muy probable',
    LKey.FR: 'Très probable',
    LKey.HI: 'बहुत संभावना है',
    LKey.KO: '가능성이 매우 높다',
    LKey.NE: 'धेरै सम्भावित',
    LKey.RU: 'Скорее всего',
    LKey.TG: 'Эҳтимоли зиёд',
    LKey.UR: 'بہت ملتا جلتا',
    LKey.UZ: 'Juda ehtimol',
    LKey.ZH: '很可能',
})

#####################################################################################################

_SURVAY_THREE_TITLE_MAP: Final = FrozenDict({
    LKey.AR: 'يرجى تقييم جودة الترجمة على مقياس من 1 إلى 5.',
    LKey.AZ: 'Zəhmət olmasa tərcümənin keyfiyyətini 1-dən 5-ə qədər olan şkala ilə qiymətləndirin.',
    LKey.DE: 'Bitte bewerten Sie die Qualität der Übersetzung auf einer Skala von 1 bis 5.',
    LKey.EN: 'Please rate the quality of translation on a scale from 1 to 5.',
    LKey.ES: 'Por favor califique la calidad de la traducción en una escala de 1 a 5.',
    LKey.FR: 'Veuillez évaluer la qualité de la traduction sur une échelle de 1 à 5.',
    LKey.HI: 'कृपया अनुवाद की गुणवत्ता को 1 से 5 के पैमाने पर रेट करें।',
    LKey.KO: '번역 품질을 1에서 5까지 평가해 주세요.',
    LKey.NE: 'कृपया 1 देखि 5 सम्मको स्केलमा अनुवादको गुणस्तर मूल्याङ्कन गर्नुहोस्।',
    LKey.RU: 'Пожалуйста, оцените качество перевода по шкале от 1 до 5.',
    LKey.TG: 'Лутфан ба сифати тарҷума аз 1 то 5 баҳо диҳед.',
    LKey.UR: 'براہ کرم ترجمے کے معیار کو 1 سے 5 کے پیمانے پر درجہ دیں۔',
    LKey.UZ: "Iltimos, tarjima sifatini 1 dan 5 gacha bo'lgan shkala bo'yicha baholang.",
    LKey.ZH: '请按 1 到 5 的等级对翻译质量进行评分。',
})

#####################################################################################################

_SURVAY_THREE_RATE_ONE_MAP: Final = FrozenDict({
    LKey.AR: 'رهيب',
    LKey.AZ: 'Dəhşətli',
    LKey.DE: 'Schrecklich',
    LKey.EN: 'Terrible',
    LKey.ES: 'Horrible',
    LKey.FR: 'Terrible',
    LKey.HI: 'भयानक',
    LKey.KO: '끔찍한',
    LKey.NE: 'भयानक',
    LKey.RU: 'Ужасное',
    LKey.TG: 'Даҳшатнок',
    LKey.UR: 'خوفناک',
    LKey.UZ: "Qo'rqinchli",
    LKey.ZH: '糟糕的',
})

#####################################################################################################

_SURVAY_THREE_RATE_TWO_MAP: Final = FrozenDict({
    LKey.AR: 'سيء',
    LKey.AZ: 'Pis',
    LKey.DE: 'Schlecht',
    LKey.EN: 'Bad',
    LKey.ES: 'Mal',
    LKey.FR: 'Mauvais',
    LKey.HI: 'खराब',
    LKey.KO: '나쁜',
    LKey.NE: 'खराब',
    LKey.RU: 'Плохое',
    LKey.TG: 'Бад',
    LKey.UR: 'برا',
    LKey.UZ: 'Yomon',
    LKey.ZH: '坏的',
})

#####################################################################################################

_SURVAY_THREE_RATE_THREE_MAP: Final = FrozenDict({
    LKey.AR: 'طبيعي',
    LKey.AZ: 'Normal',
    LKey.DE: 'Normal',
    LKey.EN: 'Normal',
    LKey.ES: 'Normal',
    LKey.FR: 'Normale',
    LKey.HI: 'सामान्य',
    LKey.KO: '정상',
    LKey.NE: 'सामान्य',
    LKey.RU: 'Среднее',
    LKey.TG: 'Муқаррарӣ',
    LKey.UR: 'نارمل',
    LKey.UZ: 'Oddiy',
    LKey.ZH: '普通的',
})

#####################################################################################################

_SURVAY_THREE_RATE_FOUR_MAP: Final = FrozenDict({
    LKey.AR: 'جيد',
    LKey.AZ: 'Yaxşı',
    LKey.DE: 'Gut',
    LKey.EN: 'Good',
    LKey.ES: 'Bien',
    LKey.FR: 'Bien',
    LKey.HI: 'अच्छा',
    LKey.KO: '좋은',
    LKey.NE: 'राम्रो',
    LKey.RU: 'Хорошее',
    LKey.TG: 'Хуб',
    LKey.UR: 'اچھی',
    LKey.UZ: 'Yaxshi',
    LKey.ZH: '好的',
})

#####################################################################################################

_SURVAY_THREE_RATE_FIVE_MAP: Final = FrozenDict({
    LKey.AR: 'ممتاز',
    LKey.AZ: 'Mükəmməl',
    LKey.DE: 'Perfekt',
    LKey.EN: 'Perfect',
    LKey.ES: 'Perfecto',
    LKey.FR: 'Parfait',
    LKey.HI: 'उत्तम',
    LKey.KO: '완벽한',
    LKey.NE: 'उत्तम',
    LKey.RU: 'Идеальное',
    LKey.TG: 'Комил',
    LKey.UR: 'کامل',
    LKey.UZ: 'Mukammal',
    LKey.ZH: '完美的',
})

#####################################################################################################

_REVIEW_TITLE_MAP: Final = FrozenDict({
    LKey.AR: 'يرجى مشاركة أفكارك حول الخدمة بشكل عام.',
    LKey.AZ: 'Zəhmət olmasa xidmət haqqında ümumi fikirlərinizi bölüşün.',
    LKey.DE: 'Bitte teilen Sie uns Ihre Meinung über den Dienst im Allgemeinen mit.',
    LKey.EN: 'Please share your thoughts about the service in general.',
    LKey.ES: 'Por favor comparta sus opiniones sobre el servicio en general.',
    LKey.FR: 'Veuillez partager vos réflexions sur le service en général.',
    LKey.HI: 'कृपया सेवा के बारे में अपने विचार साझा करें।',
    LKey.KO: '서비스에 대한 전반적인 생각을 공유해주세요.',
    LKey.NE: 'कृपया सामान्य रूपमा सेवाको बारेमा आफ्नो विचार साझा गर्नुहोस्।',
    LKey.RU: 'Поделитесь, пожалуйста, своим мнением о сервисе в целом.',
    LKey.TG: 'Лутфан фикрҳои худро дар бораи хидмат дар маҷмӯъ мубодила кунед.',
    LKey.UR: 'براہ کرم عام طور پر سروس کے بارے میں اپنے خیالات کا اشتراک کریں۔',
    LKey.UZ: 'Iltimos, xizmat haqida umumiy fikringizni bildiring.',
    LKey.ZH: '请分享您对该服务的总体看法。',
})

#####################################################################################################

_REVIEW_PLACEHOLDER_MAP: Final = FrozenDict({
    LKey.AR: 'انقر لبدء الكتابة أو تسجيل الصوت',
    LKey.AZ: 'Səs yazmağa və ya yazmağa başlamaq üçün toxunun',
    LKey.DE: 'Tippen Sie auf , um mit dem Schreiben oder der Sprachaufnahme zu beginnen',
    LKey.EN: 'Tap to start writing or record voice',
    LKey.ES: 'Toque para comenzar a escribir o grabar el voz',
    LKey.FR: 'Appuyez pour commencer à écrire ou enregistrer la voix',
    LKey.HI: 'लिखना शुरू करने या आवाज़ रिकॉर्ड करने के लिए टैप करें',
    LKey.KO: '글쓰기를 시작하거나 음성을 녹음하려면 탭하세요.',
    LKey.NE: 'लेखन सुरु गर्न वा आवाज रेकर्ड गर्न ट्याप गर्नुहोस्',
    LKey.RU: 'Нажмите, чтобы начать писать или начать запись речи',
    LKey.TG: 'Барои оғоз кардани навиштан ё сабти овоз клик кунед',
    LKey.UR: 'لکھنا شروع کرنے یا آواز ریکارڈ کرنے کے لیے تھپتھپائیں۔',
    LKey.UZ: 'Yozishni yoki ovoz yozishni boshlash uchun bosing',
    LKey.ZH: '点击开始书写或录音',
})

#####################################################################################################

_REVIEW_BOTTOM_TEXT_MAP: Final = FrozenDict({
    LKey.AR: 'يمكنك تخطي هذا السؤال وإنهاء الاستبيان على الفور',
    LKey.AZ: 'Bu sualı atlaya və anketi dərhal bitirə bilərsiniz',
    LKey.DE: 'Sie können diese Frage überspringen und die Umfrage sofort beenden',
    LKey.EN: 'You can skip this question and finish the survey straight away',
    LKey.ES: 'Puede omitir esta pregunta y finalizar la encuesta de inmediato.',
    LKey.FR: 'Vous pouvez ignorer cette question et terminer le sondage immédiatement',
    LKey.HI: 'आप इस प्रश्न को छोड़ कर सीधे सर्वेक्षण समाप्त कर सकते हैं',
    LKey.KO: '이 질문을 건너뛰고 바로 설문조사를 완료할 수 있습니다.',
    LKey.NE: 'तपाइँ यो प्रश्न छोड्न सक्नुहुन्छ र तुरुन्तै सर्वेक्षण समाप्त गर्न सक्नुहुन्छ',
    LKey.RU: 'Вы можете пропустить этот вопрос и сразу завершить опрос.',
    LKey.TG: 'Шумо метавонед ин саволро гузаред ва дарҳол пурсишро анҷом диҳед',
    LKey.UR: 'آپ اس سوال کو چھوڑ سکتے ہیں اور فوراً سروے مکمل کر سکتے ہیں۔',
    LKey.UZ: "Siz bu savolni o'tkazib yuborishingiz va so'rovni darhol tugatishingiz mumkin",
    LKey.ZH: '您可以跳过此问题并直接完成调查',
})

#####################################################################################################

_FINISH_SURVAY_BTN_MAP: Final = FrozenDict({
    LKey.AR: 'قم بإنهاء الاستطلاع',
    LKey.AZ: 'Anketi tamamlayın',
    LKey.DE: 'Beenden Sie die Umfrage',
    LKey.EN: 'Finish the survey',
    LKey.ES: 'Terminar la encuesta',
    LKey.FR: "Terminer l'enquête",
    LKey.HI: 'सर्वेक्षण समाप्त करें',
    LKey.KO: '설문조사를 완료하세요',
    LKey.NE: 'सर्वेक्षण समाप्त गर्नुहोस्',
    LKey.RU: 'Завершить опрос',
    LKey.TG: 'Пурсишро анҷом диҳед',
    LKey.UR: 'سروے مکمل کریں۔',
    LKey.UZ: "So'rovni yakunlang",
    LKey.ZH: '完成调查',
})

#####################################################################################################

_BACK_TO_MENU_BTN_MAP: Final = FrozenDict({
    LKey.AR: 'العودة إلى القائمة',
    LKey.AZ: 'Menyuya qayıt',
    LKey.DE: 'Zurück zum Menü',
    LKey.EN: 'Back to menu',
    LKey.ES: 'Volver al menú',
    LKey.FR: 'Retour au menu',
    LKey.HI: 'मैन्यू में वापस',
    LKey.KO: '메뉴로 돌아가기',
    LKey.NE: 'मेनुमा फर्कनुहोस्',
    LKey.RU: 'Назад к меню',
    LKey.TG: 'Бозгашт ба меню',
    LKey.UR: 'مینو پر واپس جائیں۔',
    LKey.UZ: 'Menyuga qaytish',
    LKey.ZH: '返回菜单',
})

#####################################################################################################

_FINAL_TEXT_MAP: Final = FrozenDict({
    LKey.AR: 'شكرا لإجاباتك!',
    LKey.AZ: 'Cavablarınız üçün təşəkkür edirik!',
    LKey.DE: 'Vielen Dank für Ihre Antworten!',
    LKey.EN: 'Thank you for your answers!',
    LKey.ES: '¡Gracias por sus respuestas!',
    LKey.FR: 'Merci pour vos réponses !',
    LKey.HI: 'आपके जवाब के लिए धन्यवाद!',
    LKey.KO: '답변해주셔서 감사합니다!',
    LKey.NE: 'तपाईंको जवाफहरूको लागि धन्यवाद!',
    LKey.RU: 'Спасибо за ваши ответы!',
    LKey.TG: 'Ташаккур барои ҷавобҳоятон!',
    LKey.UR: 'آپ کے جوابات کے لیے آپ کا شکریہ!',
    LKey.UZ: 'Javoblaringiz uchun rahmat!',
    LKey.ZH: '谢谢您的回答！',
})

#####################################################################################################

_LANG_SELECT_TITLE_MAP: Final = FrozenDict({
    LKey.AR: 'اختر لغتك المفضلة',
    LKey.AZ: 'Tercih etdiyiniz dili seçin',
    LKey.DE: 'Wählen Sie Ihre bevorzugte Sprache',
    LKey.EN: 'Select your preferred language',
    LKey.ES: 'Seleccionar una idioma preferida',
    LKey.FR: 'Sélectionnez votre langue préférée',
    LKey.HI: 'अपनी पसंदीदा भाषा चुनें',
    LKey.KO: '선호하는 언어를 선택하세요',
    LKey.NE: 'आफ्नो मनपर्ने भाषा चयन गर्नुहोस्',
    LKey.RU: 'Выберите предпочитаемый язык',
    LKey.TG: 'Забони дӯстдоштаи худро интихоб кунед',
    LKey.UR: 'اپنی پسند کی زبان منتخب کریں۔',
    LKey.UZ: "O'zingiz yoqtirgan tilni tanlang",
    LKey.ZH: '选择您的首选语言',
})

#####################################################################################################

_EDITING_MAP: Final = FrozenDict({
    LKey.AR: 'التحرير',
    LKey.AZ: 'Redaktə',
    LKey.DE: 'Bearbeitung',
    LKey.EN: 'Editing',
    LKey.ES: 'Editar',
    LKey.FR: 'Édition',
    LKey.HI: 'संपादन',
    LKey.KO: '편집',
    LKey.NE: 'सम्पादन गर्दै',
    LKey.RU: 'Редактирование',
    LKey.TG: 'Таҳрир',
    LKey.UR: 'ترمیم کرنا',
    LKey.UZ: 'Tahrirlash',
    LKey.ZH: '編輯',
})

#####################################################################################################

_T_ARABIC_MAP: Final = FrozenDict({
    LKey.AR: 'عربي',
    LKey.AZ: 'ərəb',
    LKey.DE: 'Arabisch',
    LKey.EN: 'Arabic',
    LKey.ES: 'Árabe',
    LKey.FR: 'Arabe',
    LKey.HI: 'अरबी',
    LKey.KO: '아라비아 말',
    LKey.NE: 'अरबी',
    LKey.RU: 'Арабский',
    LKey.TG: 'арабӣ',
    LKey.UR: 'عربی',
    LKey.UZ: 'arabcha',
    LKey.ZH: '阿拉伯',
})

#####################################################################################################

_T_AZERBAIJANI_MAP: Final = FrozenDict({
    LKey.AR: 'أذربيجاني',
    LKey.AZ: 'Azərbaycan',
    LKey.DE: 'Aserbaidschanisch',
    LKey.EN: 'Azerbaijani',
    LKey.ES: 'Azerí',
    LKey.FR: 'Azerbaïdjanais',
    LKey.HI: 'आज़रबाइजानी',
    LKey.KO: '아제르바이잔',
    LKey.NE: 'अजरबैजानी',
    LKey.RU: 'Азербайджанский',
    LKey.TG: 'озарбойҷонӣ',
    LKey.UR: 'آذربائیجانی',
    LKey.UZ: 'ozarbayjon',
    LKey.ZH: '阿塞拜疆语',
})

#####################################################################################################

_T_GERMAN_MAP: Final = FrozenDict({
    LKey.AR: 'ألمانية',
    LKey.AZ: 'alman',
    LKey.DE: 'Deutsch',
    LKey.EN: 'German',
    LKey.ES: 'Alemán',
    LKey.FR: 'Allemand',
    LKey.HI: 'जर्मन',
    LKey.KO: '독일 사람',
    LKey.NE: 'जर्मन',
    LKey.RU: 'Немецкий',
    LKey.TG: 'олмонӣ',
    LKey.UR: 'جرمن',
    LKey.UZ: 'nemis',
    LKey.ZH: '德语',
})

#####################################################################################################

_T_ENGLISH_MAP: Final = FrozenDict({
    LKey.AR: 'إنجليزي',
    LKey.AZ: 'İngilis dili',
    LKey.DE: 'Englisch',
    LKey.EN: 'English',
    LKey.ES: 'Inglés',
    LKey.FR: 'Anglais',
    LKey.HI: 'अंग्रेज़ी',
    LKey.KO: '영어',
    LKey.NE: 'अंग्रेजी',
    LKey.RU: 'Английский',
    LKey.TG: 'англисӣ',
    LKey.UR: 'انگریزی',
    LKey.UZ: 'Ingliz',
    LKey.ZH: '英语',
})

#####################################################################################################

_T_SPANISH_MAP: Final = FrozenDict({
    LKey.AR: 'الأسبانية',
    LKey.AZ: 'ispan dili',
    LKey.DE: 'Spanisch',
    LKey.EN: 'Spanish',
    LKey.ES: 'Español',
    LKey.FR: 'Espagnol',
    LKey.HI: 'स्पैनिश',
    LKey.KO: '스페인의',
    LKey.NE: 'स्पेनिस',
    LKey.RU: 'Испанский',
    LKey.TG: 'испанӣ',
    LKey.UR: 'ہسپانوی',
    LKey.UZ: 'ispancha',
    LKey.ZH: '西班牙语',
})

#####################################################################################################

_T_FRENCH_MAP: Final = FrozenDict({
    LKey.AR: 'فرنسي',
    LKey.AZ: 'Fransız dili',
    LKey.DE: 'Französisch',
    LKey.EN: 'French',
    LKey.ES: 'Francés',
    LKey.FR: 'Français',
    LKey.HI: 'फ्रेंच',
    LKey.KO: '프랑스 국민',
    LKey.NE: 'फ्रान्सेली',
    LKey.RU: 'Французский',
    LKey.TG: 'фаронсавӣ',
    LKey.UR: 'فرانسیسی',
    LKey.UZ: 'frantsuz',
    LKey.ZH: '法语',
})

#####################################################################################################

_T_HINDI_MAP: Final = FrozenDict({
    LKey.AR: 'الهندية',
    LKey.AZ: 'hind',
    LKey.DE: 'Hindi',
    LKey.EN: 'Hindi',
    LKey.ES: 'Hindi',
    LKey.FR: 'Hindi',
    LKey.HI: 'हिंदी',
    LKey.KO: '힌디 어',
    LKey.NE: 'हिन्दी',
    LKey.RU: 'Хинди',
    LKey.TG: 'ҳиндӣ',
    LKey.UR: 'ہندی',
    LKey.UZ: 'hind',
    LKey.ZH: '印地语',
})

#####################################################################################################

_T_KOREAN_MAP: Final = FrozenDict({
    LKey.AR: 'الكورية',
    LKey.AZ: 'koreyalı',
    LKey.DE: 'Koreanisch',
    LKey.EN: 'Korean',
    LKey.ES: 'Coreano',
    LKey.FR: 'Coréen',
    LKey.HI: 'कोरियाई',
    LKey.KO: '한국인',
    LKey.NE: 'कोरियाली',
    LKey.RU: 'Корейский',
    LKey.TG: 'Корея',
    LKey.UR: 'کورین',
    LKey.UZ: 'koreys',
    LKey.ZH: '韩国人',
})

#####################################################################################################

_T_NEPALI_MAP: Final = FrozenDict({
    LKey.AR: 'النيبالية',
    LKey.AZ: 'nepal dili',
    LKey.DE: 'Nepalesisch',
    LKey.EN: 'Nepali',
    LKey.ES: 'Nepalí',
    LKey.FR: 'Népalais',
    LKey.HI: 'नेपाली',
    LKey.KO: '네팔어',
    LKey.NE: 'नेपाली',
    LKey.RU: 'Непальский',
    LKey.TG: 'непалӣ',
    LKey.UR: 'نیپالی',
    LKey.UZ: 'Nepal',
    LKey.ZH: '尼泊尔语',
})

#####################################################################################################

_T_RUSSIAN_MAP: Final = FrozenDict({
    LKey.AR: 'الروسية',
    LKey.AZ: 'rus',
    LKey.DE: 'Russisch',
    LKey.EN: 'Russian',
    LKey.ES: 'Ruso',
    LKey.FR: 'Russe',
    LKey.HI: 'रूसी',
    LKey.KO: '러시아인',
    LKey.NE: 'रुसी',
    LKey.RU: 'Русский',
    LKey.TG: 'русӣ',
    LKey.UR: 'روسی',
    LKey.UZ: 'rus',
    LKey.ZH: '俄语',
})

#####################################################################################################

_T_TAJIK_MAP: Final = FrozenDict({
    LKey.AR: 'الأسبانية',
    LKey.AZ: 'tacik',
    LKey.DE: 'Tadschikisch',
    LKey.EN: 'Tajik',
    LKey.ES: 'Tayiko',
    LKey.FR: 'Tadjik',
    LKey.HI: 'ताजिक',
    LKey.KO: '타직어',
    LKey.NE: 'ताजिक',
    LKey.RU: 'Таджикский',
    LKey.TG: 'тоҷикӣ',
    LKey.UR: 'تاجک',
    LKey.UZ: 'tojik',
    LKey.ZH: '塔吉克',
})

#####################################################################################################

_T_URDU_MAP: Final = FrozenDict({
    LKey.AR: 'الأردية',
    LKey.AZ: 'Urdu',
    LKey.DE: 'Urdu',
    LKey.EN: 'Urdu',
    LKey.ES: 'Urdu',
    LKey.FR: 'Ourdou',
    LKey.HI: 'उर्दू',
    LKey.KO: '우르두어',
    LKey.NE: 'उर्दू',
    LKey.RU: 'Урду',
    LKey.TG: 'урду',
    LKey.UR: 'اردو',
    LKey.UZ: 'urdu',
    LKey.ZH: '乌尔都语',
})

#####################################################################################################

_T_UZBEK_MAP: Final = FrozenDict({
    LKey.AR: 'الأوزبكية',
    LKey.AZ: 'tacik',
    LKey.DE: 'Usbekisch',
    LKey.EN: 'Uzbek',
    LKey.ES: 'Uzbeko',
    LKey.FR: 'Ouzbek',
    LKey.HI: 'उज़बेक',
    LKey.KO: '우즈벡어',
    LKey.NE: 'उज्बेक',
    LKey.RU: 'Узбекский',
    LKey.TG: 'узбек',
    LKey.UR: 'ازبک',
    LKey.UZ: "o'zbek",
    LKey.ZH: '乌兹别克语',
})

#####################################################################################################

_T_CHINESE_MAP: Final = FrozenDict({
    LKey.AR: 'صينى',
    LKey.AZ: 'çinli',
    LKey.DE: 'Chinesisch',
    LKey.EN: 'Chinese',
    LKey.ES: 'Chino',
    LKey.FR: 'Chinois',
    LKey.HI: 'चीनी',
    LKey.KO: '중국인',
    LKey.NE: 'चिनियाँ',
    LKey.RU: 'Китайский',
    LKey.TG: 'чинӣ',
    LKey.UR: 'چینی',
    LKey.UZ: 'Xitoy',
    LKey.ZH: '中国人',
})

#####################################################################################################

_REC_ERROR_MSG_MAP: Final = FrozenDict({
    LKey.AR: 'فشل التعرف على الكلام. حاول مرة اخرى.',
    LKey.AZ: 'Nitqin tanınması uğursuz oldu. Zəhmət olmasa bir daha cəhd edin.',
    LKey.DE: 'Die Spracherkennung ist fehlgeschlagen. Bitte versuchen Sie es erneut.',
    LKey.EN: 'Speech recognition failed. Please try again.',
    LKey.ES: 'El reconocimiento de voz falló. Inténtalo de nuevo.',
    LKey.FR: 'La reconnaissance vocale a échoué. Veuillez réessayer.',
    LKey.HI: 'वाक् पहचान विफल. कृपया पुनः प्रयास करें।',
    LKey.KO: '음성 인식에 실패했습니다. 다시 시도해 주세요.',
    LKey.NE: 'वाक् पहिचान असफल भयो। फेरि प्रयास गर्नुहोस।',
    LKey.RU: 'Распознавание речи не удалось. Пожалуйста, попробуйте еще раз.',
    LKey.TG: 'Шинохтани нутқ ноком шуд. Лутфан бори дигар кӯшиш кунед.',
    LKey.UR: 'تقریر کی شناخت ناکام ہو گئی۔ دوبارہ کوشش کریں.',
    LKey.UZ: "Nutqni tanib bo‘lmadi. Iltimos, yana bir bor urinib ko'ring.",
    LKey.ZH: '语音识别失败。请重试。',
})

#####################################################################################################
# AUTOGENERATE_END
#####################################################################################################

_NOTRANSLATE_WRAP_PATTERN: Final = _re_compile(r'(\[@(?P<non_translated>.*?)@\])', MULTILINE | UNICODE)

#####################################################################################################

def _get_notranslate_group(match: Match[str]) -> str:
    return match.group('non_translated')

#####################################################################################################

def _clean_notranslate_wraps(text: str) -> str:
    return _NOTRANSLATE_WRAP_PATTERN.sub(_get_notranslate_group, text)

#####################################################################################################

@dataclass(frozen=True)
class _LocalizedSentence:
    default_text: str
    localized_sentences: Mapping[LKey, str] = field(default_factory=lambda: FrozenDict({}))

    #####################################################################################################

    def __call__(self, logger: Logger, locale: LKey = LKey.EN, **kwargs: str | int | bool) -> str:
        localized_sentence = self.localized_sentences.get(locale, '')
        if not localized_sentence:
            logger.warning(f'Cannot find localized sentence for "{locale.value}". Use default text: "{self.default_text}"')
            localized_sentence = _clean_notranslate_wraps(self.default_text)
        return localized_sentence.format(**kwargs)

#####################################################################################################

class TKey(_LocalizedSentence, Enum):
    LANG_SELECT_TITLE = 'Select your preferred language', _LANG_SELECT_TITLE_MAP
    DIALOG_PLACEHOLDER = 'Click on the microphone and start talking', _DIALOG_PLACEHOLDER_MAP
    END_DIALOG = 'End the dialog', _END_DIALOG_MAP
    START_DIALOG = 'Start the dialog', _START_DIALOG_MAP
    CLOSE_POPUP_TITLE = 'Would you like to end the dialog?', _CLOSE_POPUP_TITLE_MAP
    CLOSE_POPUP_TEXT = 'It will be impossible to return and continue the dialog after completion.', _CLOSE_POPUP_TEXT_MAP
    CLOSE_POPUP_END_BTN = 'End', _CLOSE_POPUP_END_BTN_MAP
    CLOSE_POPUP_CONTINUE_BTN = 'Сontinue the dialog', _CLOSE_POPUP_CONTINUE_BTN_MAP
    NEXT_SURVAY_BTN = 'Next', _NEXT_SURVAY_BTN_MAP
    SKIP_SURVAY_BTN = 'or Skip the survey', _SKIP_SURVAY_BTN_MAP
    QUESTION = 'Question', _QUESTION_MAP
    OF = 'of', _OF_MAP
    SURVAY_ONE_TITLE = 'Please rate on a scale from 1 to 5 how easy it was for you to use the translator.', _SURVAY_ONE_TITLE_MAP
    SURVAY_ONE_RATE_ONE = 'Very difficult', _SURVAY_ONE_RATE_ONE_MAP
    SURVAY_ONE_RATE_TWO = 'Difficult', _SURVAY_ONE_RATE_TWO_MAP
    SURVAY_ONE_RATE_THREE = 'Neutral', _SURVAY_ONE_RATE_THREE_MAP
    SURVAY_ONE_RATE_FOUR = 'Easy', _SURVAY_ONE_RATE_FOUR_MAP
    SURVAY_ONE_RATE_FIVE = 'Very easy', _SURVAY_ONE_RATE_FIVE_MAP
    SURVAY_TWO_TITLE = 'Please rate from 1 to 5 how likely you are to recommend our service to a friend or a colleague.', _SURVAY_TWO_TITLE_MAP
    SURVAY_TWO_RATE_ONE = 'Very Unlikely', _SURVAY_TWO_RATE_ONE_MAP
    SURVAY_TWO_RATE_TWO = 'Unlikely', _SURVAY_TWO_RATE_TWO_MAP
    SURVAY_TWO_RATE_THREE = 'Neutral', _SURVAY_TWO_RATE_THREE_MAP
    SURVAY_TWO_RATE_FOUR = 'Likely', _SURVAY_TWO_RATE_FOUR_MAP
    SURVAY_TWO_RATE_FIVE = 'Very Likely', _SURVAY_TWO_RATE_FIVE_MAP
    SURVAY_THREE_TITLE = 'Please rate the quality of translation on a scale from 1 to 5.', _SURVAY_THREE_TITLE_MAP
    SURVAY_THREE_RATE_ONE = 'Terrible', _SURVAY_THREE_RATE_ONE_MAP
    SURVAY_THREE_RATE_TWO = 'Bad', _SURVAY_THREE_RATE_TWO_MAP
    SURVAY_THREE_RATE_THREE = 'Normal', _SURVAY_THREE_RATE_THREE_MAP
    SURVAY_THREE_RATE_FOUR = 'Good', _SURVAY_THREE_RATE_FOUR_MAP
    SURVAY_THREE_RATE_FIVE = 'Perfect', _SURVAY_THREE_RATE_FIVE_MAP
    REVIEW_TITLE = 'Please share your thoughts about the service in general.', _REVIEW_TITLE_MAP
    REVIEW_PLACEHOLDER = 'Tap to start writing or record voice', _REVIEW_PLACEHOLDER_MAP
    REVIEW_BOTTOM_TEXT = 'You can skip this question and finish the survey straight away', _REVIEW_BOTTOM_TEXT_MAP
    FINISH_SURVAY_BTN = 'Finish the survey', _FINISH_SURVAY_BTN_MAP
    FINAL_TEXT = 'Thank you for your answers!', _FINAL_TEXT_MAP
    BACK_TO_MENU_BTN = 'Back to menu', _BACK_TO_MENU_BTN_MAP
    EDITING = 'Editing', _EDITING_MAP
    T_ARABIC = 'Arabic', _T_ARABIC_MAP
    T_AZERBAIJANI = 'Azerbaijani', _T_AZERBAIJANI_MAP
    T_GERMAN = 'German', _T_GERMAN_MAP
    T_ENGLISH = 'English', _T_ENGLISH_MAP
    T_SPANISH = 'Spanish', _T_SPANISH_MAP
    T_FRENCH = 'French', _T_FRENCH_MAP
    T_HINDI = 'Hindi', _T_HINDI_MAP
    T_KOREAN = 'Korean', _T_KOREAN_MAP
    T_NEPALI = 'Nepali', _T_NEPALI_MAP
    T_RUSSIAN = 'Russian', _T_RUSSIAN_MAP
    T_TAJIK = 'Tajik', _T_TAJIK_MAP
    T_URDU = 'Urdu', _T_URDU_MAP
    T_UZBEK = 'Uzbek', _T_UZBEK_MAP
    T_CHINESE = 'Chinese', _T_CHINESE_MAP
    REC_ERROR_MSG = 'Speech recognition failed. Please try again.', _REC_ERROR_MSG_MAP

#####################################################################################################
