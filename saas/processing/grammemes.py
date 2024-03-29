# -*- Encoding: utf-8 -*-

# ----- Грамматические признаки -----

# часть речи
PARTS_OF_SPEECH = (
    'S', # существительное (яблоня, лошадь, корпус, вечность)
    'A', # прилагательное (коричневый, таинственный, морской)
    'NUM', # числительное (четыре, десять, много)
    'ANUM', # числительное-прилагательное (один, седьмой, восьмидесятый)
    'V', # глагол (пользоваться, обрабатывать)
    'ADV', # наречие (сгоряча, очень)
    'PRAEDIC', # предикатив (жаль, хорошо, пора)
    'PARENTH', # вводное слово (кстати, по-моему)
    'SPRO', # местоимение-существительное (она, что)
    'APRO', # местоимение-прилагательное (который, твой)
    'ADVPRO', # местоименное наречие (где, вот)
    'PRAEDICPRO', # местоимение-предикатив (некого, нечего)
    'PR', # предлог (под, напротив)
    'CONJ', # союз (и, чтобы)
    'PART', # частица (бы, же, пусть)
    'INTJ', # междометие (увы, батюшки)
    )

# род
GENDERS = (
    'm', # мужской род (работник, стол)
    'f', # женский род (работница, табуретка)
    'n', # средний род (животное, озеро)
    'mf', # «общий род» (задира, пьяница)
    )

# склонение    
DECLENSIONS = (
    '1decl',    # первое склонение
    '2decl',    # второе склонение
    '3decl',    # третье склонение
    '0',        # несклоняемые
    'adjdecl',  # склоняющиеся как прилагательное
    'hetrcl',   # разносклоняемые
    'ideclm',   # на -ий
    'ideclf',   # на -ия
    'idecln',   # на -ие
    'famdeclm', # фамилий мужского рода
    'famdeclf', # фамилий женского рода
    'pltantum', # только множественного числа
    )

# спряжение    
CONJUGATIONS = (
    '1conj',    # первое спряжение
    '2conj',    # второе спряжение
    'hetrcj',   # разноспрягаемые
    'irr',      # неправильные
    )

# разряд существительных
NOUN_TYPES = (
    'concr',     #конкретные
    'abstr',     #отвлеченные
    'mat',       #вещественные
    'coll',      #собирательные
    )

# разряд местоимений
PRONOUN_TYPES = (
    'pers',      #личные
    'refl',      #возвратное
    'rel',       #вопросительно-относительные
    'indef',     #неопределённые
    'neg',       #отрицательные
    'poss',      #притяжательные
    'dem',       #указательные
    'def',       #определительные
    )

# разряд прилагательных
ADVERB_TYPES = (
    'manner',    #образа действия
    'degree',    #меры и степени
    'time',      #времени
    'place',     #места
    'reason',    #причины
    'goal',      #цели
    )

#разряд наречий 
ADJECTIVE_TYPES = (
    'qual',      #качественные
    'reladj',    #относительные
    'possadj',   #притяжательные
    )

# одушевленность
ANIMATES = (
    'anim', # одушевленность (человек, ангел, утопленник)
    'inan', # неодушевленность (рука, облако, культура)
    )

# число
NUMBERS = (
    'sg', # единственное число (яблоко, гордость)
    'pl', # множественное число (яблоки, ножницы, детишки)
    )

# падеж
CASES = (
    'nom', # именительный падеж (голова, сын, степь, сани, который)
    'gen', # родительный падеж (головы, сына, степи, саней, которого)
    'dat', # дательный падеж (голове, сыну, степи, саням, которому)
    'acc', # винительный падеж (голову, сына, степь, сани, который/которого)
    'ins', # творительный падеж (головой, сыном, степью, санями, которым)
    'loc', # предложный падеж ([о] голове, сыне, степи, санях, котором)
    'gen2', # второй родительный падеж (чашка чаю)
    'acc2', # второй винительный падеж (постричься в монахи; по два человека)
    'loc2', # второй предложный падеж (в лесу, на оси)
    'voc', # звательная форма (Господи, Серёж, ребят)
    'adnum', # счётная форма (два часа, три шара)
    )

