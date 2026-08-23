"""
RASTRO — protótipo local
Flask + HTML + CSS + JS puro.

A versão abaixo reproduz a direção visual do mockup:
sidebar no desktop, bottom-nav no celular, cards em glassmorphism,
TALK → barreira → 1% → WORLD → PERFIL e SECRET.

Os dados ficam em memória de propósito para o protótipo.
"""

from flask import Flask, render_template, request, jsonify
import uuid

app = Flask(__name__)
app.secret_key = "rastro-dev-secret"

STATE = {
    "points": 20,
    "purchased_elements": [0],
    "completed_steps": 0,
    "barriers_overcome": 2,
    "checkins": 1,
    "current_mood": "mais ou menos",
    "current_objective": "estudos",
    "current_barrier": "não sei por onde começar",
    "pattern": "Você parece avançar melhor quando transforma algo grande em um primeiro passo pequeno.",
    "goals": [
        {"id": 1, "text": "Abrir o material de estudo e escolher apenas uma questão", "tag": "começo", "done": False},
        {"id": 2, "text": "Ler o enunciado da primeira questão sem tentar resolver tudo", "tag": "foco", "done": False},
        {"id": 3, "text": "Estudar por 10 minutos sem exigir terminar o conteúdo", "tag": "progresso", "done": False},
    ],
    "secret_posts": [
        {"id": 1, "text": "Achei que era a única pessoa que travava quando tinha coisa demais para fazer.", "hearts": 12},
        {"id": 2, "text": "Descobri que começar pequeno funciona melhor para mim do que tentar mudar tudo de uma vez.", "hearts": 27},
    ],
}

WORLD_ELEMENTS = [
    (0, "🌱", "Seu primeiro passo"),
    (15, "🪴", "Uma pequena constância"),
    (30, "🌳", "Uma barreira atravessada"),
    (50, "🏡", "Um espaço que começa a ser seu"),
    (75, "🐦", "Mais movimento no seu mundo"),
    (105, "🌸", "Seu rastro está florescendo"),
]

MOOD_OPTIONS = ["muito mal", "mal", "mais ou menos", "bem", "muito bem"]

OBJECTIVE_RULES = {
    "estudos": ["estud", "enem", "prova", "faculdade", "matéria", "lição", "escola", "vestibular", "nota"],
    "trabalho": ["emprego", "trabalh", "vaga", "currículo", "entrevista", "estágio", "carreira", "chefe"],
    "dinheiro": ["dinheiro", "gasto", "gastar", "econom", "guardar", "dívida", "financeir", "salário", "orçamento"],
    "rotina": ["rotina", "organizar", "organiza", "horário", "tempo", "casa", "quarto", "tarefas", "procrastin"],
    "projeto pessoal": ["projeto", "ideia", "criar", "aprender", "curso", "hobby", "portfólio", "empreender"],
    "relações": ["amigo", "amizade", "família", "famili", "namoro", "relacion", "sozinh", "conversar com alguém"],
    "bem-estar": ["cansad", "sono", "dormir", "exerc", "aliment", "energia", "descans", "ansios", "estress", "estresse"],
}

BARRIER_RULES = {
    "não sei por onde começar": ["não sei por onde", "perdid", "não sei como", "não sei o que fazer", "sem direção", "por onde", "não sei começar"],
    "falta de tempo": ["sem tempo", "não tenho tempo", "tempo", "correria", "horário", "ocupad"],
    "distração": ["celular", "distra", "instagram", "tiktok", "procrastin", "não consigo focar", "foco"],
    "tarefa parece grande demais": ["muita coisa", "grande demais", "sobrecarreg", "não dou conta", "coisa demais", "tudo ao mesmo tempo", "complicado"],
    "falta de energia": ["cansad", "sem energia", "exaust", "esgot", "sem força", "sono", "desanim"],
    "medo de não conseguir": ["medo", "fracass", "não vou conseguir", "não sou capaz", "insegur", "vergonha"],
    "preciso de companhia": ["sozinh", "solidão", "ninguém", "isolad", "não tenho com quem", "companhia"],
}

BARRIER_OPTIONS = [
    "não sei por onde começar",
    "falta de tempo",
    "distração",
    "tarefa parece grande demais",
    "falta de energia",
    "medo de não conseguir",
    "preciso de companhia",
]

