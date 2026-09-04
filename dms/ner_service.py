# py dms/ner_service.py
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "benchmark_a" / "best_model"

MAX_LENGTH = 256
STRIDE = 32
BATCH_SIZE = 4

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = None
model = None

def get_ner_model():
    global tokenizer, model

    if tokenizer is None:
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH,
            use_fast=True
        )

    if model is None:
        print("Loading DeBERTa NER model...")

        model = AutoModelForTokenClassification.from_pretrained(
            MODEL_PATH
        )

        model = model.to(dtype=torch.float32)
        model = model.to(device)
        model.eval()

        print("NER model loaded.")
        print("Device:", device)

    return tokenizer, model

def finish_entity(entity, text):
    entity["text"] = text[
        entity["start"]:entity["end"]
    ].strip()

    entity["confidence"] = (
        sum(entity["scores"]) /
        len(entity["scores"])
    )

    del entity["scores"]
    return entity

def merge_bio_entities(predictions, offsets, confidences, text):
    entities = []
    current_entity = None

    for label, offset, confidence in zip(
        predictions,
        offsets,
        confidences
    ):
        start, end = int(offset[0]), int(offset[1])

        if start == 0 and end == 0:
            continue

        if label == "O":
            if current_entity is not None:
                entities.append(
                    finish_entity(
                        current_entity,
                        text
                    )
                )
                current_entity = None
            continue

        if "-" not in label:
            continue

        prefix, entity_type = label.split("-", 1)

        if (
            prefix == "B"
            or current_entity is None
            or current_entity["label"] != entity_type
        ):
            if current_entity is not None:
                entities.append(
                    finish_entity(
                        current_entity,
                        text
                    )
                )

            current_entity = {
                "label": entity_type,
                "start": start,
                "end": end,
                "scores": [float(confidence)]
            }
        else:
            current_entity["end"] = end
            current_entity["scores"].append(
                float(confidence)
            )

    if current_entity is not None:
        entities.append(
            finish_entity(
                current_entity,
                text
            )
        )

    return entities

def remove_duplicate_entities(entities):
    unique = []

    for entity in entities:
        if not entity["text"]:
            continue

        duplicate = False

        for existing in unique:
            same_label = (
                entity["label"] ==
                existing["label"]
            )

            same_text = (
                entity["text"].lower().strip() ==
                existing["text"].lower().strip()
            )

            overlapping = (
                entity["start"] < existing["end"]
                and entity["end"] > existing["start"]
            )

            if same_label and same_text and overlapping:
                duplicate = True

                if entity["confidence"] > existing["confidence"]:
                    existing.update(entity)

                break

        if not duplicate:
            unique.append(entity)

    return sorted(
        unique,
        key=lambda x: x["start"]
    )

def extract_entities(text):
    if not text or not text.strip():
        return []

    tokenizer, model = get_ner_model()

    encoded = tokenizer(
        text,
        truncation=True,
        max_length=MAX_LENGTH,
        stride=STRIDE,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        padding="max_length",
        return_tensors="pt"
    )

    offsets = encoded.pop("offset_mapping")
    encoded.pop("overflow_to_sample_mapping", None)

    all_entities = []
    total_chunks = encoded["input_ids"].shape[0]

    for start_index in range(0, total_chunks, BATCH_SIZE):
        end_index = start_index + BATCH_SIZE

        batch = {
            key: value[start_index:end_index].to(device)
            for key, value in encoded.items()
        }

        with torch.no_grad():
            outputs = model(**batch)

            probabilities = torch.softmax(
                outputs.logits,
                dim=-1
            )

            predicted_ids = torch.argmax(
                probabilities,
                dim=-1
            )

            confidence_scores = torch.max(
                probabilities,
                dim=-1
            ).values

        predicted_ids = predicted_ids.cpu().numpy()
        confidence_scores = confidence_scores.cpu().numpy()

        batch_offsets = offsets[
            start_index:end_index
        ].numpy()

        for i in range(len(predicted_ids)):
            labels = [
                model.config.id2label[int(label_id)]
                for label_id in predicted_ids[i]
            ]

            entities = merge_bio_entities(
                labels,
                batch_offsets[i],
                confidence_scores[i],
                text
            )

            all_entities.extend(entities)

    return remove_duplicate_entities(
        all_entities
    )

def group_entities(entities):
    grouped = {}

    for entity in entities:
        label = entity["label"]
        value = entity["text"]

        if label not in grouped:
            grouped[label] = []

        if value not in grouped[label]:
            grouped[label].append(value)

    return grouped

if __name__ == "__main__":
    print("NER service ready.")
    print("DeBERTa will load only when a resume is processed.")
