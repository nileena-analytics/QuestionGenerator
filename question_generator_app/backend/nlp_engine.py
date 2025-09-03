#Importing libraries
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import torch
import re


#Loading models
try:
    qg_pipeline = pipeline(
        "text2text-generation",
        model="iarfmoose/t5-base-question-generator",
        device=-1
    )
except Exception as e:
    print("Error loading QG model:", e)
    qg_pipeline = None


try:
    sentence_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")  
except Exception as e:
    print("Error loading sentence model:", e)  
    sentence_model = None

#Choosing cosine similarity function
_cos_sim = getattr(util, "cos_sim", getattr(util, "pytorch_cos_sim", None))




def _normalize(text: str) -> str:
    #Normalization of the input
    t = text.strip().lower()
    t = re.sub(r"[^a-z0-9\s\?]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = t.replace("natural language processing", "nlp")
    t = t.replace("electricity to power our homes", "electricity usage home")
    return t

def _is_meaningful(question: str, paragraph: str, threshold: float = 0.40) -> bool:
    #Checking if question is meaningful - not vague and relevant to paragraph
    #some patterns which may indicate low quality
    vague_patterns = [
        r"what does it mean to",
        r"what does .* do",
        r"what is it",
        r"what does it mean",
        r"how does it work",
        r"what does it do",
    ]
    q_lower = question.lower()
    for pat in vague_patterns:  
        if re.search(pat, q_lower):
            return False

    try:
        #Encoding
        q_emb = sentence_model.encode(question, convert_to_tensor=True, normalize_embeddings=True)
        p_emb = sentence_model.encode(paragraph, convert_to_tensor=True, normalize_embeddings=True)
        sim = _cos_sim(q_emb, p_emb).item()
        return sim >= threshold
    except Exception:
        return True


def generate_questions(paragraph: str, num_questions: int = 5, similarity_threshold: float = 0.85):

    if not qg_pipeline:
        return ["Error: Question generator model not loaded."]
    if not sentence_model or _cos_sim is None:
        return _simple_generation_no_semantic(paragraph, num_questions)

    try:
        #Over-generate candidate questions
        task_input = f"generate questions: {paragraph}"
        num_candidates = max(num_questions * 6, 20)
        num_beams = max(num_candidates, 25)

        results = qg_pipeline(
            task_input,
            max_length=64,
            num_beams=num_beams,
            num_return_sequences=num_candidates,
            do_sample=False,
            early_stopping=True
        )

        raw = [r.get("generated_text", "").strip() for r in results]


        #Filter valid questions
        candidates = []
        for q in raw:
            if not q:
                continue
            if not q.endswith("?"):
                if any(q.lower().startswith(w) for w in ("who", "what", "when", "where", "why", "how", "which")):
                    q = q + "?"
            if q.endswith("?") and len(q.split()) >= 4:
                if _is_meaningful(q, paragraph):
                    candidates.append(q)

        if not candidates:
            return ["Could not generate good questions."]


        #Remove duplicates
        seen = set()
        surface_unique = []
        for q in candidates:
            key = _normalize(q)
            if key and key not in seen:
                seen.add(key)
                surface_unique.append(q)

        if not surface_unique:
            return ["Could not generate good questions."]


        #Semantic deduplication- remove near-duplicates using embeddings
        unique_questions = []
        kept_embs = []

        for q in surface_unique:
            q_emb = sentence_model.encode(q, convert_to_tensor=True, normalize_embeddings=True)
            if q_emb.dim() == 1:
                q_emb = q_emb.unsqueeze(0)

            if kept_embs:
                stacked = torch.cat(kept_embs, dim=0)
                sims = _cos_sim(q_emb, stacked)[0]
                max_sim = sims.max().item()
                if max_sim >= similarity_threshold:
                    continue 

            kept_embs.append(q_emb)
            unique_questions.append(q)


        #Ranking questions
        unique_questions.sort(key=lambda x: (-len(x.split()), x))

        return unique_questions[:num_questions] if unique_questions else ["Could not generate good questions."]

    except Exception as e:
        return [f"Error generating questions: {e}"]

def _simple_generation_no_semantic(paragraph: str, num_questions: int) -> list:
    #Simple generation if the previous method didn't work
    try:
        task_input = f"generate questions: {paragraph}"
        num_candidates = max(num_questions * 3, 6)
        num_beams = max(num_candidates, 8)

        results = qg_pipeline(
            task_input,
            max_length=64,
            num_beams=num_beams,
            num_return_sequences=num_candidates,
            do_sample=False,
            early_stopping=True
        )

        raw = [r.get("generated_text", "").strip() for r in results]

        #Deduplicate and cleaning questions
        qs, seen = [], set()
        for q in raw:
            if not q:
                continue
            if not q.endswith("?"):
                if any(q.lower().startswith(w) for w in ("who", "what", "when", "where", "why", "how", "which")):
                    q = q + "?"
            if q.endswith("?") and len(q.split()) >= 4:
                key = _normalize(q)
                if key and key not in seen:
                    seen.add(key)
                    qs.append(q)
            if len(qs) >= num_questions:
                break
        return qs if qs else ["Could not generate good questions."]

    except Exception as e:
        return [f"Error generating questions: {e}"]