GOAL_TEMPLATES = {
    "estudos": {
        "não sei por onde começar": [
            ("Abrir o material e escolher apenas uma questão", "começo"),
            ("Ler o enunciado da primeira questão", "foco"),
            ("Estudar por 10 minutos sem exigir terminar", "progresso"),
        ],
        "falta de tempo": [
            ("Reservar 10 minutos para uma única matéria", "tempo"),
            ("Escolher a tarefa mais importante do dia", "prioridade"),
            ("Encerrar os 10 minutos registrando o que avançou", "progresso"),
        ],
        "distração": [
            ("Deixar o celular longe por 10 minutos", "foco"),
            ("Abrir somente o material que você vai usar", "ambiente"),
            ("Fazer uma questão antes de olhar outra tela", "começo"),
        ],
        "tarefa parece grande demais": [
            ("Dividir o conteúdo em uma única questão", "começo"),
            ("Estudar só a primeira parte, sem tentar terminar tudo", "ação"),
            ("Marcar o que você conseguiu entender", "progresso"),
        ],
        "falta de energia": [
            ("Beber água e fazer uma pausa curta", "corpo"),
            ("Escolher uma tarefa de estudo que leve 5 minutos", "energia"),
            ("Parar depois do primeiro pequeno avanço se precisar", "cuidado"),
        ],
        "medo de não conseguir": [
            ("Escolher uma questão fácil para começar", "coragem"),
            ("Tentar por 5 minutos sem buscar perfeição", "tentativa"),
            ("Anotar uma coisa que você descobriu tentando", "reflexão"),
        ],
        "preciso de companhia": [
            ("Mandar mensagem para alguém para estudar junto", "conexão"),
            ("Combinar 15 minutos de estudo acompanhado", "companhia"),
            ("Contar depois o que você conseguiu fazer", "progresso"),
        ],
    },
    "trabalho": {
        "não sei por onde começar": [
            ("Abrir uma única vaga compatível com você", "começo"),
            ("Anotar uma habilidade que você já possui", "clareza"),
            ("Dar um pequeno passo no currículo", "ação"),
        ],
        "falta de tempo": [
            ("Separar 10 minutos para procurar uma vaga", "tempo"),
            ("Escolher apenas uma plataforma para olhar hoje", "prioridade"),
            ("Salvar uma oportunidade interessante", "progresso"),
        ],
        "distração": [
            ("Abrir somente a página de vagas que você escolheu", "foco"),
            ("Pesquisar por 10 minutos sem alternar de aplicativo", "foco"),
            ("Salvar uma vaga antes de sair", "ação"),
        ],
        "tarefa parece grande demais": [
            ("Escrever apenas o título do seu currículo", "começo"),
            ("Escolher três habilidades para destacar", "ação"),
            ("Revisar uma única parte do currículo", "progresso"),
        ],
        "falta de energia": [
            ("Fazer uma pausa e beber água antes de começar", "cuidado"),
            ("Escolher uma tarefa profissional de 5 minutos", "energia"),
            ("Encerrar quando o pequeno passo estiver concluído", "limite"),
        ],
        "medo de não conseguir": [
            ("Encontrar uma vaga em que você cumpra parte dos requisitos", "coragem"),
            ("Escrever uma frase sobre o que você sabe fazer", "confiança"),
            ("Salvar a vaga sem se obrigar a enviar hoje", "tentativa"),
        ],
        "preciso de companhia": [
            ("Pedir para alguém revisar uma parte do seu currículo", "conexão"),
            ("Conversar com alguém sobre uma área que interessa", "companhia"),
            ("Registrar uma dica que recebeu", "progresso"),
        ],
    },
    "dinheiro": {
        "não sei por onde começar": [
            ("Registrar um único gasto de hoje", "começo"),
            ("Anotar quanto entrou e quanto saiu este mês", "clareza"),
            ("Escolher uma pequena despesa para observar", "consciência"),
        ],
        "falta de tempo": [
            ("Separar 5 minutos para registrar seus gastos", "tempo"),
            ("Anotar apenas as três últimas compras", "prioridade"),
            ("Escolher um gasto para acompanhar esta semana", "progresso"),
        ],
        "distração": [
            ("Abrir sua lista de gastos antes de qualquer rede social", "foco"),
            ("Registrar uma compra assim que ela acontecer", "atenção"),
            ("Fechar o aplicativo depois de completar o registro", "limite"),
        ],
        "tarefa parece grande demais": [
            ("Anotar somente os gastos de hoje", "começo"),
            ("Separar gastos em duas categorias", "clareza"),
            ("Escolher uma categoria para observar", "progresso"),
        ],
        "falta de energia": [
            ("Fazer uma pausa e depois registrar apenas um gasto", "cuidado"),
            ("Escolher a parte mais simples do orçamento", "energia"),
            ("Parar depois de organizar uma única informação", "limite"),
        ],
        "medo de não conseguir": [
            ("Escolher uma pequena economia possível esta semana", "coragem"),
            ("Registrar sem julgamento um gasto que aconteceu", "consciência"),
            ("Anotar uma mudança que seria realista", "progresso"),
        ],
        "preciso de companhia": [
            ("Conversar com alguém de confiança sobre uma meta financeira", "conexão"),
            ("Pedir ajuda para organizar uma categoria", "companhia"),
            ("Anotar uma dica que recebeu", "progresso"),
        ],
    },
    "rotina": {
        "não sei por onde começar": [
            ("Escolher uma única tarefa para hoje", "começo"),
            ("Colocar essa tarefa em um horário específico", "clareza"),
            ("Fazer só os primeiros 5 minutos", "ação"),
        ],
        "falta de tempo": [
            ("Escolher uma tarefa que caiba em 10 minutos", "tempo"),
            ("Bloquear 10 minutos no seu horário", "prioridade"),
            ("Deixar o próximo passo preparado", "progresso"),
        ],
        "distração": [
            ("Deixar o celular fora do alcance por 10 minutos", "foco"),
            ("Começar uma tarefa antes de abrir outra tela", "começo"),
            ("Usar um cronômetro de 10 minutos", "atenção"),
        ],
        "tarefa parece grande demais": [
            ("Escolher apenas uma parte da tarefa", "começo"),
            ("Fazer a menor ação possível", "ação"),
            ("Parar para reconhecer o que já mudou", "progresso"),
        ],
        "falta de energia": [
            ("Escolher uma tarefa que leve 5 minutos", "energia"),
            ("Beber água e fazer uma pausa curta", "cuidado"),
            ("Deixar uma tarefa pronta para amanhã", "continuidade"),
        ],
        "medo de não conseguir": [
            ("Criar uma versão pequena da rotina", "coragem"),
            ("Testar a nova rotina por apenas um dia", "tentativa"),
            ("Anotar o que funcionou", "reflexão"),
        ],
        "preciso de companhia": [
            ("Convidar alguém para fazer a tarefa junto", "conexão"),
            ("Contar a alguém qual pequena tarefa você quer concluir", "companhia"),
            ("Compartilhar depois que terminou", "progresso"),
        ],
    },
    "projeto pessoal": {
        "não sei por onde começar": [
            ("Escrever em uma frase o que você quer criar", "clareza"),
            ("Escolher a primeira ação do projeto", "começo"),
            ("Trabalhar nele por 10 minutos", "ação"),
        ],
        "falta de tempo": [
            ("Separar 10 minutos para o projeto", "tempo"),
            ("Escolher uma única entrega pequena", "prioridade"),
            ("Salvar o próximo passo para continuar depois", "progresso"),
        ],
        "distração": [
            ("Abrir somente a ferramenta do projeto", "foco"),
            ("Trabalhar por 10 minutos sem alternar de aplicativo", "atenção"),
            ("Salvar o que foi feito", "progresso"),
        ],
        "tarefa parece grande demais": [
            ("Transformar o projeto em uma tarefa de 5 minutos", "começo"),
            ("Fazer apenas a primeira parte", "ação"),
            ("Registrar o que já existe", "progresso"),
        ],
        "falta de energia": [
            ("Escolher uma parte leve do projeto", "energia"),
            ("Fazer uma pausa curta antes de começar", "cuidado"),
            ("Encerrar após um pequeno avanço", "limite"),
        ],
        "medo de não conseguir": [
            ("Criar uma versão simples do projeto", "coragem"),
            ("Testar uma ideia sem exigir que fique perfeita", "tentativa"),
            ("Anotar o que aprendeu", "reflexão"),
        ],
        "preciso de companhia": [
            ("Mostrar a ideia para alguém de confiança", "conexão"),
            ("Pedir uma opinião sobre o primeiro passo", "companhia"),
            ("Registrar uma sugestão útil", "progresso"),
        ],
    },
    "relações": {
        "não sei por onde começar": [
            ("Escrever o que você gostaria de conseguir dizer", "clareza"),
            ("Escolher uma pessoa segura para conversar", "conexão"),
            ("Enviar uma mensagem curta e honesta", "ação"),
        ],
        "falta de tempo": [
            ("Separar 5 minutos para responder alguém importante", "tempo"),
            ("Mandar uma mensagem simples", "conexão"),
            ("Marcar um momento para conversar depois", "progresso"),
        ],
        "distração": [
            ("Guardar o celular e ouvir alguém por 10 minutos", "presença"),
            ("Responder uma pessoa sem alternar aplicativos", "foco"),
            ("Fazer uma pergunta e realmente escutar", "conexão"),
        ],
        "tarefa parece grande demais": [
            ("Escolher apenas uma coisa que você quer dizer", "começo"),
            ("Escrever uma frase sem enviar ainda", "clareza"),
            ("Decidir se vale continuar a conversa", "limite"),
        ],
        "falta de energia": [
            ("Dar um pequeno espaço para descansar antes de conversar", "cuidado"),
            ("Enviar uma mensagem simples em vez de explicar tudo", "energia"),
            ("Escolher o momento em que você se sente mais disponível", "limite"),
        ],
        "medo de não conseguir": [
            ("Escrever primeiro o que você gostaria que a pessoa entendesse", "coragem"),
            ("Usar uma frase começando por 'eu sinto...'", "clareza"),
            ("Escolher se quer conversar agora ou depois", "limite"),
        ],
        "preciso de companhia": [
            ("Enviar mensagem para alguém de confiança", "conexão"),
            ("Pedir companhia para uma atividade simples", "companhia"),
            ("Agradecer a pessoa que esteve presente", "progresso"),
        ],
    },
    "bem-estar": {
        "não sei por onde começar": [
            ("Escolher uma coisa simples que faria seu dia um pouco melhor", "começo"),
            ("Fazer essa ação por 5 minutos", "ação"),
            ("Anotar como você se sentiu depois", "reflexão"),
        ],
        "falta de tempo": [
            ("Separar 5 minutos para você hoje", "tempo"),
            ("Escolher uma pausa curta que realmente ajude", "cuidado"),
            ("Deixar a próxima pausa marcada", "progresso"),
        ],
        "distração": [
            ("Ficar 10 minutos sem alternar entre aplicativos", "foco"),
            ("Deixar o celular longe durante uma pausa", "presença"),
            ("Perceber o que você estava procurando ao abrir o celular", "consciência"),
        ],
        "tarefa parece grande demais": [
            ("Escolher uma mudança pequena em vez de mudar tudo", "começo"),
            ("Fazer só 5 minutos hoje", "ação"),
            ("Reconhecer o que já foi possível", "progresso"),
        ],
        "falta de energia": [
            ("Beber água e fazer uma pausa curta", "corpo"),
            ("Escolher uma ação que exija pouca energia", "energia"),
            ("Permitir que o pequeno passo seja suficiente hoje", "cuidado"),
        ],
        "medo de não conseguir": [
            ("Escolher uma mudança tão pequena que pareça possível", "coragem"),
            ("Testar por um dia, sem promessa de perfeição", "tentativa"),
            ("Anotar o que funcionou", "reflexão"),
        ],
        "preciso de companhia": [
            ("Pensar em alguém com quem você se sente seguro", "conexão"),
            ("Enviar uma mensagem simples pedindo companhia", "companhia"),
            ("Registrar como foi receber apoio", "reflexão"),
        ],
    },
}