# степень сравнения (3) / краткость (2)
DEGREES_AND_BREVITIES = (
    'comp', # сравнительная степень (глубже)
    'comp2', # форма «по+сравнительная степень» (поглубже)
    'supr', # превосходная степень (глубочайший)

    'brev', # краткая форма (высок, нежна, прочны, рад)
    'plen', # полная форма (высокий, нежная, прочные, морской)
    )

# вид
ASPECTS = (
    'pf', # совершенный вид (пошёл, встречу)
    'ipf', # несовершенный вид (ходил, встречаю)
    )

# переходность
TRANSITIVITIES = (
    'intr', # непереходность (ходить, вариться)
    'tran', # переходность (вести, варить)
    )

# залог
VOICES = (
    'act', # действительный залог (разрушил, разрушивший)
    'pass', # страдательный залог (только у причастий: разрушаемый, разрушенный)
    'med', # медиальный, или средний залог (глагольные формы на -ся: разрушился и т.п.)
    )

# наклонение (3) / форма (репрезентация) глагола (3)
MOODS_AND_FORMS = (
    'indic', # изъявительное наклонение (украшаю, украшал, украшу)
    'imper', # повелительное наклонение (украшай)
    'imper2', # форма повелительного наклонения 1 л. мн. ч. на -те (идемте)

    'inf', # инфинитив (украшать)
    'partcp', # причастие (украшенный)
    'ger', # деепричастие (украшая)
    )

# время
TENSES = (
    'praet', # прошедшее время (украшали, украшавший, украсив)
    'praes', # настоящее время (украшаем, украшающий, украшая)
    'fut', # будущее время (украсим)
    )

# лицо
PERSONS = (
    '1p', # первое лицо (украшаю)
    '2p', # второе лицо (украшаешь)
    '3p', # третье лицо (украшает)
    )

# Антропонимы
ANTHROPONYMS = (
    'persn', # личное имя (Иван, Дарья, Леопольд, Эстер, Гомер, Маугли)
    'patrn', # отчество (Иванович, Павловна)
    'famn', # фамилия (Николаев, Волконская, Гумбольдт)
    )

# прочие признаки
OTHER = (
    'norm', 'ciph', 'anom', 'distort', 'bastard', 'INIT', 'abbr',
    '0', # несклоняемое (шоссе, Седых)
    )

# все грамматики
GRAMM_CATEGORIES = (
    PARTS_OF_SPEECH, GENDERS, ANIMATES, NUMBERS, CASES, DEGREES_AND_BREVITIES,
    ASPECTS, TRANSITIVITIES, VOICES, MOODS_AND_FORMS, TENSES, PERSONS, ANTHROPONYMS,
    OTHER
    )
GRAMMS = []
for gr in GRAMM_CATEGORIES:
    GRAMMS.extend(gr)
GRAMMS = tuple(GRAMMS)

