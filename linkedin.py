from dotenv import load_dotenv

load_dotenv()  # carrega ANTHROPIC_API_KEY do .env

import pandas as pd
import requests
import re
from collections import Counter
from linkedin_api import Linkedin
import time
import random
import os
from requests.cookies import RequestsCookieJar

# Login por cookies da sessão do navegador (login por senha dispara CHALLENGE)
jar = RequestsCookieJar()
jar.set("li_at", os.environ["LI_AT"], domain=".linkedin.com")
jar.set("JSESSIONID", os.environ["JSESSIONID"], domain=".linkedin.com")
api = Linkedin("", "", cookies=jar)

# Status no terminal: uma linha por requisição à API (cada página da busca também passa por aqui)
_fetch = api._fetch
_n = 0
def _fetch_verbose(uri, *a, **kw):
    global _n
    _n += 1
    print(f"[req {_n}] {uri.split('?')[0]} ...", end=" ", flush=True)
    res = _fetch(uri, *a, **kw)
    print(res.status_code, flush=True)
    return res
api._fetch = _fetch_verbose

print("Buscando vagas (pode levar alguns minutos)...", flush=True)

# data = api.search_jobs(job_title=["backend","back end","back-end", "software", "front-end", "frontend", "front end", "mobile", "fullstack", "full-stack"],location_name="United States")
# data = api.search_jobs(job_title=["backend","back end","back-end", "software", "front-end", "frontend", "front end", "mobile", "fullstack", "full-stack"],location_name="Brazil")

# Try alternative location formats for United States
# Option 1: Using location_name with full country name
# data = api.search_jobs(job_title=["fullstack", "full-stack", "full stack"], location_name="United States")

# Option 2: Without location to see all results
# data = api.search_jobs(job_title=["fullstack", "full-stack", "full stack"])

# Option 3: Using keywords parameter (recommended for broader search)
data = api.search_jobs(
    keywords="full stack OR fullstack OR full-stack OR desenvolvedor de software OR engenheiro de software OR desenvolvedor web OR backend OR back-end OR frontend OR front-end", 
    location_name="Belo Horizonte",
    limit=1000,
)

# Alternative: Try specific cities or regions
# data = api.search_jobs(job_title=["fullstack", "full-stack", "full stack"], location_name="New York, United States")
# data = api.search_jobs(job_title=["fullstack", "full-stack", "full stack"], location_name="San Francisco Bay Area")

# data = api.search_jobs(job_title=["backend","back end","back-end", "software", "front-end", "frontend", "front end", "mobile", "fullstack", "full-stack"],location_name="Belo Horizonte")
# data = api.search_jobs(job_title=["backend","back end","back-end", "software", "front-end", "frontend", "front end", "mobile", "fullstack", "full-stack"],location_name="Canada")
# data = api.search_jobs(job_title=["full-stack", "fullstack", "full stack","nest", "nestjs", "nest.js", "node","nodejs","node js", "node.js"],location_name="Brazil")

print(f"Search returned {len(data)} job listings")
df = pd.DataFrame(data)

df['job_id'] = df['trackingUrn'].str.split(':').str[-1]
 
from terms import build_prompt, extract_terms

MIN_JOBS = 3  # ignora palavras que aparecem em menos vagas
MAX_SHARE = 0.5  # ignora palavras em mais da metade das vagas (de, com, experiencia...)


def fetch_job_details(job_id):
    try:
        time.sleep(random.uniform(0.5, 1.5))  # evita rate limiting
        return api.get_job(job_id)
    except KeyError:
        return {}
    except Exception as e:
        print(f"Error fetching job {job_id}: {str(e)}")
        return {}


print(f"Processing {len(df['job_id'])} jobs...")
job_terms = []  # conjunto de palavras por vaga
for i, job_id in enumerate(df['job_id'], 1):
    if i % 50 == 0:
        print(f"Processed {i}/{len(df['job_id'])} jobs...")
    text = (fetch_job_details(job_id).get("description") or {}).get("text", "")
    if text:
        job_terms.append(extract_terms(text))

n_jobs = len(job_terms)
print(f"\nJobs with descriptions: {n_jobs}")

freq = Counter(k for terms in job_terms for k in terms)
frequent = {k: c for k, c in freq.most_common(1500) if MIN_JOBS <= c <= MAX_SHARE * n_jobs}

prompt = build_prompt(Counter(frequent), n_jobs)
out = f"linkedin_prompt_{time.strftime('%Y%m%d_%H%M%S')}.txt"
open(out, "w").write(prompt)
print(prompt)
print(f"Prompt salvo em: {out}")