PATTERNS = {
    "não sei por onde começar": "Você parece avançar melhor quando transforma algo grande em um primeiro passo pequeno.",
    "falta de tempo": "Você pode se beneficiar de ações curtas e específicas, em vez de esperar por um bloco perfeito de tempo.",
    "distração": "Seu desafio parece estar menos na vontade e mais em proteger sua atenção no momento de começar.",
    "tarefa parece grande demais": "Quando algo parece enorme, dividir em partes pequenas pode tornar o começo mais possível.",
    "falta de energia": "Você parece se beneficiar de passos curtos que respeitam sua energia, em vez de tentar fazer tudo de uma vez.",
    "medo de não conseguir": "Você pode avançar melhor quando troca a cobrança de acertar pela liberdade de apenas tentar.",
    "preciso de companhia": "Ter alguém por perto pode tornar alguns próximos passos mais possíveis para você.",
}


def detect_objective(text):
    normalized = (text or "").lower()
    for objective, keywords in OBJECTIVE_RULES.items():
        if any(keyword in normalized for keyword in keywords):
            return objective
    return "projeto pessoal"


def detect_barrier(text):
    normalized = (text or "").lower()
    for barrier, keywords in BARRIER_RULES.items():
        if any(keyword in normalized for keyword in keywords):
            return barrier
    return "não sei por onde começar"


