import re
import unicodedata

TOKEN = re.compile(r"\.?[^\W\d_][\w#+]*(?:[.\-][\w#+]+)*")


def norm(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def extract_terms(text):
    """Conjunto de palavras (normalizadas) de uma descrição. Sem heurística: quem filtra é a contagem + o LLM."""
    return {k for k in map(norm, TOKEN.findall(text)) if len(k) > 1}


PROMPT = (
    "Abaixo há uma lista de termos extraídos de vagas de emprego de desenvolvimento de software, "
    "no formato 'termo: número de vagas que o citam'. Filtre e devolva SOMENTE os que fazem sentido para a "
    "demanda do mercado de tecnologia (linguagens, frameworks, bancos de dados, ferramentas, plataformas, "
    "metodologias e conceitos técnicos). Ignore empresas, cidades, idiomas, cargos genéricos e palavras comuns. "
    "Una variações do mesmo termo (ex.: 'nodejs' e 'node.js' -> Node.js) somando as contagens e devolva "
    "uma tabela ordenada da mais para a menos demandada.\n\n"
)


def build_prompt(freq, n_jobs):
    """freq: Counter termo -> nº de vagas. Retorna o prompt + a lista, pronto para colar em um chat."""
    lines = "\n".join(f"{k}: {c}" for k, c in freq.most_common())
    return f"{PROMPT}Total de vagas analisadas: {n_jobs}\n\n{lines}\n"


if __name__ == "__main__":
    t = extract_terms("Experiência com Python, node.js, Kafka/RabbitMQ, C# e .NET. javascript e docker.")
    assert {"python", "node.js", "kafka", "rabbitmq", "c#", ".net", "javascript", "docker", "experiencia"} <= t, t
    print("ok")
