# py dms/search_service.py
from sentence_transformers import SentenceTransformer, util
from rapidfuzz.fuzz import ratio
from database import get_connection, search_exact_entity

MIN_SIMILARITY = 0.35
similarity_model = None

def get_similarity_model():
    global similarity_model
    if similarity_model is None:
        print("Loading similarity model...")
        similarity_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Similarity model loaded.")
    return similarity_model

def format_results(rows):
    return [{
        "resume_id": row[0],
        "file_name": row[1],
        "file_path": row[2],
        "text": row[3],
        "entity_type": row[4],
        "entity_text": row[5]
    } for row in rows]

def get_unique_entities(entity_type=None):
    connection = get_connection()
    cursor = connection.cursor()

    if entity_type:
        cursor.execute("""
            SELECT DISTINCT entity_text
            FROM entities
            WHERE entity_type = ?
            ORDER BY entity_text
        """, (entity_type,))
    else:
        cursor.execute("""
            SELECT DISTINCT entity_text
            FROM entities
            ORDER BY entity_text
        """)

    entities = [row[0] for row in cursor.fetchall() if row[0].strip()]
    connection.close()
    return entities

def get_documents_by_entity(entity_text, entity_type=None):
    connection = get_connection()
    cursor = connection.cursor()

    if entity_type:
        cursor.execute("""
            SELECT DISTINCT
                r.resume_id,
                r.file_name,
                r.file_path,
                r.extracted_text,
                e.entity_type,
                e.entity_text
            FROM resumes r
            JOIN entities e ON r.resume_id = e.resume_id
            WHERE LOWER(e.entity_text) = LOWER(?)
            AND e.entity_type = ?
        """, (entity_text, entity_type))
    else:
        cursor.execute("""
            SELECT DISTINCT
                r.resume_id,
                r.file_name,
                r.file_path,
                r.extracted_text,
                e.entity_type,
                e.entity_text
            FROM resumes r
            JOIN entities e ON r.resume_id = e.resume_id
            WHERE LOWER(e.entity_text) = LOWER(?)
        """, (entity_text,))

    rows = cursor.fetchall()
    connection.close()
    return format_results(rows)

def find_similar_entities(query, entity_type=None, top_k=3):
    candidates = get_unique_entities(entity_type)

    if not candidates:
        return []

    model = get_similarity_model()

    query_embedding = model.encode(
        query,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    candidate_embeddings = model.encode(
        candidates,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    semantic_scores = util.cos_sim(
        query_embedding,
        candidate_embeddings
    )[0]

    scored = []

    for i, candidate in enumerate(candidates):
        semantic_score = float(semantic_scores[i])

        fuzzy_score = ratio(
            query.lower(),
            candidate.lower()
        ) / 100

        combined_score = (
            semantic_score * 0.8 +
            fuzzy_score * 0.2
        )

        scored.append({
            "entity": candidate,
            "score": combined_score
        })

    scored.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return scored[:top_k]


def search_entity(query, entity_type=None):
    exact_rows = search_exact_entity(
        query,
        entity_type
    )

    if exact_rows:
        results = format_results(exact_rows)

        return {
            "status": "exact",
            "query": query,
            "matched_entity": results[0]["entity_text"],
            "results": results
        }

    similar_entities = find_similar_entities(
        query,
        entity_type
    )

    if not similar_entities:
        return {
            "status": "not_found",
            "query": query,
            "results": []
        }

    all_results = []

    for suggestion in similar_entities:
        documents = get_documents_by_entity(
            suggestion["entity"],
            entity_type
        )

        for document in documents:
            document["similar_entity"] = suggestion["entity"]
            document["similarity_score"] = suggestion["score"]
            all_results.append(document)

    return {
        "status": "similar",
        "query": query,
        "matched_entity": similar_entities[0]["entity"],
        "similarity_score": similar_entities[0]["score"],
        "suggestions": similar_entities,
        "results": all_results
    }

    return {
        "status": "similar",
        "query": query,
        "matched_entity": best["entity"],
        "similarity_score": best["score"],
        "suggestions": similar_entities,
        "results": results
    }

if __name__ == "__main__":
    print("Search service ready.")
    print("Similarity model loads only when similar search is required.")
