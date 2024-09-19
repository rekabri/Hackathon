from llama_index.core              import Settings
from llama_index.llms.openai       import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# Modellek inicializálása
def initialize_models():
    model = "gpt-3.5-turbo"  # Választhatsz más modellt is, pl. gpt-4 vagy gpt-4-turbo
    
    # Settings objektum beállítása az embed_model és llm modellekhez
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
    Settings.llm = OpenAI(
        temperature=0,
        model=model,
        presence_penalty=-2,  # Helyes beállítás PRESENCE_PENALTY
        top_p=1,  # TOP_P helyes beállítás
        #max_tokens=512  # Beállíthatod, ha szükséges
    )