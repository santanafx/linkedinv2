import pandas as pd
import requests
import re
from collections import Counter
from linkedin_api import Linkedin
import time
import random

# Function to create LinkedIn API connection with retry logic
def create_linkedin_connection(username, password, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to LinkedIn (attempt {attempt + 1}/{max_retries})...")
            api = Linkedin(username, password)
            print("Successfully connected to LinkedIn!")
            return api
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            if "CHALLENGE" in str(e):
                print("\nLinkedIn Challenge detected. This can happen due to:")
                print("1. Too many automated requests")
                print("2. LinkedIn's security measures")
                print("3. Account flagged for suspicious activity")
                print("\nPossible solutions:")
                print("- Wait a few hours/days before trying again")
                print("- Use a different LinkedIn account")
                print("- Try logging into LinkedIn manually through a browser first")
                print("- Consider using LinkedIn's official API with proper authentication")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 30  # Exponential backoff
                    print(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached. Exiting...")
                    return None
            else:
                print(f"Unexpected error: {str(e)}")
                return None
    return None

# Try to establish connection
api = create_linkedin_connection("santanafx@gmail.com", "Lucas4215")

# Only proceed if connection was successful
if api is None:
    print("Could not establish LinkedIn connection. Exiting...")
    exit(1)

# data = api.search_jobs(job_title=["backend","back end","back-end", "software", "front-end", "frontend", "front end", "mobile", "fullstack", "full-stack"],location_name="United States")
# data = api.search_jobs(job_title=["backend","back end","back-end", "software", "front-end", "frontend", "front end", "mobile", "fullstack", "full-stack"],location_name="Brazil")

# Try alternative location formats for United States
# Option 1: Using location_name with full country name
# data = api.search_jobs(job_title=["fullstack", "full-stack", "full stack"], location_name="United States")

# Option 2: Without location to see all results
# data = api.search_jobs(job_title=["fullstack", "full-stack", "full stack"])

# Option 3: Using keywords parameter (recommended for broader search)
data = api.search_jobs(
    keywords="fullstack OR full-stack OR full stack", 
    location_name="Belo Horizonte"
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
 
keywords = [
  # Linguagens
  "javascript", "typescript",
  "python", "java", "golang", "rust",
  "c#", "csharp", "c sharp",
  "php", "ruby", "kotlin", "scala",
  "c++", "cpp", "swift", "dart",

  # Backend / APIs
  "node", "nodejs", "node.js",
  "express", "fastify",
  "nest", "nestjs", "nest.js",
  "spring", "spring boot", "springboot",
  "django", "flask", "fastapi",
  "ruby on rails", "rails", "rubyonrails", "ruby-on-rails",
  "laravel", "symfony",
  ".net", ".net core", "dotnet", "dotnet core",
  "asp.net", "aspnet", "asp net", "asp net core", "typeorm", "type orm", "prisma", "sequelize",

  # Frontend
  "react", "reactjs", "react.js", "react js",
  "redux", "vue", "vuejs", "vue.js", "vue js",
  "angular",
  "svelte",
  "next", "nextjs", "next.js",
  "astro",

  # Mobile
  "react native", "react-native", "reactnative",
  "flutter",
  "android", "ios",
  "swiftui", "jetpack compose",

  # Banco de dados
  "postgres", "postgresql",
  "mysql", "mariadb",
  "mongodb", "redis",
  "oracle", "sql server",
  "elasticsearch",
  "neo4j", "cassandra",

  # Cloud & DevOps
  "aws", "azure", "gcp", "google cloud",
  "docker", "kubernetes", "k8s",
  "terraform", "ansible", "puppet", "chef",
  "ci/cd", "github actions", "gitlab ci", "jenkins",
  "prometheus", "grafana",
  "serverless",

  # Testes
  "jest", "mocha", "chai",
  "pytest", "junit",
  "cypress", "playwright",
  "selenium", "appium",
  "tdd", "bdd",

  # APIs / Protocolos
  "rest", "restful",
  "graphql", "graph ql",
  "gRPC",
  "webhooks",

  # Arquitetura / Conceitos
  "microservices", "microserviços",
  "clean architecture",
  "ddd", "solid",
  "event driven", "event-driven",

  # Data / Big Data
  "spark", "hadoop",
  "kafka", "airflow",
  "etl", "data engineering",
  "data science", "tableau", "power bi",

  # AI / Machine Learning
  "tensorflow", "pytorch",
  "scikit-learn", "mlops",
  "llm", "large language models",
  "prompt engineering",

  # Blockchain / Web3
  "solidity", "ethereum",
  "web3", "hardhat", "truffle",
  "polygon", "solana",

  # Ferramentas variadas
  "git", "github", "gitlab",
  "excel",
  "n8n",

  # Senioridade
  "junior", "júnior",
  "pleno", "mid", "middle",
  "senior", "sênior"
]
# keywords = ["golang", "go", "senior", "junior", "pleno", "mid"]
# keywords = ["ruby","ruby on rails","ruby-on-rails", "senior", "junior", "pleno", "mid"]
# keywords = ["spring","spring boot","java", "senior", "junior", "pleno", "mid"]
# keywords = ["nest", "nestjs", "nest.js", "node","nodejs","node js", "node.js", "senior", "junior", "pleno", "mid"]
# keywords = [".net", ".net core", "dot net", "dotnet", "asp.net", "senior", "junior", "pleno", "mid"]
# keywords = ["php", "laravel", "senior", "junior", "pleno", "mid"]

keyword_counts = Counter()

def fetch_job_details(job_id):
    try:
        # Add a small delay to avoid rate limiting
        time.sleep(random.uniform(0.5, 1.5))
        response = api.get_job(job_id)
    except KeyError:
        return {}
    except Exception as e:
        print(f"Error fetching job {job_id}: {str(e)}")
        return {}
    if 'message' in response:
        return response
    return response

print(f"Processing {len(df['job_id'])} jobs...")
processed_count = 0
jobs_with_descriptions = 0
total_description_length = 0

for job_id in df['job_id']:
    processed_count += 1
    if processed_count % 50 == 0:  # Reduzir frequência de logs
        print(f"Processed {processed_count}/{len(df['job_id'])} jobs...")
    
    details = fetch_job_details(job_id)
    if not details:
        continue
        
    description_text = details.get("description", {}).get("text", "")
    if description_text:
        jobs_with_descriptions += 1
        total_description_length += len(description_text)
        
        # Normalizar texto - remover acentos e converter para lowercase
        import unicodedata
        description_text = unicodedata.normalize('NFD', description_text)
        description_text = ''.join(c for c in description_text if unicodedata.category(c) != 'Mn')
        description_text = description_text.lower()
        
        # Debug: mostrar algumas descrições para verificar o conteúdo
        if processed_count <= 3:
            print(f"\nSample description {processed_count} (first 200 chars):")
            print(description_text[:200] + "...")
        
        for keyword in keywords:
            # Normalizar keyword também
            import unicodedata
            keyword_normalized = unicodedata.normalize('NFD', keyword)
            keyword_normalized = ''.join(c for c in keyword_normalized if unicodedata.category(c) != 'Mn')
            keyword_lower = keyword_normalized.lower()
            
            # Busca mais flexível - considera múltiplas variações
            matches = 0
            
            # 1. Busca exata da substring
            matches += description_text.count(keyword_lower)
            
            # 2. Busca com espaços/pontuação ao redor (mais flexível que \b)
            patterns = [
                fr'[\s\.,;:\-\(\)]{re.escape(keyword_lower)}[\s\.,;:\-\(\)]',  # com pontuação
                fr'^{re.escape(keyword_lower)}[\s\.,;:\-\(\)]',  # início da string
                fr'[\s\.,;:\-\(\)]{re.escape(keyword_lower)}$',  # final da string
                fr'^{re.escape(keyword_lower)}$'  # palavra única
            ]
            
            for pattern in patterns:
                matches += len(re.findall(pattern, description_text))
            
            # 3. Para keywords compostas, também buscar sem espaços/hífen
            if ' ' in keyword_lower or '-' in keyword_lower or '.' in keyword_lower:
                # Remove espaços, hífens e pontos para busca alternativa
                alt_keyword = keyword_lower.replace(' ', '').replace('-', '').replace('.', '')
                matches += description_text.count(alt_keyword)
            
            keyword_counts[keyword] += matches

print(f"\nStatistics:")
print(f"Total jobs processed: {processed_count}")
print(f"Jobs with descriptions: {jobs_with_descriptions}")
print(f"Average description length: {total_description_length // max(jobs_with_descriptions, 1)} characters")

# Filtrar apenas keywords com contagem > 0 e ordenar
keyword_df = pd.DataFrame(keyword_counts.items(), columns=['Keyword', 'Count'])
keyword_df = keyword_df[keyword_df['Count'] > 0].sort_values(by='Count', ascending=False)

print(f"\nKeyword Analysis (showing only keywords found):")
print(keyword_df.to_string(index=False))

# Salvar resultados em CSV
timestamp = time.strftime("%Y%m%d_%H%M%S")
csv_filename = f"linkedin_keyword_analysis_{timestamp}.csv"
keyword_df.to_csv(csv_filename, index=False)
print(f"\nResults saved to: {csv_filename}")

# Análise adicional
print(f"\nTop 10 technologies:")
tech_keywords = [k for k in keywords if k not in ["senior", "junior", "pleno", "mid"]]
tech_df = keyword_df[keyword_df['Keyword'].isin(tech_keywords)].head(10)
print(tech_df.to_string(index=False))

print(f"\nSeniority levels:")
seniority_keywords = ["senior", "junior", "pleno", "mid"]
seniority_df = keyword_df[keyword_df['Keyword'].isin(seniority_keywords)]
print(seniority_df.to_string(index=False))