def build_goals(objective, barrier):
    templates = GOAL_TEMPLATES.get(objective, GOAL_TEMPLATES["projeto pessoal"])
    return [
        {"id": index + 1, "text": text, "tag": tag, "done": False}
        for index, (text, tag) in enumerate(
            templates.get(barrier, templates["não sei por onde começar"])
        )
    ]


def unlocked_elements(points=None):
    return [(emoji, label) for cost, emoji, label in WORLD_ELEMENTS if cost in STATE["purchased_elements"]]


def world_progress(points):
    owned = len(STATE["purchased_elements"])
    total = len(WORLD_ELEMENTS)
    if owned >= total:
        return 100, 0
    locked_costs = sorted(cost for cost, *_ in WORLD_ELEMENTS if cost not in STATE["purchased_elements"])
    next_cost = locked_costs[0]
    return (owned / total) * 100, max(0, next_cost - points)


def completed_count():
    return sum(1 for goal in STATE["goals"] if goal["done"])


@app.route("/")
def home():
    progress, remaining = world_progress(STATE["points"])
    return render_template(
        "index.html",
        active="home",
        points=STATE["points"],
        completed=completed_count(),
        current_mood=STATE["current_mood"],
        current_objective=STATE["current_objective"],
        current_barrier=STATE["current_barrier"],
        pattern=STATE["pattern"],
        world_elements=unlocked_elements(STATE["points"]),
        progress=progress,
        remaining=remaining,
    )