# vvv TODO vvv
"""
# ----- Семантические признаки -----

# Разряды
CATEGORIES = (
    'r:concr', # предметные имена (девочка, стол, молоко)
    'r:abstr', # непредметные имена (вождение, яркость, время)
    'r:propn', # имена собственные (Иван, Эйнштейн, Петроград)
    'r:qual', # качественные (хороший, большой)
    'r:rel', # вопросительные/относительные (кто, который, когда, деревянный, лунный)
    'r:poss', # притяжательные (мой, его, свой, божий, отцов, мужнин)
    'r:invar', # неизменяемые (беж, джерси)
    'r:card', # количественные (два, пять, десять)
    'r:card:pauc', # числительные малого количества (два, три, четыре, оба, пол, полтора)
    'r:ord', # порядковые (первый, второй, десятый)
    'r:pers', # личные (я, он)
    'r:ref', # возвратные (себя)
    'r:dem', # указательные (этот, такой)
    'r:indet', # неопределенные (некоторый, некогда)
    'r:neg', # отрицательные (никакой, ничей)
    'r:spec', # кванторные (определительные) (всякий, каждый, любой)
    )

# Таксономия (тематический класс):
TAXONOMY = (
    't:hum', # лица (человек, учитель)
    't:hum:etn', # этнонимы (эфиоп, итальянка)
    't:hum:kin', # имена родства (брат, бабушка)
    't:hum:supernat', # сверхъестественные существа (русалка, инопланетянин)
    't:animal', # животные (корова, жираф, сорока, ящерица, муравей)
    't:plant', # растения (береза, роза, трава)
    't:stuff', # вещества и материалы (вода, песок, тесто, жесть, шелк)
    't:space', # пространство и место (космос, город, тайга, овраг, вход)
    't:constr', # здания и сооружения (дом, шалаш, мост)
    't:tool', # инструменты и приспособления (молоток, палка, пуговица, машина)
    't:tool:instr', # инструменты (молоток, штопор, игла, карандаш)
    't:tool:device', # механизмы и приборы (телефон, сеялка, градусник)
    't:tool:transp', # транспортные средства (автобус, поезд, сани)
    't:tool:weapon', # оружие (сабля, пистолет, гаубица)
    't:tool:mus', # музыкальные инструменты (рояль, скрипка, колокол)
    't:tool:furn', # мебель (стол, диван, шкаф)
    't:tool:dish', # посуда (чашка, кастрюля, фляжка)
    't:tool:cloth', # одежда и обувь (платье, шляпа, ботинки)
    't:food', # еда и напитки (пирог, каша, молоко)
    't:text', # тексты (рассказ, книга, афиша)
    't:action', # мероприятие (аукцион, вернисаж, вечеринка, выборы, именины, заседание, культпоход)
    't:be', # бытийная сфера (жить, возникнуть, убить)
    't:be:exist', # существование (жизнь, наличие, бытие; жить, происходить)
    't:be:appear', # начало существования (возникновение, рождение, формирование, учреждение, творение; возникнуть, родиться, сформировать, создать)
    't:be:disapp', # прекращение существования (смерть, казнь, ликвидация; умереть, убить, улетучиться, ликвидировать, искоренить)
    't:behav', # поведение и поступки человека (разгильдяйство, подхалимаж, неповиновение, ребячество, предательство; куролесить, привередничать)
    't:changest', # изменение состояния или признака (укрепление, затвердение, осушение, конденсация, осложнение; взрослеть, богатеть, расширить, испачкать)
    't:color', # цвет (окраска, колорит, желтизна, прозелень)
    't:contact', # контакт и опора (прикосновение, объятие; касаться, обнимать, облокотиться)
    't:dir', # направление (туда, наверх, обратный, подветренный)
    't:dist', # расстояние (далеко, близко, далекий, соседний)
    't:dist:max', # большое (далеко, вдали, вдалеке, дальний, отдаленный)
    't:dist:min', # малое (близко, вблизи, близкий, недалекий)
    't:move', # движение (беготня, вынос, качка; бежать, дергаться, бросить, нести)
    't:move:body', # изменение положения тела, части тела (поклон; согнуть, нагнуться, примоститься)
    't:put', # помещение объекта (размещение, расстановка, погрузка, намотка)
    't:impact', # физическое воздействие (удар, втирание, обмолот)
    't:impact:creat', # создание физического объекта (лепка, отливка, плетение, сооружение, строительство)
    't:impact:destr', # уничтожение (слом, сожжение)
    't:loc', # местонахождение (местоположение; лежать, стоять, положить)
    't:loc:body', # положение тела в пространстве (лежание; сидеть)
    't:poss', # посессивная сфера (обладание, приобретение, покупка, потеря, лишение; иметь дать, подарить, приобрести, лишиться)
    't:ment', # ментальная сфера (знание, абстракция, воображение, воспоминание, догадка; знать, верить, догадаться, помнить, считать)
    't:perc', # восприятие (осязание, слух, видимость, взгляд, зрелище; смотреть, слышать, нюхать, чуять)
    't:psych', # психическая сфера (апатия, безумие, вдохновение, спокойствие; гипнотизировать, сочувствовать, настроиться, терпеть)
    't:psych:emot', # эмоция (восторг, раскаяние, печаль; радоваться, обидеть)
    't:psych:volit', # воля (намерение, решение; решить)
    't:speech', # речь (дискуссия, молва, ахинея, реплика, подковырка; говорить, советовать, спорить, каламбурить)
    't:physiol', # физиологическая сфера (жажда, кровоизлияние, судорога, утомление, икота; кашлять, икать)
    't:weather', # природное явление (зарница, вьюга, зной; бушевать, вьюжить)
    't:sound', # звук (шум, перезвон, хлопок, аплодисменты, диссонанс; гудеть, шелестеть)
    't:light', # свет (луч, полумрак, светлынь, иллюминация; гаснуть, лучиться)
    't:taste', # вкус (вкуснота, горчинка, кислятина)
    't:smell', # запах (аромат, перегар; пахнуть, благоухать)
    't:temper', # температура (прохлада, стужа, нагрев)
    't:physq', # физические свойства (мягкий, вязкий)
    't:physq:form', # форма (кривой, круглый)
    't:physq:color', # цвет (красный, бесцветный)
    't:physq:taste', # вкус (кислый, приторный)
    't:physq:smell', # запах (ароматный, тухлый)
    't:physq:temper', # температура (горячий, ледяной)
    't:physq:weight', # вес (тяжелый, легкий)
    't:speed', # скорость (быстро, медленно, проворный)
    't:speed:max', # большая (быстро, мигом, скорый, быстрый)
    't:speed:min', # малая (медленно, неторопливо, медленный, тягучий)
    't:quant', # количество (столько, достаточно, большой, достаточный, трехкратный)
    't:quant:max', # большое (много, навалом, обильный, многочисленный)
    't:quant:min', # малое (мало, чуть-чуть, ничтожный, малочисленный)
    't:quant:abs', # абсолютное (двухтысячный, восьмимилионный)
    't:size', # размер (высокий, короткий)
    't:size:max', # большой (высокий, длинный)
    't:size:min', # малый (низкий, короткий)
    't:size:abs', # абсолютный (двухэтажный)
    't:time', # время (тогда, поздно; весна, годовщина, минута, современность; прошлый, ночной)
    't:time:dur', # длительность (вечно, недолго; долгий, краткий)
    't:time:dur:max', # большая (вечно, подолгу, всегда; долгий, продолжительный)
    't:time:dur:min', # малая (временно, недолго; краткий, кратковременный)
    't:time:dur:abs', # абсолютная (восьмичасовой)
    't:time:period', # период (межсезонье, путина, сенокос, стаж)
    't:time:moment', # момент (миг, мгновение)
    't:time:week', # день недели (понедельник)
    't:time:month', # месяц (январь)
    't:time:age', # возраст (детство, молодость, двадцатилетие; зрелый)
    't:time:age:max', # большой (старый, древний)
    't:time:age:min', # малый (молодой, малолетний)
    't:time:age:abs', # абсолютный (трехлетний)
    't:humq', # свойство/качества человека (порядочность, безволие, остроумие; умный, верный, ловкий)
    't:inter', # взаимодействие и взаимоотношение (взаимопомощь, вражда, схватка, драка)
    't:disease', # болезнь (ангина, диабет)
    't:game', # игра (жмурки, покер, домино, волейбол)
    't:sport', # спорт (спартакиада, акробатика, баскетбол)
    't:param', # параметр (высота, грузоподъемность)
    't:unit', # единица измерения (балл, килограмм, метр, минута)
    't:put', # помещение объекта (положить, вложить, спрятать)
    't:impact', # физическое воздействие (бить, колоть, вытирать)
    't:impact:creat', # создание физического объекта (выковать, смастерить, сшить)
    't:impact:destr', # уничтожение (взорвать, сжечь, зарезать)
    't:hum | t:hum:supernat', # лица (Людмила, Черномор)
    't:persn', # имена (Александр)
    't:patrn', # отчества (Сергеевич)
    't:famn', # фамилии (Пушкин)
    't:topon', # топонимы (Европа, Волга, Эльбрус, Москва, Преображенка)
    't:place', # место (здесь, посередине, левый, придорожный, теменной)
    )

# Мереология:
MEREOLOGY = (
    'pt:part', # части (верхушка, кончик, половина; начало, финал)
    'pt:partb & pc:hum', # части тела и органы человека (голова, сердце, ноготь)
    'pt:partb & pc:animal', # части тела и органы животных (хвост, жало)
    'pt:part & pc:plant', # части растений (лист, ветка, корень)
    'pt:part & pc:constr', # части зданий и сооружений (комната, дверь, арка)
    'pt:part & pc:tool', # части приспособлений (деталь, лопасть, крышка)
    'pt:part & pc:tool:instr', # части инструментов (топорище, лезвие)
    'pt:part & pc:tool:device', # части механизмов и приборов (дисплей, корпус, кнопка)
    'pt:part & pc:tool:transp', # части транспортных средств (руль, колесо, капот)
    'pt:part & pc:tool:weapon', # части оружия (дуло, курок, эфес)
    'pt:part & pc:tool:mus', # части музыкальных инструментов (струна, гриф)
    'pt:part & pc:tool:furn', # части предметов мебели (сиденье, подлокотник)
    'pt:part & pc:tool:dish', # части предметов посуды (носик, горлышко)
    'pt:part & pc:tool:cloth', # части одежды и обуви (рукав, каблук)
    'pt:qtm', # кванты и порции вещества (капля, комок, порция; оборот, прыжок, кивок)
    'pt:set', # множество (система, выборка, алгоритм)
    'pt:set | pt:aggr', # множества и совокупности объектов (набор, букет, мебель, человечество)
    'hi:class', # имена классов (животное, ягода, инструмент)
    )

# Топология:
TOPOLOGY = (
    'top:contain', # вместилища (кошелек, комната, озеро, ниша)
    'top:horiz', # горизонтальные поверхности (пол, площадка)
    )

# Оценка:
EVALUATION = (
    'ev', # оценка (неопределенная по признаку «положительная/отрицательная») (озорник, махина)
    'ev:posit', # положительная (умница, светило)
    'ev:neg', # отрицательная (негодяй, вертихвостка)
    )

# Словообразовательные пометы
DERIVATIONAL_TAGS = (
    'd:dim', # диминутивы (зайчик, коробочка; Саша, Женечка, Николаич; тихонький, крохотный; немножко, быстренько)
    'd:aug', # аугментативы (детина, домище; здоровенный, злющий)
    'd:sing', # сингулятивы (пылинка, изюминка)
    'd:nag', # nomina agentis (писатель, создатель, докладчик)
    'd:fem', # nomina feminina (немка, генеральша, доярка)
    'd:pref', # приставочные глаголы (забегать, оглядеть)
    'd:semelf', # семельфактивы (кивнуть, чихнуть, боднуть, качнуться)
    'd:impf', # вторичные имперфективы (-ива-, -ва-, -а-) (выпивать, вбивать, прогонять)
    'der:v', # отглагольные имена/прилагательные/наречия (выбор, демонстрация; ковкий, навязчивый, кочевой; отродясь, стоймя)
    'der:a', # отадъективные имена/наречия (краснота, жадность; быстро, обычно)
    'der:adv', # отадвербиальные прилагательные (поздний, здешний)
    'd:atten', # аттенуативы (угловатый, жуликоватый; рановато, суховато)
    'd:habit', # хабитивы (глазастый, пузатый)
    'd:carit', # каритивы (безглазый, бездыханный)
    'd:potent | d:impot', # потенциальные (плавучий, недееспособный)
    'd:potent', # поссибилитивы (плавучий, плодородный, занимательный)
    'd:impot', # импоссибилитивы (несоизмеримый, недееспособный)
    'der:s', # отыменные прилагательные/наречия (домашний, железный; вверху, дома)
    )


Имена числительные (NUM, A-NUM)

Местоимения, в том числе:
S-PRO', # местоимения-существительные (он, кто)
A-PRO', # местоимения-прилагательные (его, какой)
ADV-PRO', # местоимения-наречия (где, как)


# Каузация:
CAUSATIVITY = (
    'ca:caus', # каузативные глаголы (показать, вертеть)
    'ca:noncaus', # некаузативные глаголы (видеть, вертеться)
    )

# Служебные глаголы:
AUXILIARY_VERBS = (
    'aux:phase', # фазовые (начать, продолжать, прекратить)
    'aux:caus', # служебные каузативные (вызвать, привести (к))
    )



Наречия (ADV)

Таксономия производящего слова-прилагательного
der:a & dt:size', # размер (высоко, коротко)
der:a & dt:size:max', # большой (высоко, бесконечно)
der:a & dt:size:min', # малый (коротко, низко)
der:a & dt:physq', # физические свойства (твердо, плотно)
der:a & dt:physq:form', # форма (плоско, прямо)
der:a & dt:physq:color', # цвет (красно, добела)
der:a & dt:physq:taste', # вкус (горько, вкусно)
der:a & dt:physq:smell', # запах (смрадно, зловонно)
der:a & dt:physq:temper', # температура (тепло, прохладно)
der:a & dt:physq:weight', # вес (тяжело, легко)
der:a & dt:humq', # качества человека (внимательно, грубо)
"""