@app.route("/talk")
def talk():
    return render_template(
        "talk.html",
        active="talk",
        objective=STATE["current_objective"],
        barrier=STATE["current_barrier"],
    )


@app.route("/world")
def world():
    progress, remaining = world_progress(STATE["points"])
    return render_template(
        "world.html",
        active="world",
        points=STATE["points"],
        elements=unlocked_elements(STATE["points"]),
        owned_costs=STATE["purchased_elements"],
        progress=progress,
        remaining=remaining,
    )


@app.route("/onepct")
def onepct():
    return render_template(
        "onepct.html",
        active="onepct",
        goals=STATE["goals"],
        completed=completed_count(),
        barrier=STATE["current_barrier"],
        objective=STATE["current_objective"],
    )


@app.route("/secret")
def secret():
    return render_template("secret.html", active="secret", posts=STATE["secret_posts"])


@app.route("/perfil")
def perfil():
    return render_template(
        "perfil.html",
        active="perfil",
        points=STATE["points"],
        completed=completed_count(),
        barriers_overcome=STATE["barriers_overcome"],
        checkins=STATE["checkins"],
        world_count=len(unlocked_elements(STATE["points"])),
        pattern=STATE["pattern"],
        barrier=STATE["current_barrier"],
        objective=STATE["current_objective"],
    )


@app.post("/api/checkin")
def api_checkin():
    data = request.get_json(force=True)
    mood = (data.get("mood") or "").strip().lower()
    if mood not in MOOD_OPTIONS:
        return jsonify({"error": "mood inválido"}), 400
    STATE["current_mood"] = mood
    STATE["checkins"] += 1
    return jsonify({"ok": True, "mood": mood, "checkins": STATE["checkins"]})


@app.post("/api/talk/answer")
def api_talk_answer():
    data = request.get_json(force=True)
    step = int(data.get("step", 0))
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "empty"}), 400

    if step == 0:
        objective = detect_objective(text)
        barrier = detect_barrier(text)
        STATE["current_objective"] = objective
        STATE["current_barrier"] = barrier
        return jsonify({
            "done": False,
            "step": 1,
            "objective": objective,
            "barrier": barrier,
            "reply": f"Entendi. Isso parece estar ligado a <strong>{objective}</strong>. Um obstáculo que apareceu no que você contou foi <strong>{barrier}</strong>.<br><br>Qual dessas barreiras representa melhor o seu momento?",
            "options": BARRIER_OPTIONS,
        })

    if step == 1:
        barrier = text if text in BARRIER_OPTIONS else STATE["current_barrier"]
        STATE["current_barrier"] = barrier
        return jsonify({
            "done": False,
            "step": 2,
            "barrier": barrier,
            "reply": f"Perfeito. Então vamos trabalhar a partir de <strong>{barrier}</strong>.<br><br>Se você pudesse deixar uma única coisa 1% melhor hoje, qual seria? Pode responder livremente.",
        })

    objective = STATE["current_objective"]
    barrier = STATE["current_barrier"]
    STATE["goals"] = build_goals(objective, barrier)
    STATE["pattern"] = PATTERNS.get(barrier, PATTERNS["não sei por onde começar"])
    return jsonify({
        "done": True,
        "step": 3,
        "objective": objective,
        "barrier": barrier,
        "reply": "Pronto. Em vez de te entregar uma lista enorme, transformei o que você contou em três pequenos passos. Eles já estão no 1%.",
        "redirect": "/onepct",
    })


@app.post("/api/goals/toggle")
def api_goals_toggle():
    data = request.get_json(force=True)
    try:
        goal_id = int(data.get("id"))
    except (TypeError, ValueError):
        return jsonify({"error": "id inválido"}), 400

    for goal in STATE["goals"]:
        if goal["id"] == goal_id:
            was_done = goal["done"]
            goal["done"] = not was_done
            STATE["points"] = max(0, STATE["points"] + (5 if goal["done"] else -5))
            if goal["done"]:
                STATE["completed_steps"] += 1
            else:
                STATE["completed_steps"] = max(0, STATE["completed_steps"] - 1)
            break

    STATE["barriers_overcome"] = max(2, 2 + STATE["completed_steps"] // 3)
    progress, remaining = world_progress(STATE["points"])
    return jsonify({
        "goals": STATE["goals"],
        "points": STATE["points"],
        "completed": completed_count(),
        "unlocked": len(unlocked_elements(STATE["points"])),
        "progress": progress,
        "remaining": remaining,
    })


@app.post("/api/world/buy")
def api_world_buy():
    data = request.get_json(force=True)
    try:
        cost = int(data.get("cost"))
    except (TypeError, ValueError):
        return jsonify({"error": "invalid"}), 400

    match = next((item for item in WORLD_ELEMENTS if item[0] == cost), None)
    if not match:
        return jsonify({"error": "not_found"}), 404
    if cost in STATE["purchased_elements"]:
        return jsonify({"error": "already_owned"}), 400
    if STATE["points"] < cost:
        return jsonify({"error": "insufficient_points"}), 400

    STATE["purchased_elements"].append(cost)
    progress, remaining = world_progress(STATE["points"])
    return jsonify({
        "ok": True,
        "points": STATE["points"],
        "label": match[2],
        "progress": progress,
        "remaining": remaining,
    })


@app.post("/api/secret/post")
def api_secret_post():
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "empty"}), 400
    if len(text) > 500:
        return jsonify({"error": "too_long"}), 400
    post = {"id": str(uuid.uuid4()), "text": text, "hearts": 0}
    STATE["secret_posts"].insert(0, post)
    return jsonify({"post": post})


@app.post("/api/secret/heart")
def api_secret_heart():
    data = request.get_json(force=True)
    post_id = data.get("id")
    for post in STATE["secret_posts"]:
        if str(post["id"]) == str(post_id):
            post["hearts"] += 1
            return jsonify({"hearts": post["hearts"]})
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    app.run(debug=False, port=5000)
